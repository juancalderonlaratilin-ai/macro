/* [PRUEBA4] Referencia del ADC = VDD. Ver LEEME_PRUEBA4.md.
 * autocero.h - aproximacion sucesiva de 10 bits del duty de I0/Q0 (sec. 7.3, sec. 5.3).
 * Logica pura: no toca registros. La FSM aplica los duty y mide los tiempos. */
#ifndef AUTOCERO_H
#define AUTOCERO_H

#include <stdint.h>
#include <stdbool.h>

/* ---- [PRUEBA4] Referencia del ADC = VDD (rompe la regla 2 a pedido del equipo) ----
 * La sec. 5.3 fija la consigna en el codigo 2048 con el FVR (1,024 V). Esta copia usa VDD
 * como referencia del ADC, asi que la escala va de 0 a VDD y el codigo 2048 es VDD/2.
 * La consigna se calcula con la misma formula de firmware_prueba3, con VDD en vez del FVR:
 *     consigna = redondear(4096 x V_objetivo / VDD)
 * 1850 mV con VDD = 3700 mV -> 2048 (centro de la escala, +/-1,85 V de rango). */
#define AZ_V_OBJETIVO_MV         1850u   /* Vref2 de practica 2; medirla y ajustarla aqui */
#define AZ_VDD_MV                3700u   /* PENDIENTE: VDD medido con multimetro (sec. 0: 3,70 V nominal) */
#define AZ_VREF_MIN_MV           3000u   /* fuera de 3,0..4,2 V se usa AZ_VDD_NOMINAL_MV */
#define AZ_VREF_MAX_MV           4200u
#define AZ_VDD_NOMINAL_MV        3700u
#define AZ_CODIGO_SAT_BAJO       7u      /* <= 7 es saturacion abajo (ADLTH, sec. 6.4) */
#define AZ_CODIGO_SAT_ALTO       4088u   /* >= 4088 es saturacion arriba (ADUTH, sec. 6.4) */

/* ---- Valores fijos del diseno ---- */
#define AZ_PASOS                 10u     /* un bit por paso, del bit 9 al 0 (sec. 7.3) */
#define AZ_DUTY_MAX              1023u   /* PWM de 10 bits (sec. 6.7) */
#define AZ_DUTY_NEUTRO           512u    /* 50 % = VREF_BUF, comando neutro (sec. 6.7) */

/* ---- PENDIENTES: se confirman en el banco, se ajustan solo aqui ---- */
#define AZ_GANANCIA_G            20      /* PENDIENTE V8: ganancia de practica 2 (10 o 20). sec. 13 punto 4 */
#define AZ_SIGNO_I               (+1)    /* PENDIENTE V8: +1 = si codigo > consigna, subir el duty de I0. sec. 7.3 */
#define AZ_SIGNO_Q               (+1)    /* PENDIENTE V8: idem para Q0 */

/* Codigos ADC que mueve un paso de duty. Con el FVR era G * VDD / FVRA2X ~ 1,807 * G
 * (sec. 5.5 d). [PRUEBA4] Con VDD de referencia el paso de comando (VDD/4096) y el LSB del
 * ADC (VDD/4096) son iguales: G codigos por paso. G = 20 -> 20; G = 10 -> 10. */
#define AZ_PASO_PWM_CODIGOS      ((uint16_t)AZ_GANANCIA_G)
#define AZ_MARGEN_TOL_CODIGOS    10u     /* margen sobre un paso PWM (sec. 7.3, tabla de parametros) */
#define AZ_TOL_CODIGOS           (AZ_PASO_PWM_CODIGOS + AZ_MARGEN_TOL_CODIGOS) /* TOL_AZ: 30 con G = 20 (27 mV) */

/* La consigna no puede acercarse a la saturacion mas que TOL_AZ: VALIDAR tiene que caber. */
#define AZ_CONSIGNA_MIN          (AZ_CODIGO_SAT_BAJO + 1u + AZ_TOL_CODIGOS)
#define AZ_CONSIGNA_MAX          (AZ_CODIGO_SAT_ALTO - 1u - AZ_TOL_CODIGOS)

/* [PRUEBA4] Codigo ADC de AZ_V_OBJETIVO_MV con la referencia vref_mv (aqui VDD). Si vref_mv
 * esta fuera de AZ_VREF_MIN_MV..AZ_VREF_MAX_MV usa AZ_VDD_NOMINAL_MV. Acota a
 * AZ_CONSIGNA_MIN..MAX. */
uint16_t az_calcular_consigna(uint16_t vref_mv);

/* [PRUEBA3] Fija la consigna que usan az_decidir() y los residuos. Arranca en 2048. */
void     az_fijar_consigna(uint16_t codigos);
uint16_t az_consigna(void);

/* Empieza una calibracion: acumulados en 0, paso 0. */
void az_iniciar(void);

/* Duty que hay que aplicar ahora: lo decidido hasta aqui + el bit de prueba del
 * paso en curso. En el paso 0 vale 512. Al terminar, es el resultado final. */
uint16_t az_duty_i(void);
uint16_t az_duty_q(void);

/* Duty ya decidido (sin el bit de prueba): lo que se informa en S:CAL. */
uint16_t az_decidido_i(void);
uint16_t az_decidido_q(void);

/* Pasos terminados (0..AZ_PASOS). */
uint8_t az_pasos_hechos(void);

/* Cierra el paso en curso con una muestra de cada canal. Conserva el bit de
 * prueba si SIGNO * (codigo - consigna) > 0 (el codigo sigue alto: hace falta mas
 * duty). Devuelve true cuando ya se hicieron los AZ_PASOS pasos. */
bool az_decidir(uint16_t codigo_i, uint16_t codigo_q);

#endif
