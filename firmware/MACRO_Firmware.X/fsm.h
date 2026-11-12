/* fsm.h - maquina de estados de MACRO (sec. 7.3), LED (sec. 7.5) y pulsador SW2.
 * Se llama solo desde main. Ninguna espera bloquea: el tiempo son ticks de Timer6 (10 ms). */
#ifndef FSM_H
#define FSM_H

#include <stdint.h>
#include <stdbool.h>
#include "adquisicion.h"

typedef enum {
    FSM_INICIO = 0,
    FSM_PREPARAR,
    FSM_REPOSO,
    FSM_MANUAL,
    FSM_HABILITAR,
    FSM_CALIBRAR,
    FSM_VALIDAR,
    FSM_MEDIR,
    FSM_ALARMA,
    FSM_FALLO
} fsm_estado_t;

typedef enum {
    FSM_RES_OK = 0,
    FSM_RES_ESTADO,     /* el comando no vale en el estado actual */
    FSM_RES_RANGO       /* argumento fuera de rango */
} fsm_resultado_t;

/* INICIO: deja EN_AZ_PIC = 0, PWM 512/512 y Timer4 parado, y pasa a PREPARAR en el primer tick. */
void fsm_iniciar(void);

/* Un tick de 10 ms: tiempos, LED, SW2 y transiciones. */
void fsm_tick(void);

/* Un par nuevo del ADC. enviado = false si la linea de datos no cupo en la FIFO de TX (TXOVR). */
void fsm_par(const adq_par_t *par, bool enviado);

/* Comandos del PC (sec. 7.4). */
fsm_resultado_t fsm_cmd_z(void);
fsm_resultado_t fsm_cmd_r(void);
fsm_resultado_t fsm_cmd_a(bool entrar_manual);
fsm_resultado_t fsm_cmd_p(char canal, uint16_t duty);   /* canal 'I' o 'Q', duty 0-1023 */
void fsm_duty_actual(uint16_t *duty_i, uint16_t *duty_q);

fsm_estado_t fsm_estado(void);

#endif
