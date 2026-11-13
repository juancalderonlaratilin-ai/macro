/* autocero.h - aproximacion sucesiva de 10 bits del duty de I0/Q0 (sec. 7.3, sec. 5.3).
 * Logica pura: no toca registros. La FSM aplica los duty y mide los tiempos. */
#ifndef AUTOCERO_H
#define AUTOCERO_H

#include <stdint.h>
#include <stdbool.h>

/* ---- Valores fijos del diseno ---- */
#define AZ_CONSIGNA_CODIGOS      2048u   /* codigo ADC = 1,024 V; = ADSTPT (sec. 5.3, sec. 6.4) */
#define AZ_PASOS                 10u     /* un bit por paso, del bit 9 al 0 (sec. 7.3) */
#define AZ_DUTY_MAX              1023u   /* PWM de 10 bits (sec. 6.7) */
#define AZ_DUTY_NEUTRO           512u    /* 50 % = VREF_BUF, comando neutro (sec. 6.7) */

/* ---- PENDIENTES: se confirman en el banco, se ajustan solo aqui ---- */
#define AZ_GANANCIA_G            20      /* PENDIENTE V8: ganancia de practica 2 (10 o 20). sec. 13 punto 4 */
#define AZ_SIGNO_I               (+1)    /* PENDIENTE V8: +1 = si codigo > 2048, subir el duty de I0. sec. 7.3 */
#define AZ_SIGNO_Q               (+1)    /* PENDIENTE V8: idem para Q0 */

/* Codigos ADC que mueve un paso de duty: G * VDD / FVRA2X ~ 1,807 * G (sec. 5.5 d).
 * G = 20 -> 36; G = 10 -> 18. */
#define AZ_PASO_PWM_CODIGOS      ((uint16_t)(((uint32_t)AZ_GANANCIA_G * 1807UL + 500UL) / 1000UL))
#define AZ_MARGEN_TOL_CODIGOS    10u     /* margen sobre un paso PWM (sec. 7.3, tabla de parametros) */
#define AZ_TOL_CODIGOS           (AZ_PASO_PWM_CODIGOS + AZ_MARGEN_TOL_CODIGOS) /* TOL_AZ: 46 con G = 20 */

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
 * prueba si SIGNO * (codigo - 2048) > 0 (el codigo sigue alto: hace falta mas
 * duty). Devuelve true cuando ya se hicieron los AZ_PASOS pasos. */
bool az_decidir(uint16_t codigo_i, uint16_t codigo_q);

#endif
