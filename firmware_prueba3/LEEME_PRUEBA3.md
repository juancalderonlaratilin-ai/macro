# firmware_prueba3: auto-cero centrado en 1,85 V

Copia de `firmware_prueba` del 20/11/2026, con los mensajes `S:AZ`, el resultado retenido y SW2 como stop. **El único cambio es la consigna del auto-cero.** La especificación (§5.3) la fija en el código 2048 = 1,024 V, el centro de la escala del FVR. Esta copia lleva I y Q a la tensión que se pone en `autocero.h`, por defecto **1,85 V** (Vref2 de práctica 2).

La referencia del ADC sigue siendo el **FVR de 2,048 V** (regla 2). No se tocó ningún archivo de MCC.

En MPLAB X se abre como un proyecto aparte, `MACRO_Firmware_prueba3` (*File → Open Project → firmware_prueba3/MACRO_Firmware.X*). Después: *Clean and Build* y grabar.

## La fórmula

Al arrancar, el PIC lee el FVR real de su calibración de fábrica (FVRA2X, en mV) y calcula:

```
consigna = redondear(4096 × V_objetivo / FVR_real)
```

| FVR_real | Consigna para 1,850 V |
|---|---|
| 2048 mV (nominal) | 3700 |
| 2100 mV | 3608 |
| 1966 mV (−4 %) | 3854 |
| 2130 mV (+4 %) | 3558 |

Si FVRA2X da un valor fuera de 1966–2130 mV, que no es creíble, usa 2048 mV.

Al arrancar el PIC envía:

```
S:MACRO,FVR=2048
S:CONSIGNA,3700,1850     <- código al que va a centrar y tensión objetivo en mV
S:DIAG
S:REPOSO
```

## Qué cambió en el código

| Archivo | Cambio |
|---|---|
| `autocero.h/.c` | `AZ_V_OBJETIVO_MV` (1850) y `az_calcular_consigna()` con la fórmula. La búsqueda compara contra la consigna calculada en lugar de 2048 |
| `adquisicion.h/.c` | `adq_fijar_consigna()`: pone `ADSTPT` = consigna y recalcula los umbrales de saturación, que el ADC mide como diferencia contra `ADSTPT`. Con consigna 3700 quedan `ADLTH` = −3692 y `ADUTH` = 387, así la saturación sigue siendo ≤ 7 y ≥ 4088 códigos. Con 2048 da lo mismo que MCC |
| `fsm.c` | En PREPARAR calcula la consigna, la aplica al ADC y la avisa. Los residuos de VALIDAR y `S:MEDIR` se miden contra ella |
| `protocolo.c/.h` | Mensaje `S:CONSIGNA,<códigos>,<mV>` |
| `nbproject/project.xml` | Nombre `MACRO_Firmware_prueba3` y otro UUID, para no confundirlo con `firmware_prueba` en MPLAB |

Todo lo demás queda igual que en `firmware_prueba`: comandos `D:`, `X:`, `B`, `E?`, `S:AZ`, `PRUEBA_RETENER_RESULTADO` y `PRUEBA_SW2_PARA`.

## Para cambiar el objetivo

Edita `AZ_V_OBJETIVO_MV` en `autocero.h`, por ejemplo con la Vref2 medida en práctica 2, y recompila. La consigna queda acotada a 54–4041 códigos para que la ventana de VALIDAR (±`TOL_AZ`) no toque la saturación.

## Lo que cuesta

La escala del ADC termina en el FVR real (≈ 2,048 V). Con el objetivo en 1,85 V quedan:

- **hacia arriba: ≈ 0,2 V** (unos 390 códigos antes de la saturación, con FVR nominal);
- hacia abajo: 1,85 V.

Una señal que suba más de ~0,2 V sobre el reposo se recorta en 4095 y dispara `SAT_I`/`SAT_Q` en MEDIR. Para tener 1,85 V al centro con rango simétrico habría que referir el ADC a VDD (rompe la regla 2) o desplazar el nivel por hardware.

## Herramienta de diagnóstico

`firmware_prueba/herramientas/diag_i.py` acepta la consigna para medir los cruces contra ella:

```
python diag_i.py --puerto COM5 --consigna 3700
```

Usa el número que salga en `S:CONSIGNA`.
