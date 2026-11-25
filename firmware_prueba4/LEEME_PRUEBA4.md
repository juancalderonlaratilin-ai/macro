# firmware_prueba4: ADC referido a VDD

Copia de `firmware_prueba3` del 21/11/2026. **Cambia dos cosas: la referencia del ADC pasa a VDD en lugar del FVR de 2,048 V, y desde el 23/11 la bomba de carga del ADC queda encendida al iniciar** (ver «Bomba de carga del ADC»). Lo primero rompe a propósito la regla 2 del proyecto ("nunca usar VDD como referencia") y vale solo para esta copia de prueba. El firmware de entrega (`firmware/`) sigue con el FVR y sin bomba de carga.

En MPLAB X se abre como `MACRO_Firmware_prueba4` (*File → Open Project → firmware_prueba4/MACRO_Firmware4.X*). Antes hay que copiar el `Makefile` de la raíz del proyecto desde `firmware_prueba3/MACRO_Firmware3.X/`. Después: *Clean and Build* y grabar.

Para volver a generar el código de MCC sin perder las correcciones a mano (`eusart1.*`, `interrupt_manager.c`), seguir la guía [MACRO prueba4: guía para regenerar MCC por periférico](https://claude.ai/artifact/PAL7jQgnrnKqEdAo8cNiad) (24/11/2026). Con ella MCC queda en referencia VDD y *setpoint*, igual que lo que corre.

## Qué se gana y qué se pierde

| | FVR (prueba, prueba3) | VDD (prueba4) |
|---|---|---|
| Escala del ADC | 0 a 2,048 V | 0 a VDD (≈ 3,70 V) |
| 1 LSB | 0,50 mV | ≈ 0,90 mV |
| Centro (código 2048) | 1,024 V | VDD/2 ≈ 1,85 V |
| Rango alrededor de 1,85 V | +0,2 V / −1,85 V | ±1,85 V |
| La medida depende de | el FVR (estable) | el valor y el ruido de VDD |

Con el mismo ruido en voltios, el SINAD de una senoidal de escala completa sale unos 5 dB mejor que con el FVR, porque la escala es 1,8 veces más grande. No es que haya menos ruido. Cualquier ruido o rizado de VDD entra directo en la medida.

## La consigna (24/11/2026: fija en 2048)

Con VDD como referencia la consigna es **2048 fija** (`AZ_CONSIGNA` en `autocero.h`), el mismo `ADSTPT` que deja MCC. Ya no se calcula `4096 × V_objetivo / VDD` como en `firmware_prueba3`.

Por qué no hace falta la cuenta: el código 2048 es VDD/2, y Vref2 de práctica 2 (`VREF_BUF`) también es VDD/2. Las dos siguen al mismo riel, así que el reposo cae en 2048 con cualquier VDD (es la cancelación ratiométrica de §5.0). La fórmula anterior daba 2048 con 3700 mV y se movía (2066 con 3667 mV) solo porque mezclaba un objetivo fijo en voltios con una escala que depende de VDD.

`ADQ_VDD_MV` (en `adquisicion.h`, 3700) **ya no entra en ninguna cuenta del PIC.** Solo viaja en `S:MACRO,VDD=<mV>` para que el PC pase de códigos a voltios. Mide VDD con el multímetro y ponlo ahí para que la escala en voltios sea exacta. El auto-cero no depende de ese valor.

Al arrancar sale `S:CONSIGNA,2048,1850`: el segundo número es `ADQ_VDD_MV` / 2, constante de compilación.

## Qué cambió en el código

| Archivo | Cambio |
|---|---|
| `adquisicion.h/.c` | `adq_iniciar()` pone `ADREF` = 0x00 (VDD/VSS) antes del primer disparo. MCC sigue dejando 0x03; no se tocó ningún archivo de MCC |
| `adquisicion.h/.c` (23/11) | `adq_iniciar()` enciende la bomba de carga del ADC (`ADCPCON0.CPON` = 1) si `ADQ_BOMBA_CARGA` = 1. Tampoco toca archivos de MCC |
| `autocero.h/.c` | Un paso de duty ahora mueve G códigos (antes 1,807 × G): `TOL_AZ` pasa de 46 a 30 códigos, que en voltios es casi lo mismo (27 mV contra 23 mV) |
| `autocero.h/.c` (24/11) | Se quitan `az_calcular_consigna()` (la cuenta 4096 × V_objetivo / VDD), `az_fijar_consigna()`, `az_consigna()` y las constantes `AZ_V_OBJETIVO_MV`, `AZ_VDD_MV`, `AZ_VREF_MIN/MAX_MV`, `AZ_VDD_NOMINAL_MV`, `AZ_CODIGO_SAT_*` y `AZ_CONSIGNA_MIN/MAX`. Queda `AZ_CONSIGNA` = 2048 |
| `adquisicion.h` (24/11) | `ADQ_VDD_MV` (antes `AZ_VDD_MV`): solo para el mensaje `S:MACRO,VDD=` |
| `fsm.c` | Al arrancar envía `S:MACRO,VDD=3700` en lugar de `S:MACRO,FVR=…`. Desde el 24/11 aplica `AZ_CONSIGNA` sin calcularla; `adq_fijar_consigna(2048)` vuelve a escribir los mismos `ADSTPT`, `ADLTH` y `ADUTH` de MCC |
| `protocolo.c/.h` | Mensaje `S:MACRO,VDD=<mV>` |
| `nbproject/` | Proyecto `MACRO_Firmware_prueba4` en `MACRO_Firmware4.X`, con otro UUID |

Los umbrales de saturación siguen en ≤ 7 y ≥ 4088 códigos. Todo lo demás es igual a `firmware_prueba3`: `S:AZ`, resultado retenido, SW2 como stop, `D:`, `X:` y `E?`.

## Bomba de carga del ADC (23/11/2026)

El ADCC tiene una bomba de carga propia (registro `ADCPCON0`, DS40001985 §32.4). Mantiene fija la tensión de compuerta de los interruptores de entrada de la señal y de la referencia, para que no se degraden a baja tensión. Tras el reset está apagada, MCC no la toca y la especificación no la menciona.

| | Valor |
|---|---|
| Dónde se enciende | `adq_iniciar()` en `adquisicion.c`, justo después de `ADREF`, antes del primer disparo de Timer4 |
| Constante | `ADQ_BOMBA_CARGA` en `adquisicion.h`: **1 = encendida** (así queda), 0 = apagada como en el reset |
| Espera | Ninguna (regla 8). `CPRDY` avisa cuando la bomba está lista; las conversiones de los primeros milisegundos no se usan en las mediciones |
| Cómo comprobarlo | Con el depurador, `ADCPCON0` (0x29F) debe leer **0x81** con el ADC funcionando: `CPON` = 1 y `CPRDY` = 1 |

Por qué se prueba: con VDD como referencia el ruido ya era de cuantización (0,22–0,42 LSB) con la bomba apagada. Con el FVR, que queda a mitad de VDD, el ruido crecía con el código (0,21 % rms). La bomba alimenta también el interruptor de la referencia. Si ese interruptor fuera la causa, la bomba debería bajar el ruido con el FVR.

**Ojo:** esta copia usa VDD. Para probar la hipótesis del FVR hace falta FVR + bomba (por ejemplo, la misma línea en `firmware_prueba3`). Con VDD + bomba solo se comprueba que la bomba no empeora nada: repetir la continua a 0,25, 1,85 y 3,55 V y comparar con 0,41 / 0,22 / 0,42 LSB.

Para volver al comportamiento anterior basta con poner `ADQ_BOMBA_CARGA` en 0 y compilar.

## En el PC

- **Interfaz** (`herramientas/interfaz_macro.py`): con el mensaje `S:MACRO,VDD=…` convierte a voltios con VDD. Si conectas la interfaz después de que el PIC arrancó, ese mensaje ya pasó. En ese caso, presiona SW1 (reset) o elige «VDD 3700 mV» en *Ref. ADC* (se puede escribir el valor medido, por ejemplo «VDD 3667 mV»).
- **`diag_i.py`**: `python diag_i.py --puerto COM5 --ref-mv 3700`. Con `D:1`, Q mide el FVR a 1,024 V y da unos 1134 códigos con VDD = 3,70 V. De ahí también se puede despejar VDD: VDD ≈ 4194 / código (en V).
