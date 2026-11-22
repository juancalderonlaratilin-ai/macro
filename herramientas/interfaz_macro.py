#!/usr/bin/env python3
"""Interfaz de mediciones para MACRO (PIC16F18446, envío en texto ASCII).

Adaptada de la interfaz de Micro 3 según la sección 12 de MACRO_especificacion_diseno.md:
  * Referencia del ADC = FVR 2,048 V. El valor real se toma del mensaje "S:MACRO,FVR=<mV>".
  * 500 pares/s sin decimación (cada línea es un par completo del ADC).
  * Las líneas "S:...", "OK:...", "E:..." y "P:..." son mensajes del PIC: se muestran y
    NO cuentan como líneas malas.
  * Se pueden enviar comandos al PIC (Z, R, A:1, P:I,512, P?, y los de firmware_prueba).

Recibe por la UART las líneas "2048,2051\r\n" (I,Q) que manda el PIC (500 por segundo),
muestra I y Q en vivo y calcula las mediciones del ADC:

  * Senoidal: SINAD, ENOB, SNR, THD, SFDR, frecuencia y amplitud (método de
    docs/especificacion_adc.md §6: ventana de Kaiser β = 14, fundamental ±6 bins; además
    se excluye el lóbulo de la continua, bins 0 a 6, que el script original contaba como ruido).
  * Continua: media, ruido rms (σ), pico a pico, códigos distintos, histograma,
    resolución efectiva y libre de ruido (docs/especificacion_adc.md §8).
  * Periodo: si el firmware manda en Q el periodo medido con Timer1 (MODO_PERIODO,
    cuentas de 62,5 ns), histograma del periodo y su desviación estándar.

Además (21/11/2026):
  * Pestaña «Resultados» a pantalla completa (antes quedaba bajo el borde en laptops) y
    columna de controles con barra de desplazamiento.
  * «Plano I-Q en vivo»: estela de los últimos segundos que se desvanece, cero relativo
    (ΔI, ΔQ en mV), limpiar y pausa.
  * «SINAD en MATLAB»: guarda la captura y llama a MATLAB (sinad, snr, thd, sfdr de Signal
    Processing Toolbox) con macro_sinad.m; muestra sus números junto a los de Python y la figura.

Requiere:  pip install pyserial numpy matplotlib
Uso:       python interfaz_macro.py
"""
import collections
import csv
import glob
import math
import os
import queue
import re
import shutil
import subprocess
import sys
import threading
import time
try:
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox
except ImportError:
    print("\nFalta tkinter (la parte de ventanas de Python). Reinstala Python desde python.org\n"
          "y deja marcada la opción «tcl/tk and IDLE».\n")
    input("Presiona Enter para cerrar...")
    sys.exit(1)


def _falta(texto):
    """Muestra qué falta instalar y deja la ventana abierta (si no, se cierra sola)."""
    print("\n" + texto + "\n")
    try:
        r = tk.Tk()
        r.withdraw()
        messagebox.showerror("Falta algo para abrir la interfaz", texto)
        r.destroy()
    except Exception:
        pass
    try:
        input("Presiona Enter para cerrar...")
    except Exception:
        pass
    sys.exit(1)


try:
    import numpy as np
    import matplotlib
    matplotlib.use("TkAgg")
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
    import serial  # noqa: F401  (pyserial)
except ImportError as e:
    _falta(f"Falta un paquete de Python: {e.name}\n\n"
           "Abre cmd y escribe:\n    pip install pyserial numpy matplotlib\n"
           "(o:  py -m pip install pyserial numpy matplotlib)")

FS_ADC = 500.0               # cada canal se muestrea a 500 Hz (Timer4 a 1 ms, alternando I y Q)
FS = 500.0                   # líneas por segundo que manda el PIC (todos los pares)
BAUD = 115200
N_BITS = 12
VREF_NOMINAL = 2.048         # FVR x2; el valor real llega en "S:MACRO,FVR=<mV>"
VREF = VREF_NOMINAL
LSB = VREF / 2 ** N_BITS     # 0,500 mV
V_FS_RMS = VREF / 2 / math.sqrt(2)   # senoidal a escala completa: 0,724 V rms


def fijar_vref(voltios):
    """Cambia la escala de voltios de toda la interfaz (la usa el mensaje S:MACRO,FVR=...)."""
    global VREF, LSB, V_FS_RMS
    VREF = float(voltios)
    LSB = VREF / 2 ** N_BITS
    V_FS_RMS = VREF / 2 / math.sqrt(2)

T_TIMER1_NS = 62.5           # cuenta de Timer1 a 16 MHz (modo periodo)
SINAD_MIN = 60.0             # requisito


# ============================================================ mediciones (sin interfaz)

def analizar_senoidal(codigos, fs=FS, f_in=None, ancho=6, n_armonicos=5):
    """SINAD y compañía de una captura de una senoidal. Devuelve un dict."""
    x = np.asarray(codigos, dtype=float)
    m = len(x)
    w = np.kaiser(m, 14)
    dc = float((x * w).sum() / w.sum())          # continua ponderada por la ventana
    v = (x - dc) * LSB
    espectro = np.abs(np.fft.rfft(v * w)) ** 2
    s2 = (w ** 2).sum()
    a_vrms2 = lambda p: 2.0 * p / (m * s2)          # potencia de bins -> V rms²

    if f_in:
        k0 = int(round(f_in * m / fs))
    else:
        k0 = int(np.argmax(espectro[ancho + 1:])) + ancho + 1
    lo, hi = max(k0 - ancho, 1), min(k0 + ancho + 1, len(espectro))
    p_sig = espectro[lo:hi].sum()
    # ruido + distorsión: todo menos la fundamental y el lóbulo de la continua (bins 0..ancho).
    # (El script de especificacion_adc.md §6 resta desde el bin 1; con la ventana de Kaiser la
    # continua residual ocupa hasta ~5 bins y bajaba el SINAD, sobre todo a 5 Hz.)
    mascara = np.ones(len(espectro), dtype=bool)
    mascara[:ancho + 1] = False                  # lóbulo de la continua
    mascara[lo:hi] = False                       # fundamental
    p_nd = max(float(espectro[mascara].sum()), 1e-30)
    ks = np.arange(lo, hi)
    k_fino = float((espectro[lo:hi] * ks).sum() / espectro[lo:hi].sum())

    # armónicos (con plegado por encima de fs/2)
    armonicos = []
    p_arm = 0.0
    for h in range(2, n_armonicos + 1):
        kh = (h * k_fino) % m
        if kh > m / 2:
            kh = m - kh
        kh = int(round(kh))
        if kh <= ancho or abs(kh - k0) <= 2 * ancho:
            continue
        a, b = max(kh - ancho, 1), min(kh + ancho + 1, len(espectro))
        p = espectro[a:b].sum()
        armonicos.append((h, kh, p))
        p_arm += p
    p_ruido = max(p_nd - p_arm, 1e-30)

    # mayor espurio (pico de un bin) fuera de la fundamental y de la continua
    resto = espectro.copy()
    resto[:ancho + 1] = 0
    resto[lo:hi] = 0
    k_esp = int(np.argmax(resto))

    sinad = 10 * math.log10(p_sig / p_nd)
    v_sig = math.sqrt(a_vrms2(p_sig))
    r = {
        "muestras": m,
        "frecuencia_Hz": k_fino * fs / m,
        "ciclos": k_fino,
        "dc_codigo": dc,
        "dc_V": dc * LSB,
        "amplitud_pico_V": v_sig * math.sqrt(2),
        "amplitud_rms_V": v_sig,
        "ruido_dist_rms_mV": math.sqrt(a_vrms2(p_nd)) * 1e3,
        "ruido_dist_rms_LSB": math.sqrt(a_vrms2(p_nd)) / LSB,
        "sinad_dB": sinad,
        "enob_bits": (sinad - 1.76) / 6.02,
        "snr_dB": 10 * math.log10(p_sig / p_ruido),
        "thd_dB": 10 * math.log10(p_arm / p_sig) if p_arm > 0 else float("-inf"),
        "sfdr_dB": 10 * math.log10(espectro[lo:hi].max() / max(resto[k_esp], 1e-30)),
        "sinad_fs_dB": sinad + 20 * math.log10(V_FS_RMS / v_sig) if v_sig > 0 else float("nan"),
        "minimo": int(x.min()),
        "maximo": int(x.max()),
        "recorte": bool(x.min() <= 0 or x.max() >= 2 ** N_BITS - 1),
        "pocos_ciclos": k0 < 2 * ancho + 2,
        # para graficar
        "_espectro": espectro,
        "_p_fs": V_FS_RMS ** 2 * m * s2 / 2.0,
        "_k0": k0,
        "_banda": (lo, hi),
        "_armonicos": armonicos,
        "_k_esp": k_esp,
    }
    r["enob_fs_bits"] = (r["sinad_fs_dB"] - 1.76) / 6.02
    return r


def analizar_continua(codigos):
    """Ruido con entrada fija (histograma de códigos)."""
    x = np.asarray(codigos, dtype=float)
    sigma = x.std(ddof=1) if len(x) > 1 else 0.0
    valores = np.unique(x)
    return {
        "muestras": len(x),
        "media_codigo": x.mean(),
        "media_V": x.mean() * LSB,
        "sigma_LSB": sigma,
        "sigma_uV": sigma * LSB * 1e6,
        "pp_codigos": int(x.max() - x.min()),
        "pp_estimado_uV": 6.6 * sigma * LSB * 1e6,
        "codigos_distintos": len(valores),
        "resol_efectiva_bits": math.log2(2 ** N_BITS / sigma) if sigma > 0 else float("inf"),
        "resol_libre_ruido_bits": math.log2(2 ** N_BITS / (6.6 * sigma)) if sigma > 0 else float("inf"),
        "incertidumbre_sigma_pct": 100 / math.sqrt(2 * (len(x) - 1)) if len(x) > 1 else float("nan"),
    }


def analizar_periodo(cuentas):
    """Periodo entre muestras medido por el PIC con Timer1 (cuentas de 62,5 ns)."""
    t = np.asarray(cuentas, dtype=float) * T_TIMER1_NS
    return {
        "muestras": len(t),
        "media_ns": t.mean(),
        "sigma_ns": t.std(ddof=1) if len(t) > 1 else 0.0,
        "min_ns": t.min(),
        "max_ns": t.max(),
        "frecuencia_Hz": 1e9 / t.mean() if t.mean() > 0 else float("nan"),
    }


# ============================================================ decodificador de líneas ASCII

LINEA_DATOS = re.compile(rb"(\d{1,5}),(\d{1,5})")           # "I,Q" (la línea entera)
LINEA_MENSAJE = re.compile(rb"(S|OK|E|P):[ -~]*")             # mensajes del PIC (sec. 7.4)
LINEA_FVR = re.compile(rb"S:MACRO,FVR=(\d{3,4})")
LINEA_VDD = re.compile(rb"S:MACRO,VDD=(\d{4})")              # firmware_prueba4: el ADC usa VDD


class DecoAscii:
    """Junta los bytes que llegan y separa las líneas completas en tres clases:
      * datos "2048,2051" -> códigos de I y Q (0 a 4095);
      * mensajes del PIC ("S:...", "OK:...", "E:...", "P:...") -> se guardan en mensajes;
      * cualquier otra cosa (línea cortada o con ruido) -> se cuenta en lineas_malas."""

    def __init__(self):
        self.texto = bytearray()
        self.i, self.q = [], []
        self.lineas_malas = 0       # líneas que no son ni datos ni mensajes
        self.n_mensajes = 0
        self.mensajes = collections.deque(maxlen=200)   # (hora, texto)
        self.estado_pic = "?"       # último S: de estado (REPOSO, CAL, MEDIR, ALARMA...)
        self.fvr_mV = None          # de S:MACRO,FVR=<mV>
        self.vdd_mV = None          # de S:MACRO,VDD=<mV> (firmware_prueba4)
        self.ref_auto = True        # False si se eligió la referencia a mano en la interfaz
        self.t_primera = None       # hora de la primera muestra (para medir muestras/s)

    def alimentar(self, datos):
        """Agrega bytes y devuelve la lista de (i, q) nuevos."""
        self.texto += datos
        nuevos = []
        fin = self.texto.rfind(b"\n")
        if fin < 0:
            if len(self.texto) > 4096:        # mucho sin un salto de línea: es basura
                self.lineas_malas += 1
                self.texto.clear()
            return nuevos
        bloque = bytes(self.texto[:fin + 1])
        del self.texto[:fin + 1]
        for linea in bloque.split(b"\n")[:-1]:
            linea = linea.rstrip(b"\r")
            m = LINEA_DATOS.fullmatch(linea)
            if m:
                i, q = int(m.group(1)), int(m.group(2))
                self.i.append(i)
                self.q.append(q)
                nuevos.append((i, q))
            elif LINEA_MENSAJE.fullmatch(linea):
                self._mensaje(linea)
            elif linea:
                self.lineas_malas += 1
        if nuevos and self.t_primera is None:
            self.t_primera = time.perf_counter()
        return nuevos

    def _mensaje(self, linea):
        txt = linea.decode("ascii")
        self.n_mensajes += 1
        self.mensajes.append((time.strftime("%H:%M:%S"), txt))
        m = LINEA_FVR.fullmatch(linea)
        mv_vdd = LINEA_VDD.fullmatch(linea)
        if m:
            mv = int(m.group(1))
            if 1900 <= mv <= 2200:            # FVR x2 con su tolerancia de +-4 %
                self.fvr_mV, self.vdd_mV = mv, None
                if self.ref_auto:
                    fijar_vref(mv / 1000.0)
        elif mv_vdd:
            mv = int(mv_vdd.group(1))
            if 3000 <= mv <= 4300:
                self.vdd_mV, self.fvr_mV = mv, None
                if self.ref_auto:
                    fijar_vref(mv / 1000.0)
        elif txt.startswith("S:") and not txt.startswith(("S:CNT", "S:RAFAGA", "S:FIN", "S:DIAG", "S:MACRO",
                                                          "S:CONSIGNA", "S:AZ", "S:RETIENE")):
            campos = txt[2:].split(",")
            self.estado_pic = txt[2:] if campos[0] in ("ALARMA", "FALLO") else campos[0]


def fs_desde_tasa(tasa):
    """MACRO manda todos los pares: 500 líneas/s. Se redondea la tasa medida a 500/k por si
    algún día se manda 1 de cada k pares."""
    if tasa <= 0:
        return FS
    k = FS_ADC / tasa
    for redondo in (1, 2, 3, 4, 5, 10, 20, 25, 50, 100, 200, 250):
        if abs(k - redondo) <= 0.04 * redondo:   # a tasas bajas la medida varía unos %
            return FS_ADC / redondo
    return FS_ADC / max(1, round(k))


# ============================================================ simulador (prueba sin PIC)

class Simulador:
    """Imita al PIC: manda una línea "I,Q\r\n" por par (500 líneas/s) y los mensajes de arranque.
    modo "senoidal": I y Q senoidales de 0,95 V de amplitud centradas en 1,024 V, ruido de
    0,5 LSB rms y un 3.er armónico de −75 dBc.  modo "continua": 1,024 V con ruido."""

    def __init__(self, modo="senoidal", f=20.0, amp_V=0.95, ruido_LSB=0.5, cada=1):
        self.modo, self.f, self.amp, self.ruido = modo, f, amp_V / LSB, ruido_LSB
        self.cada = cada
        self.salida = bytearray(b"S:MACRO,FVR=2048\r\nS:REPOSO\r\n")
        self.n = 0
        self.t0 = time.perf_counter()
        self.lock = threading.Lock()
        self.rng = np.random.default_rng(1)

    def write(self, datos):
        return len(datos)            # el simulador no atiende comandos

    def _muestra(self, t, fase):
        if self.modo == "continua":
            v = 2048.0
        else:
            a = 2 * math.pi * self.f * t + fase
            v = 2048 + self.amp * math.sin(a) + self.amp * 10 ** (-75 / 20) * math.sin(3 * a)
        v += self.rng.normal(0, self.ruido)
        return int(min(max(round(v), 0), 4095))

    def _generar(self):
        objetivo = int((time.perf_counter() - self.t0) * FS_ADC)
        while self.n < objetivo:
            if self.n % self.cada == 0:
                t = self.n / FS_ADC
                i, q = self._muestra(t, 0.0), self._muestra(t, math.pi / 2)
                self.salida += f"{i},{q}\r\n".encode()
            self.n += 1

    @property
    def in_waiting(self):
        with self.lock:
            self._generar()
            return len(self.salida)

    def read(self, n=1):
        time.sleep(0.005)
        with self.lock:
            self._generar()
            d = bytes(self.salida[:n])
            del self.salida[:n]
            return d

    def reset_input_buffer(self):
        with self.lock:
            self.salida.clear()

    def close(self):
        pass



# ============================================================ SINAD con MATLAB

# Se escribe como macro_sinad.m en la carpeta de capturas cada vez que se usa, para que la
# versión que corre MATLAB sea siempre la de esta interfaz. Solo funciones de MATLAB y de
# Signal Processing Toolbox: sinad, snr, thd y sfdr.
MATLAB_SINAD_M = r"""function r = macro_sinad(archivo, fs, vref, canal)
%MACRO_SINAD  SINAD, ENOB, SNR, THD y SFDR de una captura de MACRO con las
%funciones de Signal Processing Toolbox (sinad, snr, thd, sfdr).
%
%   r = macro_sinad('captura_I.csv', 500, 2.048, 'I')
%
%   archivo : CSV con una columna de codigos del ADC (0 a 4095)
%   fs      : muestras por segundo de ese canal (500 en MACRO)
%   vref    : referencia del ADC en voltios (FVR real; 2.048 nominal)
%   canal   : 'I' o 'Q' (solo para el titulo)
%
%   ENOB = (SINAD - 1.76) / 6.02.  Guarda el espectro que dibuja sinad() en
%   <archivo>_sinad.png y los numeros en <archivo>_resultado.txt.
%   Lo genera interfaz_macro.py; se puede correr a mano.

if nargin < 2 || isempty(fs),   fs = 500;     end
if nargin < 3 || isempty(vref), vref = 2.048; end
if nargin < 4,                  canal = '';    end
if isempty(which('sinad'))
    error('macro:toolbox', 'Falta Signal Processing Toolbox (funcion sinad).');
end

datos = readmatrix(archivo);
codigos = datos(:, 1);
codigos = codigos(~isnan(codigos));
x = codigos * vref / 4096;              % voltios
x = x - mean(x);

r.muestras  = numel(x);
r.sinad_dB  = sinad(x, fs);
r.enob_bits = (r.sinad_dB - 1.76) / 6.02;
r.snr_dB    = snr(x, fs);
[r.thd_dB, ~, frec_arm] = thd(x, fs);
r.sfdr_dB   = sfdr(x, fs);
r.frecuencia_Hz = frec_arm(1);
r.amplitud_pico_V = sqrt(2) * sqrt(mean(x .^ 2));   % aproximada: incluye el ruido
r.matlab    = version;

[carpeta, nombre] = fileparts(archivo);
if isempty(carpeta), carpeta = pwd; end
r.figura = fullfile(carpeta, [nombre '_sinad.png']);
f = figure('Visible', 'off', 'Position', [100 100 900 520]);
sinad(x, fs);
title(sprintf('MACRO canal %s: SINAD = %.2f dB, ENOB = %.2f bits (MATLAB R%s)', ...
      canal, r.sinad_dB, r.enob_bits, version('-release')));
exportgraphics(f, r.figura, 'Resolution', 120);
close(f);

lineas = {sprintf('MACRO_MATLAB=%s', r.matlab), ...
          sprintf('MACRO_MUESTRAS=%d', r.muestras), ...
          sprintf('MACRO_SINAD_dB=%.4f', r.sinad_dB), ...
          sprintf('MACRO_ENOB_bits=%.4f', r.enob_bits), ...
          sprintf('MACRO_SNR_dB=%.4f', r.snr_dB), ...
          sprintf('MACRO_THD_dB=%.4f', r.thd_dB), ...
          sprintf('MACRO_SFDR_dB=%.4f', r.sfdr_dB), ...
          sprintf('MACRO_FRECUENCIA_Hz=%.5f', r.frecuencia_Hz), ...
          sprintf('MACRO_AMPLITUD_V=%.5f', r.amplitud_pico_V), ...
          ['MACRO_FIGURA=' r.figura]};
fid = fopen(fullfile(carpeta, [nombre '_resultado.txt']), 'w');
for k = 1:numel(lineas)
    fprintf('%s\n', lineas{k});          % consola (la lee interfaz_macro.py)
    fprintf(fid, '%s\n', lineas{k});     % y archivo, por si la consola no llega
end
fclose(fid);
end
"""

CARPETA_CAPTURAS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "capturas_matlab")
T_LIMITE_MATLAB_S = 300           # MATLAB tarda ~20-60 s en arrancar con -batch


def buscar_matlab():
    """Ruta de matlab.exe: primero el PATH, después la versión más nueva en Program Files."""
    ruta = shutil.which("matlab")
    if ruta:
        return ruta
    for base in (r"C:\Program Files\MATLAB", r"C:\Program Files (x86)\MATLAB"):
        candidatos = sorted(glob.glob(os.path.join(base, "R*", "bin", "matlab.exe")), reverse=True)
        if candidatos:
            return candidatos[0]
    return None


def texto_matlab(s):
    """Cadena entre comillas simples de MATLAB."""
    return "'" + str(s).replace("'", "''") + "'"


# ============================================================ interfaz

PUERTO_SIM_SEN = "SIMULADOR (senoidal 20 Hz)"
PUERTO_SIM_DC = "SIMULADOR (continua 1,024 V)"
ESTELAS_S = {"0,5 s": 0.5, "1 s": 1.0, "2 s": 2.0, "5 s": 5.0, "10 s": 10.0, "30 s": 30.0}
REFERENCIAS = ["Automática (mensaje S:MACRO)", "FVR 2048 mV", "VDD 3700 mV"]
AMPLITUD_MIN_SINAD = 0.05        # bajo 5 % de la escala (~51 mV pico) no hay senoidal de prueba
PUNTOS_MAX_PLANO = 3000           # se dibuja como mucho esto (se toma 1 de cada k)
COLOR_PLANO = (0.12, 0.31, 0.47)  # #1f4e79


class MarcoDesplazable(ttk.Frame):
    """Columna con barra de desplazamiento vertical: si la pantalla es baja, se baja con la
    rueda del ratón en vez de quedar cortada."""

    def __init__(self, padre):
        super().__init__(padre)
        self.lienzo = tk.Canvas(self, highlightthickness=0, borderwidth=0)
        barra = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.lienzo.yview)
        self.interior = ttk.Frame(self.lienzo, padding=8)
        self.lienzo.create_window((0, 0), window=self.interior, anchor="nw")
        self.lienzo.configure(yscrollcommand=barra.set)
        barra.pack(side=tk.RIGHT, fill=tk.Y)
        self.lienzo.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.interior.bind("<Configure>", self._ajustar)
        self.interior.bind("<Enter>", lambda _e: self.lienzo.bind_all("<MouseWheel>", self._rueda))
        self.interior.bind("<Leave>", lambda _e: self.lienzo.unbind_all("<MouseWheel>"))

    def _ajustar(self, _e=None):
        self.lienzo.configure(scrollregion=self.lienzo.bbox("all"), width=self.interior.winfo_reqwidth())

    def _rueda(self, e):
        if self.interior.winfo_reqheight() > self.lienzo.winfo_height():
            self.lienzo.yview_scroll(int(-e.delta / 120) or (-1 if e.delta > 0 else 1), "units")


class App:
    def __init__(self, raiz):
        self.raiz = raiz
        raiz.title("MACRO — Receptor y mediciones del ADC (líneas ASCII I,Q)")
        raiz.geometry("1350x760")
        raiz.minsize(900, 500)
        try:
            raiz.state("zoomed")                 # Windows: ventana maximizada
        except tk.TclError:
            pass
        self.deco = None
        self.puerto = None
        self.hilo = None
        self.parar = threading.Event()
        self.t_inicio = None
        self.fs = FS
        self.ultimo = None          # último resultado de análisis
        self.ultimo_tipo = None
        # plano I-Q en vivo
        self.plano_desde = 0        # índice desde el que se dibuja (lo mueve «Limpiar»)
        self.cero = None            # (I0, Q0) en códigos para ΔI, ΔQ
        self.plano_pausa = False
        # MATLAB
        self.cola_matlab = queue.Queue()
        self.matlab_ocupado = False

        self._armar_controles()
        self._armar_pestanas()
        self.raiz.protocol("WM_DELETE_WINDOW", self.cerrar)
        self._refrescar_puertos()
        self._tick_auto = 0
        self.raiz.after(200, self._actualizar)

    # ---------------------------------------------------------------- panel izquierdo
    def _armar_controles(self):
        marco = MarcoDesplazable(self.raiz)
        marco.pack(side=tk.LEFT, fill=tk.Y)
        izq = marco.interior

        f = ttk.LabelFrame(izq, text="1. Conexión", padding=8)
        f.pack(fill=tk.X, pady=4)
        ttk.Label(f, text="Puerto:").grid(row=0, column=0, sticky="w")
        self.cb_puerto = ttk.Combobox(f, width=28, state="readonly")
        self.cb_puerto.grid(row=0, column=1, columnspan=2, sticky="we", pady=2)
        ttk.Button(f, text="Refrescar", command=self._refrescar_puertos).grid(row=1, column=1, sticky="we")
        self.bt_conectar = ttk.Button(f, text="Conectar", command=self._conectar)
        self.bt_conectar.grid(row=1, column=2, sticky="we")
        ttk.Label(f, text="Comando:").grid(row=2, column=0, sticky="w", pady=(4, 0))
        self.en_cmd = ttk.Entry(f, width=14)
        self.en_cmd.grid(row=2, column=1, sticky="we", pady=(4, 0))
        self.en_cmd.bind("<Return>", lambda _e: self._enviar_comando())
        ttk.Button(f, text="Enviar", command=self._enviar_comando).grid(row=2, column=2, sticky="we", pady=(4, 0))
        ttk.Label(f, text="Ref. ADC:").grid(row=3, column=0, sticky="w", pady=(4, 0))
        self.cb_ref = ttk.Combobox(f, width=28, values=REFERENCIAS)
        self.cb_ref.set(REFERENCIAS[0])
        self.cb_ref.grid(row=3, column=1, columnspan=2, sticky="we", pady=(4, 0))
        self.cb_ref.bind("<<ComboboxSelected>>", lambda _e: self._cambio_referencia())
        self.cb_ref.bind("<Return>", lambda _e: self._cambio_referencia())

        f = ttk.LabelFrame(izq, text="2. Estado del enlace", padding=8)
        f.pack(fill=tk.X, pady=4)
        self.var_estado = tk.StringVar(value="Desconectado")
        ttk.Label(f, textvariable=self.var_estado, width=46, justify=tk.LEFT,
                  font=("Consolas", 9)).pack(anchor="w")

        f = ttk.LabelFrame(izq, text="3. Medición", padding=8)
        f.pack(fill=tk.X, pady=4)
        ttk.Label(f, text="Canal:").grid(row=0, column=0, sticky="w")
        self.var_canal = tk.StringVar(value="I")
        ttk.Radiobutton(f, text="I (RC0)", variable=self.var_canal, value="I").grid(row=0, column=1, sticky="w")
        ttk.Radiobutton(f, text="Q (RC1)", variable=self.var_canal, value="Q").grid(row=0, column=2, sticky="w")
        ttk.Label(f, text="Tipo:").grid(row=1, column=0, sticky="nw")
        self.var_tipo = tk.StringVar(value="senoidal")
        for k, (val, txt) in enumerate([("senoidal", "Senoidal → SINAD, ENOB, THD"),
                                        ("continua", "Continua → ruido e histograma"),
                                        ("periodo", "Periodo (MODO_PERIODO en Q)")]):
            ttk.Radiobutton(f, text=txt, variable=self.var_tipo, value=val).grid(
                row=1 + k, column=1, columnspan=2, sticky="w")

        ttk.Label(f, text="Muestras:").grid(row=4, column=0, sticky="w", pady=(6, 0))
        self.cb_n = ttk.Combobox(f, width=8, state="readonly",
                                 values=["1024", "2048", "4096", "8192", "10000", "16384"])
        self.cb_n.set("4096")
        self.cb_n.grid(row=4, column=1, sticky="w", pady=(6, 0))

        ttk.Label(f, text="f entrada (Hz):").grid(row=5, column=0, sticky="w", pady=(4, 0))
        self.en_f = ttk.Entry(f, width=8)
        self.en_f.grid(row=5, column=1, sticky="w", pady=(4, 0))
        ttk.Label(f, text="(vacío = automática)").grid(row=5, column=2, sticky="w", pady=(4, 0))

        self.var_auto = tk.BooleanVar(value=False)
        ttk.Checkbutton(f, text="Analizar cada 1 s", variable=self.var_auto).grid(
            row=6, column=0, columnspan=2, sticky="w", pady=(6, 0))
        ttk.Button(f, text="Analizar ahora", command=self.analizar).grid(
            row=6, column=2, sticky="we", pady=(6, 0), padx=(4, 0))
        self.bt_matlab = ttk.Button(f, text="SINAD en MATLAB", command=self.sinad_matlab)
        self.bt_matlab.grid(row=7, column=2, sticky="we", pady=(4, 0), padx=(4, 0))
        ttk.Label(f, text="(usa sinad() de MATLAB)").grid(row=7, column=0, columnspan=2, sticky="w", pady=(4, 0))
        self.var_resumen = tk.StringVar(value="")
        ttk.Label(f, textvariable=self.var_resumen, font=("Consolas", 10, "bold"), wraplength="3.2i",
                  foreground="#1f4e79", justify=tk.LEFT).grid(row=8, column=0, columnspan=3, sticky="w", pady=(6, 0))

        f = ttk.LabelFrame(izq, text="4. Guardar", padding=8)
        f.pack(fill=tk.X, pady=4)
        f_botones = ttk.Frame(f)
        f_botones.pack(fill=tk.X)
        ttk.Button(f_botones, text="CSV", command=self.guardar_csv).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        ttk.Button(f_botones, text="Reporte", command=self.guardar_reporte).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        ttk.Button(f_botones, text="Borrar", command=self.borrar).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

    # ---------------------------------------------------------------- pestañas de la derecha
    def _armar_pestanas(self):
        self.nb = ttk.Notebook(self.raiz)
        self.nb.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=4, pady=4)

        # Resultados: ocupa toda la pestaña, con desplazamiento
        self.tab_resultados = ttk.Frame(self.nb, padding=6)
        self.nb.add(self.tab_resultados, text="Resultados")
        barra = ttk.Scrollbar(self.tab_resultados, orient=tk.VERTICAL)
        self.txt = tk.Text(self.tab_resultados, font=("Consolas", 11), relief=tk.FLAT, wrap=tk.WORD,
                           background="white", padx=10, pady=8, yscrollcommand=barra.set)
        barra.config(command=self.txt.yview)
        barra.pack(side=tk.RIGHT, fill=tk.Y)
        self.txt.pack(fill=tk.BOTH, expand=True)
        self.txt.tag_configure("ok", foreground="#1a7f37", font=("Consolas", 12, "bold"))
        self.txt.tag_configure("mal", foreground="#c62828", font=("Consolas", 12, "bold"))
        self.txt.tag_configure("titulo", font=("Consolas", 12, "bold"))
        self._escribir([("Conéctate y presiona «Analizar ahora».\n", None)])

        self.figs = {}
        self.tabs = {}
        for nombre in ["Señal en vivo", "Plano I-Q en vivo", "Espectro", "Histograma", "MATLAB"]:
            marco = ttk.Frame(self.nb)
            self.nb.add(marco, text=nombre)
            self.tabs[nombre] = marco
            if nombre == "Plano I-Q en vivo":
                self._armar_barra_plano(marco)
            fig = Figure(figsize=(8, 6), dpi=100)
            ax = fig.add_subplot(111)
            lienzo = FigureCanvasTkAgg(fig, master=marco)
            NavigationToolbar2Tk(lienzo, marco).update()
            lienzo.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            self.figs[nombre] = (fig, ax, lienzo)

        fig, ax, _ = self.figs["Señal en vivo"]
        self.linea_i, = ax.plot([], [], label="I", lw=0.9)
        self.linea_q, = ax.plot([], [], label="Q", lw=0.9)
        ax.set_xlabel("tiempo (s)")
        ax.set_ylabel("voltios")
        ax.set_ylim(0, VREF)
        ax.grid(True)
        ax.legend(loc="upper right")
        ax.set_title("Últimos 2 s (500 muestras/s)")

        fig, ax, lienzo = self.figs["Plano I-Q en vivo"]
        self.sc_plano = ax.scatter([], [], s=7, linewidths=0)
        self.pt_plano, = ax.plot([], [], "o", ms=8, mfc="#c62828", mec="white", mew=1.2, zorder=5)
        self.txt_plano = ax.text(0.01, 0.99, "", transform=ax.transAxes, va="top", ha="left",
                                 family="monospace", fontsize=9,
                                 bbox=dict(boxstyle="round", fc="white", ec="#bbbbbb", alpha=0.85))
        ax.set_aspect("equal", adjustable="box")
        ax.grid(True)

        for nombre in ["Espectro", "Histograma"]:
            fig, ax, lienzo = self.figs[nombre]
            ax.text(0.5, 0.5, "Presiona «Analizar ahora»", ha="center", va="center", transform=ax.transAxes)
            lienzo.draw()
        fig, ax, lienzo = self.figs["MATLAB"]
        ax.axis("off")
        ax.text(0.5, 0.5, "Presiona «SINAD en MATLAB»", ha="center", va="center", transform=ax.transAxes)
        lienzo.draw()

    def _armar_barra_plano(self, marco):
        b = ttk.Frame(marco, padding=(4, 4, 4, 0))
        b.pack(fill=tk.X)
        f1 = ttk.Frame(b)
        f1.pack(fill=tk.X)
        f2 = ttk.Frame(b)
        f2.pack(fill=tk.X, pady=(2, 0))
        ttk.Label(f1, text="Estela:").pack(side=tk.LEFT)
        self.cb_estela = ttk.Combobox(f1, width=6, state="readonly", values=list(ESTELAS_S))
        self.cb_estela.set("2 s")
        self.cb_estela.pack(side=tk.LEFT, padx=(2, 8))
        self.var_desvanecer = tk.BooleanVar(value=True)
        ttk.Checkbutton(f1, text="Desvanecer", variable=self.var_desvanecer).pack(side=tk.LEFT, padx=4)
        self.var_zoom = tk.BooleanVar(value=True)
        ttk.Checkbutton(f1, text="Zoom automático", variable=self.var_zoom).pack(side=tk.LEFT, padx=4)
        self.var_delta = tk.BooleanVar(value=False)
        ttk.Checkbutton(f2, text="ΔI, ΔQ (mV)", variable=self.var_delta,
                        command=self._cambio_delta).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(f2, text="Fijar cero", command=self._fijar_cero).pack(side=tk.LEFT, padx=4)
        ttk.Button(f2, text="Limpiar", command=self._limpiar_plano).pack(side=tk.LEFT, padx=4)
        self.bt_pausa = ttk.Button(f2, text="Pausa", command=self._pausa_plano)
        self.bt_pausa.pack(side=tk.LEFT, padx=4)

    def _cambio_referencia(self):
        """Automática: la fija el mensaje S:MACRO del PIC al arrancar. A mano: «FVR 2048 mV» o
        «VDD 3700 mV» (se puede escribir otro valor, p. ej. «VDD 3667 mV»)."""
        txt = self.cb_ref.get()
        if self.deco:
            self.deco.ref_auto = txt.startswith("Autom")
        if txt.startswith("Autom"):
            if self.deco and (self.deco.vdd_mV or self.deco.fvr_mV):
                fijar_vref((self.deco.vdd_mV or self.deco.fvr_mV) / 1000.0)
            return
        m = re.search(r"(\d{4})", txt)
        if m and 1900 <= int(m.group(1)) <= 4300:
            fijar_vref(int(m.group(1)) / 1000.0)
        else:
            messagebox.showerror("Referencia", "Escribe, por ejemplo, «VDD 3667 mV» o «FVR 2048 mV».")

    def _visible(self, nombre):
        try:
            return self.nb.select() == str(self.tabs[nombre])
        except (KeyError, tk.TclError):
            return False

    # ---------------------------------------------------------------- conexión
    def _refrescar_puertos(self):
        try:
            from serial.tools import list_ports
            reales = [p.device for p in list_ports.comports()]
        except Exception:
            reales = []
        valores = reales + [PUERTO_SIM_SEN, PUERTO_SIM_DC]
        self.cb_puerto["values"] = valores
        if not self.cb_puerto.get():
            self.cb_puerto.set(valores[0])

    def _conectar(self):
        if self.puerto is not None:
            self._desconectar()
            return
        nombre = self.cb_puerto.get()
        try:
            if nombre == PUERTO_SIM_SEN:
                self.puerto = Simulador("senoidal")
            elif nombre == PUERTO_SIM_DC:
                self.puerto = Simulador("continua")
            else:
                import serial
                self.puerto = serial.Serial(nombre, BAUD, bytesize=8, parity="N", stopbits=1, timeout=0.05)
        except Exception as e:
            self.puerto = None
            messagebox.showerror("No se pudo abrir el puerto",
                                 f"{e}\n\n¿Otro programa (LabVIEW, Arduino IDE) tiene abierto el COM?")
            return
        self.deco = DecoAscii()
        fijar_vref(VREF_NOMINAL)             # hasta que llegue S:MACRO,FVR=... o S:MACRO,VDD=...
        self._cambio_referencia()
        self.fs = FS
        self.plano_desde = 0
        self.cero = None
        self.parar.clear()
        time.sleep(0.1)
        self.puerto.reset_input_buffer()
        self.t_inicio = time.perf_counter()
        self.hilo = threading.Thread(target=self._leer, daemon=True)
        self.hilo.start()
        self.bt_conectar.config(text="Desconectar")
        self.cb_puerto.config(state="disabled")

    def _enviar_comando(self):
        """Envía al PIC la línea escrita (Z, R, A:1, P:I,512, P?, D:1, X:P,0, B, E?...)."""
        cmd = self.en_cmd.get().strip()
        if not cmd or self.puerto is None:
            return
        try:
            self.puerto.write((cmd + "\n").encode("ascii"))
            self.deco.mensajes.append((time.strftime("%H:%M:%S"), ">> " + cmd))
            self.en_cmd.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("No se pudo enviar", str(e))

    def _leer(self):
        while not self.parar.is_set():
            try:
                n = self.puerto.in_waiting
                datos = self.puerto.read(n if n else 1)
            except Exception:
                self.parar.set()
                break
            if datos:
                self.deco.alimentar(datos)

    def _desconectar(self):
        self.parar.set()
        if self.hilo:
            self.hilo.join(timeout=1)
        try:
            self.puerto.close()
        except Exception:
            pass
        self.puerto = None
        self.bt_conectar.config(text="Conectar")
        self.cb_puerto.config(state="readonly")

    # ---------------------------------------------------------------- ciclo de la interfaz
    def _actualizar(self):
        try:
            self._actualizar_estado()
        finally:
            self._revisar_matlab()
            self.raiz.after(200, self._actualizar)

    def _actualizar_estado(self):
        d = self.deco
        if d is None:
            return
        n = len(d.i)
        ahora = time.perf_counter()
        dur = ahora - self.t_inicio if self.t_inicio else 0
        aviso = ""
        if n == 0 and dur > 1.5:
            aviso = ("\n⚠ No llega nada: revisa el COM, JP_TX/JP_RX\n"
                     "   y que el PIC esté programado.")
        dt = ahora - d.t_primera if d.t_primera else 0
        tasa = (n - 1) / dt if dt > 0.5 and n > 1 else 0
        if n > 50 and dt > 2:
            self.fs = fs_desde_tasa(tasa)
            if self.fs < 100:
                aviso += (f"\n⚠ Solo {self.fs:.0f} líneas/s: MACRO debe mandar 500.\n"
                          "   ¿Flujo apagado (X:T,0) o ráfaga en curso?")
        linea_cod = ""
        if n:
            ui, uq = d.i[-1], d.q[-1]
            m = min(n, max(int(self.fs), 50))
            bi, bq = d.i[-m:], d.q[-m:]
            linea_cod = (f"\núltimo I = {ui} ({ui * LSB:.3f} V)  Q = {uq} ({uq * LSB:.3f} V)"
                         f"\nmín/máx I {min(bi)}…{max(bi)}   Q {min(bq)}…{max(bq)}")
            if max(max(bi), max(bq)) > 4095:
                aviso += ("\n⚠ Llegan códigos > 4095: revisa que el ADC\n"
                          "   esté justificado a la derecha (ADFM = 1).")
            for nom, b in (("I", bi), ("Q", bq)):
                if min(b) >= 4070:
                    aviso += (f"\n⚠ {nom} pegado a 4095: el pin está en {VREF:.3f} V o\n"
                              "   más (fondo de escala). Con el FVR, en REPOSO\n"
                              "   es normal con práctica 2 conectada (sec. 5.3).")
                elif max(b) <= 25:
                    aviso += (f"\n⚠ {nom} ≈ 0 V: no llega señal al pin.\n"
                              "   Revisa J2/J7, JP_IN y JP_ADC.")
        estado = "recibiendo" if n else "esperando líneas I,Q"
        self.var_estado.set(
            f"{estado}\nmuestras: {n}   ({tasa:.0f} /s → fs = {self.fs:.0f} Hz)\n"
            f"líneas malas: {d.lineas_malas}   mensajes del PIC: {d.n_mensajes}\n"
            f"estado del PIC: {d.estado_pic}\n"
            + self._texto_referencia(d)
            + "".join(f"\n  {h} {t}" for h, t in list(d.mensajes)[-3:])
            + linea_cod + aviso)
        if n and self._visible("Señal en vivo"):
            self._dibujar_senal(d, n)
        if n and self._visible("Plano I-Q en vivo"):
            self._dibujar_plano()
        if self.var_auto.get():
            self._tick_auto += 1
            if self._tick_auto >= 5:
                self._tick_auto = 0
                self.analizar(silencioso=True)

    def _texto_referencia(self, d):
        if not d.ref_auto:
            return f"Ref. ADC = {VREF * 1000:.0f} mV (elegida a mano)"
        if d.vdd_mV:
            return f"Ref. ADC = VDD = {d.vdd_mV} mV (firmware_prueba4)"
        if d.fvr_mV:
            return f"Ref. ADC = FVR = {d.fvr_mV} mV"
        return f"Ref. ADC = {VREF * 1000:.0f} mV (nominal; reset = SW1)"

    def _dibujar_senal(self, d, n):
        k = min(n, int(2 * self.fs))
        iv = np.asarray(d.i[-k:], float) * LSB
        qv = np.asarray(d.q[-k:], float) * LSB
        t = np.arange(n - k, n) / self.fs
        self.linea_i.set_data(t, iv)
        self.linea_q.set_data(t, qv)
        fig, ax, lienzo = self.figs["Señal en vivo"]
        ax.set_xlim(t[0], t[0] + 2.0)
        ax.set_title(f"Últimos 2 s ({self.fs:.0f} muestras/s)")
        lo = min(iv.min(), qv.min())
        hi = max(iv.max(), qv.max())
        if self.var_tipo.get() == "periodo" or lo < -0.01 or hi > VREF + 0.01:
            margen = max(0.05 * (hi - lo), 0.01)
            ax.set_ylim(lo - margen, hi + margen)
        else:
            ax.set_ylim(-0.05, VREF + 0.05)
        lienzo.draw_idle()

    # ---------------------------------------------------------------- plano I-Q en vivo
    def _fijar_cero(self):
        d = self.deco
        if not d or not d.i:
            return
        m = max(1, int(0.5 * self.fs))                  # mediana del último medio segundo
        self.cero = (float(np.median(d.i[-m:])), float(np.median(d.q[-m:])))
        self.var_delta.set(True)

    def _cambio_delta(self):
        if self.var_delta.get() and self.cero is None:
            self._fijar_cero()

    def _limpiar_plano(self):
        if self.deco:
            self.plano_desde = len(self.deco.i)
        self._dibujar_plano(forzar=True)

    def _pausa_plano(self):
        self.plano_pausa = not self.plano_pausa
        self.bt_pausa.config(text="Seguir" if self.plano_pausa else "Pausa")

    def _dibujar_plano(self, forzar=False):
        if self.plano_pausa and not forzar:
            return
        d = self.deco
        fig, ax, lienzo = self.figs["Plano I-Q en vivo"]
        n = len(d.i) if d else 0
        estela = ESTELAS_S.get(self.cb_estela.get(), 2.0)
        ini = max(n - int(estela * self.fs), self.plano_desde, 0)
        delta = self.var_delta.get() and self.cero is not None
        if ini >= n:
            self.sc_plano.set_offsets(np.empty((0, 2)))
            self.pt_plano.set_data([], [])
            self.txt_plano.set_text("Sin puntos nuevos (Limpiar)")
            lienzo.draw_idle()
            return
        iv = np.asarray(d.i[ini:n], float)
        qv = np.asarray(d.q[ini:n], float)
        paso = max(1, len(iv) // PUNTOS_MAX_PLANO)
        if paso > 1:                                    # menos puntos, pero siempre el último
            iv = np.append(iv[:-1:paso], iv[-1])
            qv = np.append(qv[:-1:paso], qv[-1])
        if delta:
            x = (iv - self.cero[0]) * LSB * 1e3
            y = (qv - self.cero[1]) * LSB * 1e3
            unidad = "mV"
        else:
            x = iv * LSB
            y = qv * LSB
            unidad = "V"
        self.sc_plano.set_offsets(np.column_stack([x, y]))
        colores = np.empty((len(x), 4))
        colores[:, :3] = COLOR_PLANO
        colores[:, 3] = np.linspace(0.06, 1.0, len(x)) if self.var_desvanecer.get() else 0.6
        self.sc_plano.set_facecolors(colores)
        self.pt_plano.set_data([x[-1]], [y[-1]])

        if self.var_zoom.get():
            cx, cy = (x.min() + x.max()) / 2, (y.min() + y.max()) / 2
            minimo = 10 * LSB * (1e3 if delta else 1)   # no acercarse más que 10 LSB
            medio = max(x.max() - x.min(), y.max() - y.min(), minimo) * 0.6
            ax.set_xlim(cx - medio, cx + medio)
            ax.set_ylim(cy - medio, cy + medio)
        elif delta:
            ax.set_xlim(-self.cero[0] * LSB * 1e3, (4096 - self.cero[0]) * LSB * 1e3)
            ax.set_ylim(-self.cero[1] * LSB * 1e3, (4096 - self.cero[1]) * LSB * 1e3)
        else:
            ax.set_xlim(0, VREF)
            ax.set_ylim(0, VREF)
        ax.set_xlabel(("ΔI" if delta else "I") + f" ({unidad})")
        ax.set_ylabel(("ΔQ" if delta else "Q") + f" ({unidad})")
        ax.set_title(f"Plano I-Q en vivo: {self.cb_estela.get()} de estela ({n - ini} pares)"
                     + ("  [PAUSA]" if self.plano_pausa else ""))
        if delta:
            self.txt_plano.set_text(f"ΔI = {x[-1]:+8.2f} mV\nΔQ = {y[-1]:+8.2f} mV\n"
                                    f"|Δ| = {math.hypot(x[-1], y[-1]):7.2f} mV")
        else:
            self.txt_plano.set_text(f"I = {x[-1]:.4f} V\nQ = {y[-1]:.4f} V")
        lienzo.draw_idle()

    # ---------------------------------------------------------------- análisis
    def _datos(self):
        if self.deco is None:
            return None, "Primero conéctate."
        n = int(self.cb_n.get())
        datos = self.deco.i if self.var_canal.get() == "I" else self.deco.q
        if len(datos) < n:
            return None, f"Faltan muestras: hay {len(datos)} de {n} ({(n - len(datos)) / self.fs:.1f} s más)."
        return np.asarray(datos[-n:], dtype=float), None

    def analizar(self, silencioso=False):
        x, error = self._datos()
        if error:
            if not silencioso:
                self._escribir([(error + "\n", "mal")])
                self.nb.select(self.tab_resultados)
            return
        tipo = self.var_tipo.get()
        canal = self.var_canal.get()
        try:
            if tipo == "senoidal":
                f_txt = self.en_f.get().strip().replace(",", ".")
                r = analizar_senoidal(x, fs=self.fs, f_in=float(f_txt) if f_txt else None)
                self._mostrar_senoidal(r, canal)
                if r["amplitud_pico_V"] < AMPLITUD_MIN_SINAD * VREF / 2:
                    self.var_resumen.set(f"Canal {canal}: sin senoidal · ruido {r['ruido_dist_rms_mV']:.2f} mV rms")
                else:
                    self.var_resumen.set(f"Canal {canal}: SINAD {r['sinad_dB']:.1f} dB · ENOB {r['enob_bits']:.2f} bits")
            elif tipo == "continua":
                r = analizar_continua(x)
                self._mostrar_continua(r, canal, x)
                self.var_resumen.set(f"Canal {canal}: σ = {r['sigma_LSB']:.2f} LSB · media {r['media_V']:.4f} V")
            else:
                r = analizar_periodo(x)
                self._mostrar_periodo(r, x)
                self.var_resumen.set(f"Periodo: {r['media_ns']:.0f} ns · σ = {r['sigma_ns']:.1f} ns")
        except Exception as e:
            self._escribir([(f"Error en el análisis: {e}\n", "mal")])
            return
        self.ultimo, self.ultimo_tipo = r, tipo
        if not silencioso:
            self.nb.select(self.tab_resultados)

    def _mostrar_senoidal(self, r, canal):
        bien = r["sinad_dB"] >= SINAD_MIN
        # Sin una senoidal de prueba grande, el SINAD (dBc) solo compara el ruido contra un
        # pico de ruido: sale negativo y no significa nada.
        sin_senoidal = r["amplitud_pico_V"] < AMPLITUD_MIN_SINAD * VREF / 2
        lineas = [
            (f"SENOIDAL — canal {canal} — {r['muestras']} muestras\n\n", "titulo"),
            (f"SINAD   {r['sinad_dB']:6.1f} dB   ", None),
            ("SIN SENOIDAL DE PRUEBA\n" if sin_senoidal else
             "CUMPLE ≥ 60 dB\n" if bien else "NO CUMPLE (< 60 dB)\n", "mal" if sin_senoidal or not bien else "ok"),
            (f"ENOB    {r['enob_bits']:6.2f} bits\n", None),
            (f"SNR     {r['snr_dB']:6.1f} dB\n", None),
            (f"THD     {r['thd_dB']:6.1f} dB  (armónicos 2 a 5)\n", None),
            (f"SFDR    {r['sfdr_dB']:6.1f} dB\n\n", None),
            (f"Frecuencia   {r['frecuencia_Hz']:8.3f} Hz ({r['ciclos']:.1f} ciclos)\n", None),
            (f"Amplitud     {r['amplitud_pico_V']:8.4f} V pico\n", None),
            (f"Continua     {r['dc_V']:8.4f} V  (código {r['dc_codigo']:.1f})\n", None),
            (f"Ruido+dist.  {r['ruido_dist_rms_mV']:8.3f} mV rms ({r['ruido_dist_rms_LSB']:.2f} LSB)\n", None),
            (f"Mín / máx    {r['minimo']} / {r['maximo']}\n\n", None),
            (f"Referido a escala completa ({VREF / 2:.3f} V pico):\n", None),
            (f"SINAD_FS {r['sinad_fs_dB']:5.1f} dB   ENOB_FS {r['enob_fs_bits']:.2f} bits\n", None),
            ("\nIdeal 12 bits: 74,0 dB. Requisito: > 60 dB\n(ENOB > 9,67; ruido+dist. < 0,72 mV rms\ncon senoidal a escala completa).\n", None),
        ]
        if sin_senoidal:
            lineas.insert(1, (f"⚠ La «fundamental» mide solo {r['amplitud_pico_V'] * 1e3:.1f} mV pico: en esta captura "
                              f"no hay una senoidal de prueba, así que el SINAD no significa nada. Lo que sí vale es "
                              f"el ruido: {r['ruido_dist_rms_mV']:.2f} mV rms ({r['ruido_dist_rms_LSB']:.1f} LSB), "
                              f"que a escala completa da SINAD_FS = {r['sinad_fs_dB']:.1f} dB.\n"
                              "Para medir SINAD (prueba S1, sec. 9.3): generador en J7 con JP_IN 2–3, senoidal "
                              "centrada en 1,024 V y 0,95 V de amplitud.\n\n", "mal"))
        if r["pocos_ciclos"]:
            lineas.append(("\n⚠ Muy pocos ciclos en la captura: la fundamental\n   se mezcla con la continua. Usa más muestras\n   o una frecuencia mayor (≥ 2 Hz con 4096 a 500 Hz).\n", "mal"))
        if r["recorte"]:
            lineas.append(("\n⚠ La señal toca 0 o 4095: hay RECORTE.\n   Baja la amplitud del generador.\n", "mal"))
        if r["frecuencia_Hz"] < 1.0:
            lineas.append(("\n⚠ No se ve una senoidal clara.\n   ¿Es una señal continua? Usa «Continua».\n", "mal"))
        self._escribir(lineas)

        fig, ax, lienzo = self.figs["Espectro"]
        ax.clear()
        esp = r["_espectro"]
        f = np.arange(len(esp)) * self.fs / r["muestras"]
        dbfs = 10 * np.log10(np.maximum(esp, 1e-30) / r["_p_fs"])
        ax.plot(f, dbfs, lw=0.7, color="#1f4e79")
        lo, hi = r["_banda"]
        ax.plot(f[lo:hi], dbfs[lo:hi], lw=1.4, color="#2e7d32", label="fundamental")
        for h, kh, _p in r["_armonicos"]:
            ax.plot(f[kh], dbfs[kh], "v", color="#c62828")
            ax.annotate(f"{h}", (f[kh], dbfs[kh]), textcoords="offset points", xytext=(0, 6),
                        ha="center", fontsize=8, color="#c62828")
        ax.set_xlim(0, self.fs / 2)
        ax.set_ylim(max(dbfs.min(), -160) - 5, 5)
        ax.set_xlabel("frecuencia (Hz)")
        ax.set_ylabel("dBFS (0 dB = senoidal a escala completa)")
        ax.set_title(f"Espectro canal {canal}: SINAD = {r['sinad_dB']:.1f} dB, ENOB = {r['enob_bits']:.2f} bits")
        ax.grid(True)
        ax.legend(loc="upper right")
        lienzo.draw()
        self._histograma(np.asarray((self.deco.i if canal == "I" else self.deco.q)[-r["muestras"]:]), canal,
                         gauss=False)

    def _mostrar_continua(self, r, canal, x):
        lineas = [
            (f"CONTINUA — canal {canal} — {r['muestras']} muestras\n\n", "titulo"),
            (f"Media          {r['media_codigo']:9.2f} códigos = {r['media_V']:.4f} V\n", None),
            (f"Ruido rms (σ)  {r['sigma_LSB']:9.3f} LSB = {r['sigma_uV']:.1f} µV\n", None),
            (f"Pico a pico    {r['pp_codigos']:9d} códigos (medido)\n", None),
            (f"Pico a pico    {r['pp_estimado_uV']:9.1f} µV (≈ 6,6 σ)\n", None),
            (f"Códigos dist.  {r['codigos_distintos']:9d}\n", None),
            (f"Resol. efect.  {r['resol_efectiva_bits']:9.2f} bits\n", None),
            (f"Libre de ruido {r['resol_libre_ruido_bits']:9.2f} bits\n", None),
            (f"Incert. de σ   {r['incertidumbre_sigma_pct']:9.2f} %\n\n", None),
            ("Ideal (solo cuantización): σ = 0,29 LSB\n= 144 µV. Criterio: σ ≤ 1,4 LSB (0,7 mV).\n", None),
        ]
        bien = r["sigma_LSB"] <= 1.4
        lineas.insert(3, ("   → CUMPLE σ ≤ 1,4 LSB\n" if bien else "   → NO CUMPLE σ ≤ 1,4 LSB\n",
                          "ok" if bien else "mal"))
        self._escribir(lineas)
        self._histograma(x, canal, gauss=True, r=r)

    def _mostrar_periodo(self, r, x):
        lineas = [
            (f"PERIODO — {r['muestras']} muestras (Q = cuentas de Timer1)\n\n", "titulo"),
            (f"Media      {r['media_ns']:12.1f} ns\n", None),
            (f"σ          {r['sigma_ns']:12.1f} ns\n", None),
            (f"Mín / máx  {r['min_ns']:.1f} / {r['max_ns']:.1f} ns\n", None),
            (f"Frecuencia {r['frecuencia_Hz']:12.3f} Hz\n\n", None),
            ("Resolución: 62,5 ns por cuenta. Solo tiene\nsentido con MODO_PERIODO = 1 en el firmware.\n", None),
        ]
        self._escribir(lineas)
        fig, ax, lienzo = self.figs["Histograma"]
        ax.clear()
        t = x * T_TIMER1_NS
        ax.hist(t, bins=min(100, max(10, len(np.unique(x)))), color="#1f4e79")
        ax.set_xlabel("periodo (ns)")
        ax.set_ylabel("ocurrencias")
        ax.set_title(f"Histograma del periodo: media {r['media_ns']:.0f} ns, σ = {r['sigma_ns']:.1f} ns")
        ax.grid(True)
        lienzo.draw()

    def _histograma(self, x, canal, gauss, r=None):
        fig, ax, lienzo = self.figs["Histograma"]
        ax.clear()
        x = np.asarray(x, dtype=float)
        lo, hi = int(x.min()), int(x.max())
        if hi - lo > 400:
            bins = 200
        else:
            bins = np.arange(lo, hi + 2) - 0.5
        ax.hist(x, bins=bins, color="#1f4e79", edgecolor="white", linewidth=0.3)
        if gauss and r and r["sigma_LSB"] > 0:
            xs = np.linspace(lo - 1, hi + 1, 400)
            g = len(x) / (r["sigma_LSB"] * math.sqrt(2 * math.pi)) * np.exp(
                -0.5 * ((xs - r["media_codigo"]) / r["sigma_LSB"]) ** 2)
            ax.plot(xs, g, color="#c62828", lw=1.2, label="gaussiana con la misma σ")
            ax.legend(loc="upper right")
            ax.set_title(f"Histograma de códigos, canal {canal}: σ = {r['sigma_LSB']:.2f} LSB")
        else:
            ax.set_title(f"Histograma de códigos, canal {canal}")
        ax.set_xlabel("código del ADC")
        ax.set_ylabel("ocurrencias")
        ax.grid(True)
        lienzo.draw()

    # ---------------------------------------------------------------- SINAD con MATLAB
    def sinad_matlab(self):
        """Guarda la captura del canal elegido y la manda a MATLAB (macro_sinad.m, en otro hilo)."""
        if self.matlab_ocupado:
            return
        x, error = self._datos()
        if error:
            self._escribir([(error + "\n", "mal")])
            self.nb.select(self.tab_resultados)
            return
        canal = self.var_canal.get()
        try:
            os.makedirs(CARPETA_CAPTURAS, exist_ok=True)
            with open(os.path.join(CARPETA_CAPTURAS, "macro_sinad.m"), "w", encoding="utf-8") as f:
                f.write(MATLAB_SINAD_M)
            nombre = f"captura_{canal}_{time.strftime('%Y%m%d_%H%M%S')}.csv"
            with open(os.path.join(CARPETA_CAPTURAS, nombre), "w", newline="") as f:
                f.write("codigo\n")
                f.write("\n".join(str(int(v)) for v in x) + "\n")
        except OSError as e:
            messagebox.showerror("No se pudo guardar la captura", str(e))
            return
        orden = (f"cd({texto_matlab(CARPETA_CAPTURAS)}); "
                 f"macro_sinad({texto_matlab(nombre)}, {self.fs:.10g}, {VREF:.6g}, {texto_matlab(canal)});")
        try:
            f_txt = self.en_f.get().strip().replace(",", ".")
            py = analizar_senoidal(x, fs=self.fs, f_in=float(f_txt) if f_txt else None)
        except Exception:
            py = None
        exe = buscar_matlab()
        if exe is None:
            self._escribir([
                ("SINAD EN MATLAB\n\n", "titulo"),
                ("No encontré matlab.exe (ni en el PATH ni en C:\\Program Files\\MATLAB).\n\n", "mal"),
                ("La captura quedó lista. Abre MATLAB y pega:\n\n", None),
                (orden + "\n", "titulo"),
            ])
            self.nb.select(self.tab_resultados)
            return
        self.matlab_ocupado = True
        self.bt_matlab.config(state="disabled", text="MATLAB calculando…")
        self._escribir([
            ("SINAD EN MATLAB\n\n", "titulo"),
            (f"Canal {canal}, {len(x)} muestras a {self.fs:.0f} Hz, VREF = {VREF:.4f} V.\n", None),
            (f"MATLAB: {exe}\n\n", None),
            ("Calculando… MATLAB tarda unos 20 a 60 s en arrancar.\n", "titulo"),
            ("Mientras tanto puedes seguir usando la interfaz.\n", None),
        ])
        self.nb.select(self.tab_resultados)
        threading.Thread(target=self._hilo_matlab, args=(exe, orden, canal, nombre, py),
                         daemon=True).start()

    def _hilo_matlab(self, exe, orden, canal, nombre, py):
        t0 = time.perf_counter()
        try:
            proc = subprocess.run([exe, "-batch", orden], capture_output=True, text=True,
                                  timeout=T_LIMITE_MATLAB_S, cwd=CARPETA_CAPTURAS,
                                  creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            salida, err, codigo = proc.stdout, proc.stderr, proc.returncode
        except subprocess.TimeoutExpired:
            salida, err, codigo = "", f"MATLAB no terminó en {T_LIMITE_MATLAB_S} s.", -1
        except OSError as e:
            salida, err, codigo = "", f"No se pudo ejecutar MATLAB: {e}", -1
        valores = dict(re.findall(r"^MACRO_(\w+)=(.*?)\s*$", salida, flags=re.M))
        if "SINAD_dB" not in valores and codigo == 0:
            # En Windows el lanzador de MATLAB puede volver antes de terminar o sin pasar la
            # salida: macro_sinad.m también deja los resultados en <captura>_resultado.txt.
            archivo = os.path.join(CARPETA_CAPTURAS, nombre[:-4] + "_resultado.txt")
            while time.perf_counter() - t0 < T_LIMITE_MATLAB_S and not os.path.exists(archivo):
                time.sleep(1)
            time.sleep(0.5)
            try:
                with open(archivo, encoding="utf-8", errors="replace") as f:
                    valores = dict(re.findall(r"^MACRO_(\w+)=(.*?)\s*$", f.read(), flags=re.M))
            except OSError:
                err = err or "MATLAB terminó sin dar resultados."
        self.cola_matlab.put(dict(valores=valores, salida=salida, err=err, codigo=codigo,
                                  canal=canal, nombre=nombre, orden=orden, py=py,
                                  segundos=time.perf_counter() - t0))

    def _revisar_matlab(self):
        while True:
            try:
                res = self.cola_matlab.get_nowait()
            except queue.Empty:
                return
            self.matlab_ocupado = False
            self.bt_matlab.config(state="normal", text="SINAD en MATLAB")
            self._mostrar_matlab(res)

    def _mostrar_matlab(self, res):
        v, py = res["valores"], res["py"]
        if res["codigo"] != 0 or "SINAD_dB" not in v:
            detalle = (res["err"] or res["salida"] or "(sin salida)").strip()[-1500:]
            self._escribir([
                ("SINAD EN MATLAB — ERROR\n\n", "titulo"),
                (detalle + "\n\n", "mal"),
                ("Si falta Signal Processing Toolbox, sinad() no existe.\n", None),
                ("Para probar a mano en MATLAB:\n\n", None),
                (res["orden"] + "\n", "titulo"),
            ])
            self.nb.select(self.tab_resultados)
            return

        def num(k):
            try:
                return float(v[k])
            except (KeyError, ValueError):
                return float("nan")

        sinad = num("SINAD_dB")
        bien = sinad >= SINAD_MIN
        filas = [("SINAD (dB)", "SINAD_dB", "sinad_dB", "{:8.2f}"),
                 ("ENOB (bits)", "ENOB_bits", "enob_bits", "{:8.2f}"),
                 ("SNR (dB)", "SNR_dB", "snr_dB", "{:8.2f}"),
                 ("THD (dB)", "THD_dB", "thd_dB", "{:8.2f}"),
                 ("SFDR (dB)", "SFDR_dB", "sfdr_dB", "{:8.2f}"),
                 ("Frecuencia (Hz)", "FRECUENCIA_Hz", "frecuencia_Hz", "{:8.3f}")]
        lineas = [
            (f"SINAD EN MATLAB — canal {res['canal']} — {int(num('MUESTRAS'))} muestras\n", "titulo"),
            (f"MATLAB {v.get('MATLAB', '?')}  ({res['segundos']:.0f} s)\n\n", None),
            (f"SINAD   {sinad:6.2f} dB   ", None),
            ("CUMPLE ≥ 60 dB\n" if bien else "NO CUMPLE (< 60 dB)\n", "ok" if bien else "mal"),
            (f"ENOB    {num('ENOB_bits'):6.2f} bits   (ENOB = (SINAD − 1,76) / 6,02)\n\n", None),
            (f"{'':17s}{'MATLAB':>10s}{'Python':>10s}\n", "titulo"),
        ]
        for etiqueta, km, kp, fmt in filas:
            vp = fmt.format(py[kp]) if py and kp in py else "      —"
            lineas.append((f"{etiqueta:17s}{fmt.format(num(km)):>10s}{vp:>10s}\n", None))
        lineas += [
            ("\nMATLAB usa sinad(), snr(), thd() y sfdr() de Signal Processing Toolbox "
             "(ventana de Kaiser β = 38; THD con la fundamental y 5 armónicos). Python usa "
             "Kaiser β = 14 y armónicos 2 a 5: diferencias de unas décimas de dB son normales.\n\n", None),
            ("Archivos en:\n" + CARPETA_CAPTURAS + "\n", None),
            ("Para repetirlo en MATLAB, delante del profesor:\n", None),
            (res["orden"] + "\n", "titulo"),
        ]
        self._escribir(lineas)
        self.var_resumen.set(f"MATLAB canal {res['canal']}: SINAD {sinad:.2f} dB · ENOB {num('ENOB_bits'):.2f} bits")
        self.nb.select(self.tab_resultados)

        figura = v.get("FIGURA")
        fig, ax, lienzo = self.figs["MATLAB"]
        ax.clear()
        ax.axis("off")
        try:
            import matplotlib.image as mpimg
            ax.imshow(mpimg.imread(figura))
            ax.set_title(f"Figura de MATLAB: {os.path.basename(figura)}", fontsize=9)
        except Exception as e:
            ax.text(0.5, 0.5, f"No se pudo abrir la figura de MATLAB:\n{e}", ha="center", va="center",
                    transform=ax.transAxes)
        lienzo.draw()

    # ---------------------------------------------------------------- texto y archivos
    def _escribir(self, partes):
        self.txt.config(state=tk.NORMAL)
        self.txt.delete("1.0", tk.END)
        for texto, tag in partes:
            self.txt.insert(tk.END, texto, tag)
        self.txt.config(state=tk.DISABLED)

    def guardar_csv(self):
        if not self.deco or not self.deco.i:
            messagebox.showinfo("Sin datos", "No hay muestras todavía.")
            return
        ruta = filedialog.asksaveasfilename(defaultextension=".csv", initialfile="captura_macro.csv",
                                            filetypes=[("CSV", "*.csv")])
        if not ruta:
            return
        with open(ruta, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["n", "t_s", "i", "q", "i_V", "q_V"])
            for k, (i, q) in enumerate(zip(self.deco.i, self.deco.q)):
                w.writerow([k, f"{k / self.fs:.4f}", i, q, f"{i * LSB:.5f}", f"{q * LSB:.5f}"])
        messagebox.showinfo("Guardado", f"{len(self.deco.i)} muestras en\n{ruta}")

    def guardar_reporte(self):
        if self.ultimo is None:
            messagebox.showinfo("Sin medición", "Primero presiona «Analizar ahora».")
            return
        ruta = filedialog.asksaveasfilename(defaultextension=".txt", initialfile="reporte_medicion.txt",
                                            filetypes=[("Texto", "*.txt")])
        if not ruta:
            return
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(f"MACRO — medición {self.ultimo_tipo}, canal {self.var_canal.get()}, "
                    f"{time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"fs = {self.fs:.0f} muestras/s (líneas ASCII), VREF = {VREF:.4f} V (FVR)\n")
            f.write(f"estado del PIC: {self.deco.estado_pic}, líneas malas: {self.deco.lineas_malas}\n")
            f.write(self.txt.get("1.0", tk.END))
            f.write("\nValores numéricos:\n")
            for k, v in self.ultimo.items():
                if not k.startswith("_"):
                    f.write(f"  {k} = {v}\n")
        for nombre, (fig, _ax, _l) in self.figs.items():
            fig.savefig(ruta.rsplit(".", 1)[0] + "_" + nombre.replace(" ", "_").replace("ñ", "n") + ".png", dpi=150)
        messagebox.showinfo("Guardado", f"Reporte y gráficas guardados junto a\n{ruta}")

    def borrar(self):
        if self.deco:
            d = self.deco
            d.i.clear(); d.q.clear()
            d.lineas_malas = 0; d.n_mensajes = 0; d.t_primera = None
            self.t_inicio = time.perf_counter()
            self.plano_desde = 0

    def cerrar(self):
        if self.puerto is not None:
            self._desconectar()
        self.raiz.destroy()


def main():
    raiz = tk.Tk()
    app = App(raiz)
    raiz._app = app
    if "--autotest" in sys.argv:            # prueba automática (sin teclado): simula, analiza y sale
        app.cb_puerto.set(PUERTO_SIM_SEN)
        app._conectar()

        def paso1():
            app.analizar()
            for nombre, (fig, _ax, _l) in app.figs.items():
                fig.savefig(f"autotest_{nombre.replace(' ', '_').replace('ñ', 'n')}.png", dpi=80)
            print(app.txt.get("1.0", tk.END))
            app.var_tipo.set("continua")
            app.analizar()
            print(app.txt.get("1.0", tk.END))
            app.figs["Histograma"][0].savefig("autotest_Histograma_continua.png", dpi=80)
            raiz.update()
            raiz.after(300, app.cerrar)
        raiz.after(9500, paso1)              # 4096 muestras a 500 /s = 8,2 s
    raiz.mainloop()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        import traceback
        _falta("La interfaz se detuvo por un error:\n\n" + traceback.format_exc())
