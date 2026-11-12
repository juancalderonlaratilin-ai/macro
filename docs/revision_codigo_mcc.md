# Registro de cambios a archivos generados por MCC - MACRO

| ID | Archivo | Cambio | Motivo | Fecha |
|---|---|---|---|---|
| C-11 | `mcc_generated_files/interrupt_manager.c` (`INTERRUPT_InterruptManager`) | (a) Orden de ramas: antes TMR6 → TX → RX → ADC; ahora RX → ADI (`ADCC_ISR`) → TX → TMR6. (b) Rama RX: antes `EUSART1_RxDefaultInterruptHandler()`, ahora `EUSART1_Receive_ISR()`. (c) Rama TX: antes `EUSART1_TxDefaultInterruptHandler()`, ahora `EUSART1_Transmit_ISR()`. Cada rama sigue comprobando habilitación y bandera. | Regla 9 de CLAUDE.md y §6.12: una sola ISR con orden RX → ADI → TX → TMR6; llamar directo al código de Micro 3 de `eusart1.c` (ver C-06). | 2026-11-12 |
