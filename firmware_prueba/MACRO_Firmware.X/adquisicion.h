/* adquisicion.h - canal I/Q, base de tiempo y publicacion de pares (sec. 4, sec. 7.1).
 * Timer4 dispara el ADCC por hardware; aqui NO se escribe ADGO nunca. */
#ifndef ADQUISICION_H
#define ADQUISICION_H

#include <stdint.h>
#include <stdbool.h>

#define ADQ_ADPCH_I              0x10u   /* ANC0 = RC0 (sec. 3.1, sec. 6.4) */
#define ADQ_ADPCH_Q              0x11u   /* ANC1 = RC1 */
#define ADQ_ADPCH_AVSS           0x3Bu   /* [PRUEBA] canal interno AVSS (tierra analogica), DS Tabla 32-4 */
#define ADQ_ADPCH_FVR2           0x3Fu   /* [PRUEBA] canal interno FVR buffer 2 (se pone en 1x = 1,024 V) */
#define ADQ_DIA_FVRA2X_DIR       0x8119u /* DIA: FVR x2 en mV (sec. 5.2) */
#define ADQ_MARCADOR_ISR_DBG     1       /* 1 = RC7 sube durante la ISR ADI (prueba V2); 0 = apagado */

typedef struct {
    uint16_t i;        /* codigo ADC 0..4095 */
    uint16_t q;
    bool     sat_i;    /* ADTIF visto en esa conversion (codigo <= 7 o >= 4088) */
    bool     sat_q;
} adq_par_t;

/* Instala los handlers: ADCC_SetADIInterruptHandler y TMR6_SetInterruptHandler.
 * Llamar despues de SYSTEM_Initialize y antes de habilitar GIE. */
void adq_iniciar(void);

/* Ultimo paso de PREPARAR: ADPCH = ANC0, borra ADIF/ADTIF y arranca Timer4. */
void adq_arrancar(void);

/* Lee FVRA2X del DIA (mV). */
uint16_t adq_leer_fvra2x(void);

/* Si hay un par nuevo lo copia en *par y devuelve true (cada par se entrega una vez). */
bool adq_tomar_par(adq_par_t *par);

/* true si paso un tick de 10 ms de Timer6 sin atender (lo consume). Se llama en
 * while desde main para no perder ticks. */
bool adq_tick_nuevo(void);

/* [PRUEBA] Cambia los dos canales que alterna la ISR (D:0 = ANC0/ANC1, D:1 = AVSS/FVR2).
 * El disparo sigue siendo de Timer4 por hardware; solo cambia lo que la ISR deja en ADPCH.
 * El primer par despues del cambio puede salir mezclado: descartarlo en el PC. */
void adq_diag_canales(uint8_t canal_i, uint8_t canal_q);

/* [PRUEBA] Enciende o apaga el pulso de RC7 dentro de la ISR ADI (X:M). */
void adq_diag_marcador(bool encendido);

/* Contadores de diagnostico (solo lectura). */
uint16_t adq_pares_perdidos(void);      /* publicados y pisados antes de que main los leyera */
uint16_t adq_pares_descartados(void);   /* par mal formado (ISR vio dos I seguidas o una Q sin I) */

#endif
