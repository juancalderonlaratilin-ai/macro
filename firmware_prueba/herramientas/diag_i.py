#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""diag_i.py - Pruebas automaticas del canal I de MACRO desde el PC (firmware_prueba).

Necesita:  pip install pyserial

  python diag_i.py --puerto COM5
  python diag_i.py --puerto COM5 --sin-manual      (no manda comandos a practica 2)
  python diag_i.py --puerto COM5 --consigna 3700   (firmware_prueba3: el numero de S:CONSIGNA)

Cierra antes la interfaz: el puerto COM solo lo puede abrir un programa a la vez.
Deja JP_AZEN en 2-3 y JP_AZ_I / JP_AZ_Q cerrados para las pruebas 5 y 6.

Pruebas (empiezan y terminan en REPOSO):
  1. Identificacion: P? y E? (E? solo existe en firmware_prueba).
  2. Reposo: como estan I y Q con los comandos en VREF_BUF.
  3. ADC interno (D:1): la ranura de I convierte AVSS (0 V) y la de Q el FVR a 1,024 V.
     Si sale I ~ 0 y Q ~ 2048, el ADC, la ISR y el orden "I,Q" de la linea estan bien.
  4. PWM en REPOSO (P:I y P:Q a 0 / 1023, y X:P,0): en REPOSO U4 entrega VREF_BUF a J3,
     asi que I no deberia moverse. Si se mueve con P:I, el PWM de I llega a la entrada del
     ADC de I (puente entre las patas 16 y 17 del PIC). Si se mueve con P:Q, el PWM de Q
     llega a la cadena de I sin pasar por U4. X:P,0 congela los dos PWM a la vez.
  5. MANUAL, barrido de I: A:1 y P:I de 0 a 1023 con Q fijo. Dice si I responde, en que
     sentido y donde cruza la consigna. Q sirve de control: no deberia moverse.
  6. MANUAL, barrido de Q: P:Q de 0 a 1023 con I en 512. Q tiene que responder (control
     de que MANUAL si saca los comandos a J3). Si I responde aqui, los comandos estan
     cruzados hacia practica 2.

Guarda todas las muestras en diag_i_<fecha>.csv (prueba, paso, comando, i, q) y el
resumen en diag_i_<fecha>.txt. Manda los dos si quieres que los revise.
"""
import argparse
import csv
import statistics
import sys
import time

CODIGO_CENTRO = 2048          # consigna del auto-cero (sec. 5.3); --consigna la cambia
CODIGO_FVR2 = 2048            # FVR buffer 2 a 1,024 V, lo que mide Q con D:1
CODIGO_MAX = 4095
UMBRAL_MOVIMIENTO = 60        # codigos: menos que esto se toma como "no se movio"
DUTY_NEUTRO = 512
BARRIDO = [0, 128, 256, 384, 512, 640, 768, 896, 1023]
T_ASENTAR_S = 0.5             # filtro de 5 Hz + practica 2: ~150 ms medidos el 20/11
T_MEDIR_S = 0.3               # 150 pares


def es_par(txt):
    """'IIII,QQQQ' -> (i, q); cualquier otra cosa -> None."""
    partes = txt.split(",")
    if len(partes) != 2 or not partes[0].isdigit() or not partes[1].isdigit():
        return None
    return int(partes[0]), int(partes[1])


class Pic:
    """Lee las lineas del PIC y separa datos de mensajes."""

    def __init__(self, ser, eco=True):
        self.ser = ser
        self.eco = eco
        self.mensajes = []

    def _mensaje(self, txt):
        self.mensajes.append(txt)
        if self.eco:
            print("      << " + txt)

    def _lineas(self, segundos):
        fin = time.monotonic() + segundos
        while time.monotonic() < fin:
            crudo = self.ser.readline()
            if not crudo:
                continue
            txt = crudo.decode("ascii", "replace").strip()
            if txt:
                yield txt

    def leer(self, segundos):
        pares = []
        for txt in self._lineas(segundos):
            p = es_par(txt)
            if p is None:
                self._mensaje(txt)
            else:
                pares.append(p)
        return pares

    def comando(self, cmd, espera_s=1.0):
        """Envia un comando y devuelve su respuesta (OK:, E:, P: o S:CNT), o None."""
        print("   >> " + cmd)
        self.ser.write((cmd + "\n").encode("ascii"))
        for txt in self._lineas(espera_s):
            if es_par(txt) is not None:
                continue
            self._mensaje(txt)
            if txt.startswith(("OK:", "E:", "P:", "S:CNT")):
                return txt
        return None


def resumen(pares, canal):
    vals = [p[0] if canal == "I" else p[1] for p in pares]
    if not vals:
        return None
    return {
        "med": int(statistics.median(vals)),
        "min": min(vals),
        "max": max(vals),
        "sat_alto": sum(1 for v in vals if v >= CODIGO_MAX - 7) / len(vals),
        "n": len(vals),
    }


class Registro:
    def __init__(self):
        self.filas = []
        self.lineas = []

    def muestras(self, prueba, paso, cmd, pares):
        for i, q in pares:
            self.filas.append((prueba, paso, cmd, i, q))

    def texto(self, s=""):
        print(s)
        self.lineas.append(s)


def medir(pic, reg, prueba, paso, cmd):
    pic.leer(T_ASENTAR_S)
    pares = pic.leer(T_MEDIR_S)
    reg.muestras(prueba, paso, cmd, pares)
    ri, rq = resumen(pares, "I"), resumen(pares, "Q")
    if ri is None:
        reg.texto(f"   {paso:<14} sin datos")
        return None, None
    reg.texto(f"   {paso:<14} I = {ri['med']:4d} ({ri['min']:4d}..{ri['max']:4d})"
              f"   Q = {rq['med']:4d} ({rq['min']:4d}..{rq['max']:4d})")
    return ri["med"], rq["med"]


def se_mueve(valores, base=None):
    vals = [v for v in valores if v is not None]
    if base is not None:
        vals = vals + [base]
    return bool(vals) and (max(vals) - min(vals)) > UMBRAL_MOVIMIENTO


def saturado(v):
    return v <= 7 or v >= CODIGO_MAX - 7


def analizar_barrido(puntos, canal):
    """puntos: [(duty, i, q)]. Devuelve un dict con responde, signo, cruza y texto."""
    vals = [(d, i if canal == "I" else q) for d, i, q in puntos if i is not None]
    r = {"responde": False, "signo": None, "cruza": False, "texto": f"{canal} no se mueve con su comando"}
    if not vals or not se_mueve([v for _, v in vals]):
        return r
    r["responde"] = True
    r["signo"] = +1 if vals[-1][1] < vals[0][1] else -1
    txt = (f"{canal} {'baja' if r['signo'] > 0 else 'sube'} al subir el duty: SIGNO_{canal} = "
           f"{'+1 (lo que supone el firmware)' if r['signo'] > 0 else '-1 (invertido)'}")
    for (d0, v0), (d1, v1) in zip(vals, vals[1:]):
        if (v0 - CODIGO_CENTRO) * (v1 - CODIGO_CENTRO) <= 0 and v0 != v1:
            r["cruza"] = True
            if saturado(v0) and saturado(v1):
                txt += f"; cruza {CODIGO_CENTRO} entre los duty {d0} y {d1}"
            else:
                txt += f"; cruza {CODIGO_CENTRO} cerca del duty {d0 + (CODIGO_CENTRO - v0) * (d1 - d0) / (v1 - v0):.0f}"
            break
    else:
        txt += f"; no cruza {CODIGO_CENTRO} en 0..1023 (fuera del rango del auto-cero)"
    lineales = [(d, v) for d, v in vals if not saturado(v)]
    if len(lineales) >= 2 and lineales[-1][0] != lineales[0][0]:
        (d0, v0), (d1, v1) = lineales[0], lineales[-1]
        txt += f"; pendiente ~{abs(v1 - v0) / (d1 - d0):.0f} codigos por paso"
    r["texto"] = txt
    return r


def abrir_puerto(nombre):
    import serial
    ser = serial.Serial(nombre, 115200, timeout=0.2)
    time.sleep(0.2)
    ser.reset_input_buffer()
    return ser


def ejecutar(ser, sin_manual=False, salida=None):
    pic = Pic(ser)
    reg = Registro()
    sello = time.strftime("%Y%m%d_%H%M%S")
    salida = salida or f"diag_i_{sello}"
    conclusiones = []
    duty_q_original = DUTY_NEUTRO

    try:
        # ------------------------------------------------------------ 1. identificacion
        reg.texto("1. Identificacion")
        pares = pic.leer(0.5)
        if len(pares) < 100:
            reg.texto(f"   Solo llegaron {len(pares)} lineas de datos en 0,5 s (se esperan ~250).")
            reg.texto("   Revisa el puerto, que la interfaz este cerrada y que el PIC este encendido.")
            return 1
        r = pic.comando("R")
        p = pic.comando("P?")
        e = pic.comando("E?")
        con_mensajes = p is not None
        es_prueba = e is not None and e.startswith("S:CNT")
        if p and p.startswith("P:I,"):
            try:
                duty_q_original = int(p.split(",")[3])
            except (IndexError, ValueError):
                pass
        if not con_mensajes:
            reg.texto("   El PIC no responde a P?: firmware sin mensajes (PROTO_MENSAJES = 0).")
            reg.texto("   Se sigue a ciegas; las pruebas 3 y 4 necesitan firmware_prueba.")
        elif not es_prueba:
            reg.texto("   Responde pero no conoce E?: no es firmware_prueba. Se saltan las pruebas 3 y 4.")
        else:
            reg.texto(f"   firmware_prueba con mensajes. {p}   {e}")
        if r is None and con_mensajes:
            reg.texto("   (R no confirmo; puede estar todavia en PREPARAR)")

        # ------------------------------------------------------------ 2. reposo
        reg.texto("")
        reg.texto("2. Reposo (comandos en VREF_BUF)")
        base_i, base_q = medir(pic, reg, "reposo", "reposo", "R")
        if base_i is None:
            return 1
        if base_i >= CODIGO_MAX - 7:
            reg.texto("   I saturado arriba: en RC0 hay 2,048 V o mas.")

        # ------------------------------------------------------------ 3. ADC interno
        adc_ok = None
        if es_prueba:
            reg.texto("")
            reg.texto("3. ADC con canales internos (D:1: I = AVSS, Q = FVR 1,024 V)")
            pic.comando("D:1")
            i_int, q_int = medir(pic, reg, "adc_interno", "D:1", "D:1")
            pic.comando("D:0")
            medir(pic, reg, "adc_interno", "D:0", "D:0")
            if i_int is not None:
                adc_ok = i_int <= 5 and abs(q_int - CODIGO_FVR2) <= 40
                if adc_ok:
                    reg.texto("   OK: el ADC, la ISR y el orden I,Q funcionan. El 4095 viene del pin RC0.")
                else:
                    reg.texto("   FALLA: la ranura de I no da 0 midiendo AVSS. Problema en el PIC o el firmware.")
                    conclusiones.append("El ADC no lee bien ni sus canales internos: revisar el PIC (cambiarlo) "
                                        "y adquisicion.c antes que el analogico.")

        # ------------------------------------------------------------ 4. PWM en reposo
        reposo_mueve = None
        fuga_q = False
        if es_prueba:
            reg.texto("")
            reg.texto("4. PWM en REPOSO (los comandos no salen a J3: I no deberia moverse)")
            vals_i, vals_q = [], []
            for d in (0, 1023, DUTY_NEUTRO):
                pic.comando(f"P:I,{d}")
                vals_i.append(medir(pic, reg, "pwm_reposo", f"P:I,{d}", f"P:I,{d}")[0])
            for d in (0, 1023, duty_q_original):
                pic.comando(f"P:Q,{d}")
                vals_q.append(medir(pic, reg, "pwm_reposo", f"P:Q,{d}", f"P:Q,{d}")[0])
            pic.comando("X:P,0")
            i_parado = medir(pic, reg, "pwm_reposo", "X:P,0", "X:P,0")[0]
            pic.comando("X:P,1")
            fuga_i = se_mueve(vals_i, base_i)
            fuga_q = se_mueve(vals_q, base_i)
            reposo_mueve = fuga_i or fuga_q
            if fuga_i:
                reg.texto("   I SE MUEVE con el PWM de I sin que el comando salga a J3.")
                conclusiones.append("El PWM de I llega directo a la entrada del ADC de I en Micro3: buscar un "
                                    "puente o pista en corto entre RA2 (pata 17, PWM_I) y RC0 (pata 16, ADC_I), "
                                    "o entre TP_PWM_I y TP_ADC_I.")
            if fuga_q:
                reg.texto("   I SE MUEVE con el PWM de Q en REPOSO, con U4 entregando VREF_BUF a J3.")
                conclusiones.append("El PWM de Q llega a la cadena de I SIN pasar por el selector U4: algun nodo "
                                    "de I esta unido a PWM_Q_BUF (TP_PWM_Q, U4.1 o salida de U3D). Busca con "
                                    "P:Q,0 / P:Q,1023 en REPOSO cual punto de I sigue a TP_PWM_Q.")
            if not reposo_mueve:
                if se_mueve([i_parado], base_i):
                    reg.texto("   Solo X:P,0 mueve I (congela PWM_I y PWM_Q a la vez): repetir mirando TP_PWM_Q.")
                else:
                    reg.texto("   OK: ningun PWM se acopla a I en REPOSO.")

        # ------------------------------------------------------------ 5 y 6. MANUAL
        if not sin_manual:
            reg.texto("")
            reg.texto(f"5. MANUAL, barrido de I (Q fijo en {duty_q_original})")
            a = pic.comando("A:1")
            if con_mensajes and (a is None or not a.startswith("OK:A,1")):
                reg.texto(f"   No entro a MANUAL ({a}). Se saltan 5 y 6.")
            else:
                pic.comando(f"P:Q,{duty_q_original}")
                puntos_i = []
                for d in BARRIDO:
                    pic.comando(f"P:I,{d}")
                    i, q = medir(pic, reg, "barrido_I", f"P:I,{d}", f"P:I,{d}")
                    puntos_i.append((d, i, q))
                pic.comando(f"P:I,{DUTY_NEUTRO}")

                reg.texto("")
                reg.texto(f"6. MANUAL, barrido de Q (I fijo en {DUTY_NEUTRO})")
                puntos_q = []
                for d in BARRIDO:
                    pic.comando(f"P:Q,{d}")
                    i, q = medir(pic, reg, "barrido_Q", f"P:Q,{d}", f"P:Q,{d}")
                    puntos_q.append((d, i, q))
                pic.comando(f"P:Q,{duty_q_original}")
                pic.comando("A:0")

                ai = analizar_barrido(puntos_i, "I")
                aq = analizar_barrido(puntos_q, "Q")
                i_con_q = se_mueve([x[1] for x in puntos_q])
                q_con_i = se_mueve([x[2] for x in puntos_i])
                reg.texto("")
                reg.texto("   " + ai["texto"])
                reg.texto("   " + aq["texto"])
                if i_con_q:
                    reg.texto("   I se mueve con el comando de Q.")
                if q_con_i:
                    reg.texto("   Q se mueve con el comando de I.")

                if fuga_q and i_con_q and not ai["responde"]:
                    conclusiones.append("En MANUAL I sigue al comando de Q y no al suyo: es la misma fuga. I "
                                        "recibe el comando de Q en vez de I0.")
                elif reposo_mueve:
                    conclusiones.append("En MANUAL I tambien se mueve, pero puede ser por el mismo acople del "
                                        "PWM: corrige primero eso y repite.")
                elif not aq["responde"]:
                    conclusiones.append("Q tampoco respondio en MANUAL: los comandos no estan saliendo a J3. "
                                        "Revisar JP_AZEN en 2-3, RC2 (EN_AZ_PIC) en alto durante MANUAL y U4. "
                                        "Con eso la prueba de I no es concluyente.")
                elif ai["responde"] and ai["signo"] < 0:
                    conclusiones.append("I SI responde a su comando, pero con el signo al reves: " + ai["texto"] +
                                        ". Por eso el auto-cero lo lleva a 1023. Mandame el CSV para confirmar "
                                        "SIGNO_I = -1 (V8) antes de cambiarlo en el firmware.")
                elif ai["responde"] and not ai["cruza"]:
                    conclusiones.append(f"I SI responde a su comando pero no llega a {CODIGO_CENTRO} en todo el rango: " +
                                        ai["texto"] + ". Falta rango de comando o hay un offset grande en "
                                        "practica 2 para I.")
                elif ai["responde"]:
                    conclusiones.append("I responde bien en MANUAL: " + ai["texto"] + ". Repite el auto-cero "
                                        "con SW2 y mandame la traza S:AZ si vuelve a fallar.")
                elif i_con_q and q_con_i:
                    conclusiones.append("I responde al comando de Q y Q al de I: los comandos I0 y Q0 llegan "
                                        "cruzados a practica 2 (J3 o el cable).")
                elif i_con_q:
                    conclusiones.append("I responde al comando de Q y no al suyo: el restador de I recibe Q0. "
                                        "Revisar el cableado J3 -> practica 2.")
                else:
                    adc_txt = ("el ADC esta bien" if adc_ok else
                               "el ADC no se probo (falta firmware_prueba: corre otra vez con ese firmware)")
                    conclusiones.append("Ningun comando mueve I, Q si responde y " + adc_txt + ": la entrada del "
                                        "ADC de I esta fija por algo fuera del lazo del auto-cero. Siguiente "
                                        "medida: con SW1 apretado (PIC en reset, pines en alta impedancia) mide "
                                        "TP_ADC_I. Si sigue en VCC, el PIC no es quien la sube: desconecta J2 y "
                                        "mide J2.2 del lado de Micro3 y del lado de practica 2.")
        else:
            reg.texto("")
            reg.texto("5 y 6 saltadas (--sin-manual).")

        if not conclusiones:
            if adc_ok and reposo_mueve is False:
                conclusiones.append("El ADC y el PWM de I estan bien. Corre sin --sin-manual para probar el lazo.")
            else:
                conclusiones.append("Sin conclusion: revisa los mensajes de arriba.")

        reg.texto("")
        reg.texto("CONCLUSION")
        for c in conclusiones:
            reg.texto(" - " + c)
        return 0

    finally:
        try:
            pic.eco = False
            pic.comando("R", 0.5)
            pic.comando("D:0", 0.5)
            pic.comando("X:P,1", 0.5)
            pic.comando(f"P:I,{DUTY_NEUTRO}", 0.5)
            pic.comando(f"P:Q,{duty_q_original}", 0.5)
        except Exception:
            pass
        with open(salida + ".csv", "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["prueba", "paso", "comando", "i", "q"])
            w.writerows(reg.filas)
        with open(salida + ".txt", "w", encoding="utf-8") as f:
            f.write("\n".join(reg.lineas) + "\n")
            f.write("\nMensajes del PIC:\n" + "\n".join(pic.mensajes) + "\n")
        print(f"\nGuardado: {salida}.csv y {salida}.txt")


def main():
    ap = argparse.ArgumentParser(description="Pruebas del canal I de MACRO (firmware_prueba).")
    ap.add_argument("--puerto", required=True, help="COM5, /dev/ttyUSB0, ...")
    ap.add_argument("--sin-manual", action="store_true", help="no pasar a MANUAL (no saca comandos a J3)")
    ap.add_argument("--salida", help="nombre base de los archivos (sin extension)")
    ap.add_argument("--consigna", type=int, default=2048,
                    help="codigo al que centra el auto-cero (2048; en firmware_prueba3 el de S:CONSIGNA)")
    a = ap.parse_args()
    global CODIGO_CENTRO
    CODIGO_CENTRO = a.consigna
    try:
        ser = abrir_puerto(a.puerto)
    except Exception as ex:
        print(f"No pude abrir {a.puerto}: {ex}")
        print("Cierra la interfaz (o cualquier programa que use el puerto) y prueba otra vez.")
        return 1
    try:
        return ejecutar(ser, a.sin_manual, a.salida)
    finally:
        ser.close()


if __name__ == "__main__":
    sys.exit(main())
