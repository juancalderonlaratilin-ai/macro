# MACRO: prompt maestro para el agente

Proyecto MACRO, la evolución de Micro 3. Firmware para un **PIC16F18446-I/P (20 pines)** montado en la PCB de Micro 3. Adquiere I y Q desde la práctica 2, hace el auto-cero con PWM y envía los datos al PC por UART.

## Fuente de verdad

`docs/MACRO_especificacion_diseno.md` manda sobre cualquier otra cosa, incluido el código y los documentos de Micro 3. Si algo no está ahí o se contradice, **pregunta antes de decidir**. Secciones clave:

| Necesitas | Sección |
|---|---|
| Valores clave en una tabla | §0 |
| Pines (extraídos de la PCB) | §3 |
| Arquitectura de adquisición por hardware | §4 |
| FVR y fórmula del duty | §5 (5.5) |
| Configuración de MCC por módulo | §6 |
| ISR, máquina de estados, auto-cero, protocolo | §7 |
| SINAD y plano de impedancias | §9, §10 |
| Pruebas de banco V1–V12 | §11 |
| Supuestos aún sin confirmar | §13 |

## Reglas que no se rompen

1. **Adquisición 100 % por hardware.** `ADACT` = TMR4. El software **nunca** escribe `ADGO` ni hace polling de la conversión.
2. **Referencia del ADC = FVR 2,048 V.** `ADREF` = 0x03 y `FVRCON` = 0x82. Hay que esperar `FVRRDY` antes de arrancar Timer4. Nunca usar VDD como referencia.
3. **Sin watchdog** (`WDTE = OFF`). **Sin promedio de muestras.** ADCC en modo básico, sin Accumulate, Average ni Burst.
4. **Muestreo: 500 I + 500 Q por segundo.** Timer4 dispara cada 1 ms alternando canal: I = ANC0/RC0 (`ADPCH` 0x10), Q = ANC1/RC1 (0x11).
5. **UART:** 115 200 8N1, una línea `IIII,QQQQ\r\n` por par (500 líneas/s). Los mensajes empiezan con `S:`, `OK:` o `E:`. No usar `printf`, `sprintf` ni `scanf`: el formato ASCII se hace con una rutina propia.
6. **Solo se reutiliza `eusart1.c` / `eusart1.h` de Micro 3.** No copiar `adc_iq`, `adc_ascii`, `pwm`, `main`, `pin_manager` ni otros archivos de MCC del PIC16F18426.
7. **Después de reemplazar `eusart1.*` no se vuelve a pulsar Generate en MCC.** Todo cambio en archivos generados por MCC se anota en `docs/revision_codigo_mcc.md`.
8. **Sin esperas bloqueantes.** Los tiempos se miden con el tick de Timer6 (10 ms) dentro de la máquina de estados.
9. **Una sola ISR.** Orden de atención: RX → ADI → TX → TMR6. Cada rama comprueba la habilitación **y** la bandera.
10. **La ISR ADI solo:**
    - identifica el canal leyendo `ADPCH`;
    - copia `ADRES`;
    - lee y borra `ADTIF`;
    - escribe en `ADPCH` el otro canal;
    - al terminar Q, publica el par.

    Nada más: ni formato ni lógica de estados.
11. **`EN_AZ_PIC` (RC2) arranca en 0.** Solo vale 1 en MANUAL, HABILITAR, CALIBRAR, VALIDAR, MEDIR y ALARMA. En FALLO y REPOSO vuelve a 0 (§7.3).
12. **Chip de 20 pines.** RX1 se asigna a mano a RC5 (`RX1PPS` = 0x15) porque por defecto está en RB5. TX1 va en RC4 (`RC4PPS` = 0x0F).

## Reparto del trabajo

- **El equipo** configura MCC siguiendo §6, pulsa Generate una vez y reemplaza `eusart1.*` (§6.10).
- **El agente** escribe el firmware propio en archivos aparte de `mcc_generated_files/`. Sugerencia: `adquisicion.*`, `fsm.*`, `autocero.*`, `protocolo.*`, `ascii.*` y `main.c`.
- Antes de cambiar algo, lee la sección del documento que aplica. Después, compila si es posible y resume qué cambió y por qué.
- No inventes valores que §13 marca como pendientes (unidad de `ADACQ`, G y `SIGNO_x`, umbral BORV). Déjalos como constantes con nombre y un comentario `// PENDIENTE Vx`.
- Cuando una prueba de banco confirme un valor, actualiza §13 del documento y la constante correspondiente.

## Estilo

- Responde y comenta en español.
- C99 para XC8 2.40–2.45, MPLAB X 6.x, MCC Classic.
- Nombres claros, sin números mágicos: cada constante con unidad y la sección del documento de donde sale.
- Cambios pequeños y verificables. Un commit por tema.
