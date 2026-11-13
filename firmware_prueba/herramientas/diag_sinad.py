#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""diag_sinad.py - Diagnostico del ruido y del SINAD de MACRO en el PC.

Necesita:  pip install numpy pyserial      (pyserial solo para "capturar")

  python diag_sinad.py capturar --puerto COM5 --segundos 20 --salida q_dc.csv
  python diag_sinad.py capturar --puerto COM5 --rafaga --salida q_silencio.csv --cmd X:L,0
  python diag_sinad.py ruido q_dc.csv
  python diag_sinad.py seno  i_20hz.csv --canal I

"ruido": entrada fija. Da sigma y dice de que esta hecho el ruido (red de 60 Hz, alias del
         PWM de 15,625 kHz en 125/250 Hz, deriva lenta o ruido blanco) y si I y Q se mueven juntos.
"seno":  entrada senoidal. Ajusta la senoidal por minimos cuadrados (no necesita muestreo
         coherente), da el SINAD y separa el error en ruido aditivo y error de tiempo
         (lineas perdidas, jitter), que es lo que hace caer el SINAD al subir la frecuencia.

Los CSV pueden ser los de este script o los de la interfaz: se toman las DOS ULTIMAS columnas
numericas de cada linea como I y Q (una columna de tiempo delante no estorba).
"""
import argparse
import sys
import time

import numpy as np

FS = 500.0            # muestras/s por canal (sec. 0 de la especificacion)
F_PWM = 15625.0       # portadora de PWM6/PWM7
F_RED = 60.0          # red electrica
LSB_MV = 0.5          # 2,048 V / 4096
FS_RMS_LSB = 2048.0 / np.sqrt(2.0)   # senoidal a escala completa (1,024 V pico)


# ----------------------------------------------------------------------------- lectura
def leer_csv(ruta):
    filas = []
    with open(ruta, "r", encoding="utf-8", errors="replace") as f:
        for linea in f:
            campos = linea.replace(";", ",").strip().split(",")
            nums = []
            for c in campos:
                try:
                    nums.append(float(c))
                except ValueError:
                    pass
            if len(nums) >= 2 and len(nums) >= len(campos) - 1:
                filas.append((nums[-2], nums[-1]))
    if len(filas) < 64:
        sys.exit(f"{ruta}: solo {len(filas)} lineas con datos; hacen falta al menos 64.")
    d = np.array(filas)
    return d[:, 0], d[:, 1]


# ----------------------------------------------------------------------------- ruido
def alias(f, fs):
    f = f % fs
    return fs - f if f > fs / 2 else f


def etiqueta_tono(f, fs):
    if f < 2.0:
        return "deriva lenta / 1/f"
    for k in range(1, 9):
        if abs(f - alias(k * F_RED, fs)) <= 1.5:
            return f"red electrica (armonico {k} de 60 Hz)"
    for k in range(1, 4):
        if abs(f - alias(k * F_PWM, fs)) <= 1.5 and alias(k * F_PWM, fs) > 2:
            return f"alias del PWM de 15,625 kHz (armonico {k})"
    return "sin identificar"


def analizar_ruido(x, fs, nombre):
    n = len(x)
    media = x.mean()
    r = x - media
    sigma = r.std()
    t = np.arange(n)
    r_sin_deriva = r - np.polyval(np.polyfit(t, r, 1), t)
    print(f"\n=== Canal {nombre}: {n} muestras ({n / fs:.1f} s) ===")
    print(f"  media = {media:.2f} LSB ({media * LSB_MV:.1f} mV)")
    print(f"  sigma = {sigma:.2f} LSB = {sigma * LSB_MV:.3f} mV rms   (criterio: <= 1,4 LSB; ideal 0,29)")
    print(f"  pico a pico = {x.max() - x.min():.0f} LSB, codigos distintos = {len(np.unique(x))}")
    print(f"  sigma sin la deriva lineal = {r_sin_deriva.std():.2f} LSB")
    print(f"  SINAD que permite este ruido con una senoidal a escala completa: "
          f"{20 * np.log10(FS_RMS_LSB / max(sigma, 1e-9)):.1f} dB (hacen falta 60)")

    # Espectro: potencia por bin en LSB^2, de modo que la suma de los bins da la varianza.
    w = np.hanning(n)
    X = np.fft.rfft(r * w)
    p = 2.0 * np.abs(X) ** 2 / (n * np.sum(w ** 2))
    f = np.fft.rfftfreq(n, 1.0 / fs)
    p[0] = 0.0
    total = p.sum()
    piso = np.median(p[1:])
    blanco = piso / np.log(2.0) * (len(p) - 1)       # mediana de una exponencial = media * ln 2
    print(f"  ruido blanco (piso del espectro): ~{np.sqrt(blanco):.2f} LSB rms "
          f"= {100 * min(blanco / total, 1):.0f} % de la varianza")

    # Tonos: grupos de bins muy por encima del piso.
    fuerte = p > 30.0 * piso
    tonos = []
    k = 1
    while k < len(p):
        if fuerte[k]:
            j = k
            while j + 1 < len(p) and fuerte[j + 1]:
                j += 1
            pot = p[k:j + 1].sum()
            fc = float(np.sum(f[k:j + 1] * p[k:j + 1]) / pot)
            tonos.append((pot, fc))
            k = j + 1
        else:
            k += 1
    tonos.sort(reverse=True)
    if tonos:
        print("  tonos (lo que NO es ruido blanco):")
        for pot, fc in tonos[:8]:
            print(f"    {fc:7.2f} Hz  {np.sqrt(pot):6.2f} LSB rms  {100 * pot / total:5.1f} % de la varianza"
                  f"  -> {etiqueta_tono(fc, fs)}")
    else:
        print("  sin tonos: el ruido es de banda ancha (blanco) en 0-250 Hz.")
    return r


def cmd_ruido(a):
    i, q = leer_csv(a.archivo)
    ri = analizar_ruido(i, a.fs, "I") if a.canal in ("I", "IQ") else None
    rq = analizar_ruido(q, a.fs, "Q") if a.canal in ("Q", "IQ") else None
    if ri is not None and rq is not None and ri.std() > 0 and rq.std() > 0:
        rho = float(np.corrcoef(ri, rq)[0, 1])
        print(f"\nCorrelacion entre el ruido de I y el de Q: {rho:+.2f}")
        print("  (cerca de +1: una fuente comun -referencia, tierra o la misma fuente de senal-;")
        print("   cerca de 0: ruido independiente en cada entrada, o de banda ancha, porque I y Q")
        print("   se muestrean con 1 ms de diferencia)")
    print("\nComo leerlo:")
    print("  * Tonos de 60/120/180 Hz  -> lazo de tierra o captacion de red: es el montaje.")
    print("  * Tonos de 125/250 Hz     -> el PWM de 15,625 kHz se acopla a la entrada: repetir con X:P,0.")
    print("  * Todo blanco             -> ruido de banda ancha que el ADC, sin filtro (JP_ADC 2-3), pliega")
    print("                               entero a 0-250 Hz: fuente ruidosa o conmutada, o el propio chip")
    print("                               (se distingue con D:1 del firmware de prueba).")


# ----------------------------------------------------------------------------- seno
def ajuste_seno(x, fs):
    """Ajuste de 4 parametros (IEEE 1057): x = a cos(wt) + b sin(wt) + c."""
    n = len(x)
    t = np.arange(n) / fs
    w = np.hanning(n)
    X = np.abs(np.fft.rfft((x - x.mean()) * w))
    k = int(np.argmax(X[1:-1])) + 1
    d = 0.5 * (X[k + 1] - X[k - 1]) / (2 * X[k] - X[k - 1] - X[k + 1])      # interpolacion parabolica
    om = 2 * np.pi * (k + d) * fs / n
    for _ in range(30):
        c, s = np.cos(om * t), np.sin(om * t)
        if "ab" in locals():
            A = np.column_stack([c, s, np.ones(n), -ab[0] * t * s + ab[1] * t * c])
        else:
            A = np.column_stack([c, s, np.ones(n)])
        sol = np.linalg.lstsq(A, x, rcond=None)[0]
        ab = sol[:2]
        if len(sol) == 4:
            om += sol[3]
            if abs(sol[3]) < 1e-12 * om:
                break
    c, s = np.cos(om * t), np.sin(om * t)
    sol = np.linalg.lstsq(np.column_stack([c, s, np.ones(n)]), x, rcond=None)[0]
    modelo = sol[0] * c + sol[1] * s + sol[2]
    return om, sol, modelo


def cmd_seno(a):
    i, q = leer_csv(a.archivo)
    x = i if a.canal == "I" else q
    if a.muestras and a.muestras < len(x):
        x = x[-a.muestras:]
    n = len(x)
    fs = a.fs
    om, (ca, sa, dc), modelo = ajuste_seno(x, fs)
    amp = float(np.hypot(ca, sa))
    f0 = om / (2 * np.pi)
    res = x - modelo
    sinad = 20 * np.log10(amp / np.sqrt(2) / res.std())
    print(f"\n=== Canal {a.canal}: {n} muestras, senoidal ajustada ===")
    print(f"  f = {f0:.4f} Hz ({f0 * n / fs:.1f} ciclos), amplitud = {amp:.1f} LSB ({amp * LSB_MV / 1000:.4f} V pico), "
          f"centro = {dc:.1f} LSB")
    if x.min() <= 7 or x.max() >= 4088:
        print("  AVISO: la senal toca el fondo de escala (recorte). Con FVR la entrada debe ir de")
        print("         0,074 a 1,974 V (centro 1,024 V, amplitud 0,95 V), no centrada en 1,85 V.")
    print(f"  error total = {res.std():.2f} LSB rms")
    print(f"  SINAD = {sinad:.1f} dB   ENOB = {(sinad - 1.76) / 6.02:.2f} bits   "
          f"(llevado a escala completa: {20 * np.log10(FS_RMS_LSB / res.std()):.1f} dB)")

    # Armonicos 2..5 (plegados) -> distorsion
    t = np.arange(n) / fs
    cols, orden = [], []
    for h in range(2, 6):
        fh = alias(h * f0, fs)
        if abs(fh - f0) < 2 * fs / n or fh < 2 * fs / n or abs(fh - fs / 2) < 2 * fs / n:
            continue
        cols += [np.cos(2 * np.pi * h * f0 * t), np.sin(2 * np.pi * h * f0 * t)]
        orden.append(h)
    pot_arm = 0.0
    if cols:
        coef = np.linalg.lstsq(np.column_stack(cols), res, rcond=None)[0]
        for j, h in enumerate(orden):
            ah = float(np.hypot(coef[2 * j], coef[2 * j + 1]))
            pot_arm += ah ** 2 / 2
        print(f"  THD (armonicos {orden}) = {10 * np.log10(max(pot_arm, 1e-12) / (amp ** 2 / 2)):.1f} dBc")

    # Error de tiempo: var(res | fase) = sa^2 + (pendiente * st)^2
    fase = om * t + np.arctan2(-sa, ca)
    pend = -amp * om * np.sin(fase)                    # dx/dt en LSB/s
    M = np.column_stack([np.ones(n), pend ** 2])
    v0, v1 = np.linalg.lstsq(M, res ** 2, rcond=None)[0]
    sig_ad = np.sqrt(max(v0, 0.0))
    sig_t = np.sqrt(max(v1, 0.0))
    aporte_t = sig_t * amp * om / np.sqrt(2)
    print(f"  ruido aditivo (no depende de la pendiente): {sig_ad:.2f} LSB rms")
    print(f"  error de tiempo equivalente: {sig_t * 1e6:.1f} us rms -> {aporte_t:.2f} LSB rms a esta frecuencia")
    if aporte_t > sig_ad:
        print("  -> Domina el error de TIEMPO: el error crece donde la senal cambia mas rapido. Eso no lo")
        print("     hace el ruido de la entrada: es jitter, lineas perdidas o la frecuencia del generador")
        print("     moviendose. Mira los saltos de fase de abajo.")
    else:
        print("  -> Domina el ruido ADITIVO: el mismo que se ve con entrada fija (comando 'ruido').")

    # Saltos de fase por bloques (una linea perdida = un salto de 1 muestra)
    B = max(int(round(6 * fs / f0)), 64)
    if n >= 4 * B:
        fases = []
        for k0 in range(0, n - B + 1, B):
            tb = t[k0:k0 + B]
            A = np.column_stack([np.cos(om * tb), np.sin(om * tb), np.ones(B)])
            c1, s1, _ = np.linalg.lstsq(A, x[k0:k0 + B], rcond=None)[0]
            fases.append(np.arctan2(-s1, c1))
        dif = np.diff(np.unwrap(np.array(fases)))
        dif = (dif + np.pi) % (2 * np.pi) - np.pi
        en_muestras = dif / (om / fs)
        peor = int(np.argmax(np.abs(en_muestras)))
        print(f"  mayor salto de fase entre bloques de {B} muestras: {en_muestras[peor]:+.2f} muestras "
              f"(cerca de la muestra {(peor + 1) * B})")
        saltos = int(np.sum(np.abs(en_muestras) > 0.3))
        if saltos:
            print(f"  -> {saltos} salto(s) de mas de 0,3 muestras: se perdieron lineas entre el PIC y el archivo.")
            print("     Revisa E? en el firmware de prueba (TXOVR) y el lector del PC.")
        else:
            print("  -> sin saltos: no se perdieron lineas dentro de la captura.")


# ----------------------------------------------------------------------------- captura
def cmd_capturar(a):
    try:
        import serial
    except ImportError:
        sys.exit("Falta pyserial:  pip install pyserial")
    ser = serial.Serial(a.puerto, 115200, timeout=0.2)
    time.sleep(0.3)
    ser.reset_input_buffer()

    def enviar(c):
        ser.write((c + "\n").encode("ascii"))
        print(f">> {c}")

    for c in a.cmd or []:
        enviar(c)
        time.sleep(0.3)
    filas, mensajes = [], []
    en_rafaga = False
    if a.rafaga:
        enviar("B")
    fin = time.time() + (5.0 if a.rafaga else a.segundos + 1.0)
    descartar_hasta = time.time() + (0.0 if a.rafaga else 1.0)     # 1 s de asentamiento
    buf = b""
    terminado = False
    while time.time() < fin and not terminado:
        buf += ser.read(4096)
        while b"\n" in buf:
            linea, buf = buf.split(b"\n", 1)
            txt = linea.decode("ascii", errors="replace").strip()
            if not txt:
                continue
            if txt[0].isdigit():
                p = txt.split(",")
                if len(p) == 2 and p[0].isdigit() and p[1].isdigit():
                    if a.rafaga:
                        if en_rafaga:
                            filas.append((int(p[0]), int(p[1])))
                    elif time.time() >= descartar_hasta:
                        filas.append((int(p[0]), int(p[1])))
            else:
                print(f"<< {txt}")
                mensajes.append(txt)
                if txt.startswith("S:RAFAGA"):
                    en_rafaga = True
                elif txt == "S:FIN":
                    terminado = True
    if not a.rafaga:
        enviar("E?")
        time.sleep(0.3)
        print("<< " + ser.read(4096).decode("ascii", errors="replace").strip().splitlines()[-1])
    ser.close()
    with open(a.salida, "w", encoding="utf-8") as f:
        f.write("I,Q\n")
        for i, q in filas:
            f.write(f"{i},{q}\n")
    print(f"{len(filas)} pares guardados en {a.salida}")
    if not a.rafaga:
        esperado = a.segundos * FS
        print(f"  ({len(filas) / a.segundos:.1f} pares/s; deberian ser ~{FS:.0f}. Si faltan mas del 3 %, el PC pierde lineas.)")
        del esperado


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="orden", required=True)

    c = sub.add_parser("capturar", help="guarda pares I,Q del puerto serie en un CSV")
    c.add_argument("--puerto", required=True)
    c.add_argument("--segundos", type=float, default=20.0)
    c.add_argument("--salida", required=True)
    c.add_argument("--cmd", action="append", help="comando previo, repetible (ej. --cmd D:1 --cmd X:P,0)")
    c.add_argument("--rafaga", action="store_true", help="usa el comando B: 256 pares con la UART en silencio")
    c.set_defaults(func=cmd_capturar)

    r = sub.add_parser("ruido", help="analiza una captura con entrada fija")
    r.add_argument("archivo")
    r.add_argument("--canal", choices=["I", "Q", "IQ"], default="IQ")
    r.add_argument("--fs", type=float, default=FS)
    r.set_defaults(func=cmd_ruido)

    s = sub.add_parser("seno", help="analiza una captura con entrada senoidal")
    s.add_argument("archivo")
    s.add_argument("--canal", choices=["I", "Q"], default="I")
    s.add_argument("--fs", type=float, default=FS)
    s.add_argument("--muestras", type=int, default=0, help="usar solo las ultimas N muestras")
    s.set_defaults(func=cmd_seno)

    a = ap.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
