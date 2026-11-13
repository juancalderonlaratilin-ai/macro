# firmware_prueba: copia de diagnóstico de MACRO

Copia de `firmware/MACRO_Firmware.X` del 13/11/2026 con comandos extra para localizar el origen del ruido. **No es la versión de entrega.** El original no se tocó.

La carpeta se llama `firmware_prueba` (con guion bajo) porque MPLAB X y `make` fallan a menudo con espacios en la ruta.

**Estado: sin compilar con XC8.** La lógica nueva se probó en el PC con gcc y un simulador de los periféricos (comandos, ráfaga, flujo), pero el primer *Clean and Build* en MPLAB X es tuyo. Si XC8 da un error, pásame el mensaje.

## Qué cambia frente al original

Todo lo nuevo está marcado con `[PRUEBA]` en el código. No se agregó ningún archivo, así que el proyecto abre igual. **No pulses Generate en MCC.**

| Archivo | Cambio |
|---|---|
| `mcc_generated_files/adcc.c` | `ADCON3` pasa de `0x24` a `0x14` (corrección real, ver abajo) |
| `adquisicion.c/.h` | Los dos canales que alterna la ISR son variables (antes constantes). Marcador de RC7 apagable |
| `protocolo.c/.h` | Comandos `D:`, `X:`, `B`, `E?`. Ráfaga de 256 pares en RAM. Contador de TXOVR |
| `fsm.c/.h` | Ejecuta `D:` y `X:` solo en REPOSO. Bloquea el auto-cero mientras haya un diagnóstico activo. Envía `S:DIAG` al arrancar |
| `main.c` | Llama a `proto_par` y `proto_diag_bombear` |

Se mantienen las reglas: el disparo sigue siendo de Timer4 por hardware, nunca se escribe `ADGO`, la referencia sigue siendo FVR 2,048 V, no hay esperas bloqueantes ni promedio.

Memoria: unas 1 340 de 2 048 bytes de RAM (1 024 son la ráfaga).

## Comandos nuevos (terminados en `\n`, solo en REPOSO)

| Comando | Qué hace | Respuesta |
|---|---|---|
| `D:1` | El ADC deja los pines y mide dos canales **internos**: I = AVSS (0 V), Q = FVR buffer 2 a 1,024 V (código ≈ 2048) | `OK:D,1` |
| `D:0` | Vuelve a ANC0 / ANC1 | `OK:D,0` |
| `X:P,0` / `X:P,1` | Para / arranca Timer2: sin portadora de 15,625 kHz en RA2 y RA4 | `OK:X` |
| `X:C,0` / `X:C,1` | Apaga / enciende el reloj de 1 kHz en RC6 (CCP1) | `OK:X` |
| `X:M,0` / `X:M,1` | Apaga / enciende el pulso de RC7 en la ISR | `OK:X` |
| `X:L,0` / `X:L,1` | Apaga / enciende el LED | `OK:X` |
| `X:T,0` / `X:T,1` | Apaga / enciende las líneas de datos | `OK:X` |
| `B` | Ráfaga: la UART calla 100 ms, se guardan 256 pares (0,512 s) en RAM **sin transmitir nada** y después se envían entre `S:RAFAGA,256` y `S:FIN` | `OK:B` |
| `E?` | Contadores desde el arranque: pares que main no alcanzó a leer, pares mal formados, líneas perdidas por FIFO llena | `S:CNT,a,b,c` |

Con `D:1` o `X:P,0` activos, `Z`, SW2 y `A:1` responden `E:estado`: primero `D:0` y `X:P,1`. Un reset deja todo normal.

Con `D:1` la columna I vale 0 o 1 (está pegada al fondo de escala, no dice nada del ruido). **La que importa es Q.** El primer par tras `D:0`/`D:1` puede salir mezclado.

## Herramienta del PC

`herramientas/diag_sinad.py` (necesita `numpy`; `pyserial` solo para capturar):

```
python diag_sinad.py capturar --puerto COM5 --segundos 20 --salida q_dc.csv
python diag_sinad.py capturar --puerto COM5 --segundos 20 --salida interno.csv --cmd D:1
python diag_sinad.py capturar --puerto COM5 --rafaga --salida silencio.csv
python diag_sinad.py ruido q_dc.csv
python diag_sinad.py seno i_200hz.csv --canal I
```

- `ruido`: σ por canal y de qué está hecho el ruido: tonos de 60/120/180 Hz (red), 125/250 Hz (alias del PWM), deriva, o blanco. También la correlación entre I y Q.
- `seno`: ajusta la senoidal (no necesita muestreo coherente), da SINAD y separa el error en **ruido aditivo** y **error de tiempo**, y busca líneas perdidas.
- También lee los CSV de la interfaz: toma las dos últimas columnas numéricas como I y Q.

## Orden de pruebas

Montaje base: JP_IN 2–3, JP_ADC 2–3 (bypass), JP_AZEN 1–2, estado REPOSO. Anota σ de Q en cada paso.

| # | Prueba | Si σ baja a ~1–2 LSB | Si σ sigue en ~12 LSB |
|---|---|---|---|
| 1 | `D:1` (canales internos) | El chip está bien: el ruido entra por el pin → pasos 2–4 | El ruido es interno (FVR, VDD del PIC o digital) → pasos 5–6 |
| 2 | Pila AA (≈1,5 V) entre TEST_Q y GND de J7, cables cortos; Keysight, generador y osciloscopio **desconectados**; portátil con batería (cargador desenchufado) | Era el banco. Reconecta de a uno (cargador, osciloscopio, generador, Keysight) hasta que vuelva el ruido | El ruido se acopla dentro de la placa |
| 3 | Lo mismo con TEST_Q unido a GND en J7 (0 V) | — | — (compara con el paso 2: si el ruido crece con el código, viene de la referencia o de la fuente) |
| 4 | `ruido` sobre la captura original con la Keysight | — | Mira los tonos: 60 Hz = lazo de tierra; blanco = ruido de banda ancha plegado |
| 5 | `X:P,0`, luego `X:C,0`, `X:L,0`, `X:M,0`, de a uno | Ese periférico se acopla a la entrada | — |
| 6 | `B` (ráfaga en silencio) contra una captura normal | La actividad de TX (U5, CP2102, corriente por GND del USB) mete el ruido | — |
| 7 | Con el ruido ya resuelto: `seno` a 5, 20 y 200 Hz | — | Si domina el error de tiempo, ver el hallazgo 5 |

## Hallazgos de la revisión que no dependen del banco

1. **`ADCON3 = 0x24` está mal en el original** (la especificación §6.4 pide «Actual result vs setpoint», `ADCALC` = 001 → `0x14`). Con `0x24` el error se calcula contra `ADFLTR`, que en modo básico vale 0, así que `ADERR = ADRES` y `ADTIF` se activa con **cualquier código > 2039**. No afecta al SINAD, pero en MEDIR daría `S:ALARMA,SAT_I`/`SAT_Q` falsas justo alrededor de la consigna 2048. Corregir en MCC (ADCC → Error calculation mode) o a mano en `adcc.c`.
2. **El PMD no quedó como dice §6.13.** `PMD0 = 0x01` deja CLKR **habilitado** (para deshabilitarlo sería `0x03`), `PMD3 = 0x02` deja DAC1, CMP2 y ZCD habilitados (`0x47` los apaga y conserva el ADC) y `PMD7 = 0x00` deja CLC1–4, DSM y SMT1. No explica el ruido: esos módulos no están en uso.
3. **`ADACQ` no actúa, y no hace falta.** El retardo de 39 µs = 28,5 µs de conversión + ~10 µs de entrada a la ISR, igual con 640 que con 1280. Como la ISR deja `ADPCH` en el canal siguiente 930 µs antes del disparo, `CHOLD` sigue al pin todo ese tiempo y la muestra se toma en el disparo. Tu V5 (0,0014 LSB) lo confirma. Se puede devolver a 640.
4. **El ADC en bypass no tiene filtro anti-aliasing.** R38/C32 corta en 15,9 kHz; todo el ruido de la fuente hasta decenas de kHz se pliega entero a 0–250 Hz. 200 mV pico a pico de ruido de conmutación a ~100 kHz dejan unos 30 mV pico a pico en el pin, del orden de los 6 mV rms medidos.
5. **La caída del SINAD por encima de 100 Hz tiene forma de error de tiempo, no de ruido de tensión.** Un ruido de 12 LSB da ~41 dB planos a cualquier frecuencia. Bajar a 28–30 dB en 200 Hz equivale a un error de tiempo de 20–30 µs rms (`SINAD = −20·log10(2π·f·σt)`: 25 µs → 30 dB a 200 Hz, 36 dB a 100 Hz, 50 dB a 20 Hz). Es una hipótesis: `seno` lo mide directamente. Candidatos: líneas perdidas en el PC, un generador con fase inestable (los analógicos lo son) o la deriva de fase del HFINTOSC, que §8.5 dio por despreciable considerando solo el jitter ciclo a ciclo. Si resulta ser el oscilador, limita el SINAD a 20 Hz a ~50 dB y habría que revisar ese criterio.
