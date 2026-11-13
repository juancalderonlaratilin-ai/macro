/* protocolo.h - mensajes hacia el PC y comandos desde el PC (sec. 7.4).
 * Todo el texto sale por tx_DAT (sin esperas) y se arma con ascii.c, sin printf. */
#ifndef PROTOCOLO_H
#define PROTOCOLO_H

#include <stdint.h>
#include <stdbool.h>

#define PROTO_LINEA_RX_MAX   12u   /* "P:Q,1023" = 8; lo demas es basura (sec. 6.10: RX FIFO de 32) */

/* ---- PIC -> PC ---- */
bool proto_datos(uint16_t i, uint16_t q);                 /* "IIII,QQQQ\r\n" (sin ceros a la izquierda) */
void proto_s_macro(uint16_t fvr_mv);                      /* "S:MACRO,FVR=2047" */
void proto_s_estado(const char *nombre);                  /* "S:REPOSO" */
void proto_s_cal(uint8_t paso, uint16_t di, uint16_t dq); /* "S:CAL,4,544,496" */
void proto_s_medir(uint16_t di, uint16_t dq, int16_t ri, int16_t rq); /* "S:MEDIR,541,497,+6,-3" */
void proto_s_alarma(const char *causa);                   /* "S:ALARMA,SAT_Q" */
void proto_s_fallo(const char *causa);                    /* "S:FALLO,LIM_I" */

/* ---- [PRUEBA] Diagnostico ---- */
#define PROTO_RAFAGA_PARES   256u  /* pares que se guardan en RAM con la UART en silencio (0,512 s) */

/* Sustituye a proto_datos en main: segun el modo envia la linea, la calla (X:T,0) o guarda
 * el par en la rafaga (B). Devuelve false solo si una linea normal no cupo en la FIFO (TXOVR). */
bool proto_par(uint16_t i, uint16_t q);

/* Envia la rafaga ya capturada: "S:RAFAGA,256", 256 lineas "I,Q" y "S:FIN". Sin esperas:
 * en cada vuelta de main encola lo que quepa en la FIFO. */
void proto_diag_bombear(void);

/* X:T,1 / X:T,0: enciende o apaga las lineas de datos. */
void proto_diag_flujo(bool encendido);

/* ---- PC -> PIC ---- */
/* Lee los bytes que haya en la FIFO de RX (sin esperar), arma la linea hasta '\n'
 * y ejecuta el comando contra la FSM. Responde OK:/E:. Llamar en cada vuelta de main. */
void proto_procesar(void);

#endif
