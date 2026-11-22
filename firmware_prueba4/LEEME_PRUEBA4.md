# firmware_prueba4: ADC referido a VDD

Copia de `firmware_prueba3` del 21/11/2026. **El único cambio es la referencia del ADC: VDD en lugar del FVR de 2,048 V.** Esto rompe a propósito la regla 2 del proyecto ("nunca usar VDD como referencia") y vale solo para esta copia de prueba. El firmware de entrega (`firmware/`) sigue con el FVR.

En MPLAB X se abre como `MACRO_Firmware_prueba4` (*File → Open Project → firmware_prueba4/MACRO_Firmware4.X*). Antes hay que copiar el `Makefile` de la raíz del proyecto desde `firmware_prueba3/MACRO_Firmware3.X/`. Después: *Clean and Build* y grabar.

## Qué se gana y qué se pierde

| | FVR (prueba, prueba3) | VDD (prueba4) |
|---|---|---|
| Escala del ADC | 0 a 2,048 V | 0 a VDD (≈ 3,70 V) |
| 1 LSB | 0,50 mV | ≈ 0,90 mV |
| Centro (código 2048) | 1,024 V | VDD/2 ≈ 1,85 V |
| Rango alrededor de 1,85 V | +0,2 V / −1,85 V | ±1,85 V |
| La medida depende de | el FVR (estable) | el valor y el ruido de VDD |

Con el mismo ruido en voltios, el SINAD de una senoidal de escala completa sale unos 5 dB mejor que con el FVR, porque la escala es 1,8 veces más grande. No es que haya menos ruido. Cualquier ruido o rizado de VDD entra directo en la medida.

## La consigna

Es la misma fórmula de `firmware_prueba3`, ahora con VDD:

```
consigna = redondear(4096 × V_objetivo / VDD)
```

| VDD | Consigna para 1,850 V |
|---|---|
| 3700 mV (nominal) | 2048 |
| 3667 mV | 2066 |

El PIC no mide su propio VDD: usa la constante `AZ_VDD_MV` de `autocero.h` (3700). **Mide VDD con el multímetro y ponlo ahí.** Si quieres el centro exacto de la escala (VDD/2), basta con dejar `AZ_V_OBJETIVO_MV` = `AZ_VDD_MV` / 2.

## Qué cambió en el código

| Archivo | Cambio |
|---|---|
| `adquisicion.h/.c` | `adq_iniciar()` pone `ADREF` = 0x00 (VDD/VSS) antes del primer disparo. MCC sigue dejando 0x03; no se tocó ningún archivo de MCC |
| `autocero.h/.c` | `AZ_VDD_MV` y la fórmula con VDD. Un paso de duty ahora mueve G códigos (antes 1,807 × G): `TOL_AZ` pasa de 46 a 30 códigos, que en voltios es casi lo mismo (27 mV contra 23 mV) |
| `fsm.c` | Al arrancar envía `S:MACRO,VDD=3700` en lugar de `S:MACRO,FVR=…` y aplica la consigna |
| `protocolo.c/.h` | Mensaje `S:MACRO,VDD=<mV>` |
| `nbproject/` | Proyecto `MACRO_Firmware_prueba4` en `MACRO_Firmware4.X`, con otro UUID |

Los umbrales de saturación siguen en ≤ 7 y ≥ 4088 códigos. Todo lo demás es igual a `firmware_prueba3`: `S:AZ`, resultado retenido, SW2 como stop, `D:`, `X:` y `E?`.

## En el PC

- **Interfaz** (`herramientas/interfaz_macro.py`): con el mensaje `S:MACRO,VDD=…` convierte a voltios con VDD. Si conectas la interfaz después de que el PIC arrancó, ese mensaje ya pasó. En ese caso, presiona SW1 (reset) o elige «VDD 3700 mV» en *Ref. ADC* (se puede escribir el valor medido, por ejemplo «VDD 3667 mV»).
- **`diag_i.py`**: `python diag_i.py --puerto COM5 --ref-mv 3700`. Con `D:1`, Q mide el FVR a 1,024 V y da unos 1134 códigos con VDD = 3,70 V. De ahí también se puede despejar VDD: VDD ≈ 4194 / código (en V).
