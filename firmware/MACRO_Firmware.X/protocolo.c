/* protocolo.c - ver protocolo.h */
#include "protocolo.h"
#include "ascii.h"
#include "fsm.h"
#include "mcc_generated_files/eusart1.h"

#define PROTO_BUF_TX         40u   /* el mensaje mas largo, S:MEDIR con residuos de 4 cifras, mide 31 */
#define PROTO_DUTY_MAX       1023u /* sec. 7.4: duty 0-1023 */
#define PROTO_MENSAJES       0     /* 0 = solo lineas "I,Q" (sin S:/OK:/E:); 1 = protocolo completo de la sec. 7.4 */

static char buf_tx[PROTO_BUF_TX];

/* ---- Armado de mensajes ---- */
static uint8_t add_str(uint8_t n, const char *s)
{
    while (*s != '\0') {
        buf_tx[n++] = *s++;
    }
    return n;
}

static uint8_t add_u16(uint8_t n, uint16_t v)
{
    return (uint8_t)(n + ascii_u16(&buf_tx[n], v));
}

static uint8_t add_i16(uint8_t n, int16_t v)
{
    return (uint8_t)(n + ascii_i16_signo(&buf_tx[n], v));
}

/* Lineas de datos "I,Q": siempre se envian. */
static bool enviar_datos(uint8_t n)
{
    n = add_str(n, "\r\n");
    return tx_DAT(buf_tx, n);
}

/* Mensajes S:, OK:, E: y P: (sec. 7.4). Con PROTO_MENSAJES = 0 no sale ninguno por la UART:
 * el PIC solo manda lineas "I,Q". Los comandos del PC se siguen ejecutando, sin respuesta. */
static bool enviar_linea(uint8_t n)
{
#if PROTO_MENSAJES
    return enviar_datos(n);
#else
    (void)n;
    return true;
#endif
}

bool proto_datos(uint16_t i, uint16_t q)
{
    uint8_t n = add_u16(0, i);
    buf_tx[n++] = ',';
    n = add_u16(n, q);
    return enviar_datos(n);
}

void proto_s_macro(uint16_t fvr_mv)
{
    uint8_t n = add_str(0, "S:MACRO,FVR=");
    (void)enviar_linea(add_u16(n, fvr_mv));
}

void proto_s_estado(const char *nombre)
{
    (void)enviar_linea(add_str(add_str(0, "S:"), nombre));
}

void proto_s_cal(uint8_t paso, uint16_t di, uint16_t dq)
{
    uint8_t n = add_str(0, "S:CAL,");
    n = add_u16(n, paso);
    n = add_str(n, ",");
    n = add_u16(n, di);
    n = add_str(n, ",");
    (void)enviar_linea(add_u16(n, dq));
}

void proto_s_medir(uint16_t di, uint16_t dq, int16_t ri, int16_t rq)
{
    uint8_t n = add_str(0, "S:MEDIR,");
    n = add_u16(n, di);
    n = add_str(n, ",");
    n = add_u16(n, dq);
    n = add_str(n, ",");
    n = add_i16(n, ri);
    n = add_str(n, ",");
    (void)enviar_linea(add_i16(n, rq));
}

void proto_s_alarma(const char *causa)
{
    (void)enviar_linea(add_str(add_str(0, "S:ALARMA,"), causa));
}

void proto_s_fallo(const char *causa)
{
    (void)enviar_linea(add_str(add_str(0, "S:FALLO,"), causa));
}

/* ---- Respuestas a comandos ---- */
static void responder_resultado(fsm_resultado_t r, const char *ok_texto, uint16_t ok_valor, bool con_valor)
{
    uint8_t n;
    if (r == FSM_RES_OK) {
        n = add_str(0, ok_texto);
        if (con_valor) {
            n = add_u16(n, ok_valor);
        }
    } else if (r == FSM_RES_RANGO) {
        n = add_str(0, "E:rango");
    } else {
        n = add_str(0, "E:estado");
    }
    (void)enviar_linea(n);
}

static void responder_error_comando(void)
{
    (void)enviar_linea(add_str(0, "E:cmd"));
}

static void responder_p_consulta(void)
{
    uint16_t di, dq;
    uint8_t n;
    fsm_duty_actual(&di, &dq);
    n = add_str(0, "P:I,");     /* tal como lo fija sec. 7.4: la respuesta a P? no lleva "OK:" */
    n = add_u16(n, di);
    n = add_str(n, ",Q,");
    (void)enviar_linea(add_u16(n, dq));
}

/* ---- Interprete de una linea ya completa (sin '\r' ni '\n') ---- */
static void ejecutar(const char *s, uint8_t len)
{
    if (len == 1u && s[0] == 'Z') {
        responder_resultado(fsm_cmd_z(), "OK:Z", 0, false);
    } else if (len == 1u && s[0] == 'R') {
        responder_resultado(fsm_cmd_r(), "OK:R", 0, false);
    } else if (len == 3u && s[0] == 'A' && s[1] == ':' && (s[2] == '1' || s[2] == '0')) {
        responder_resultado(fsm_cmd_a(s[2] == '1'),
                            (s[2] == '1') ? "OK:A,1" : "OK:A,0", 0, false);
    } else if (len == 2u && s[0] == 'P' && s[1] == '?') {
        responder_p_consulta();
    } else if (len >= 5u && s[0] == 'P' && s[1] == ':' && (s[2] == 'I' || s[2] == 'Q') && s[3] == ',') {
        uint16_t n;
        if (!ascii_a_u16(&s[4], (uint8_t)(len - 4u), &n)) {
            responder_error_comando();
        } else if (n > PROTO_DUTY_MAX) {
            responder_resultado(FSM_RES_RANGO, "", 0, false);
        } else {
            responder_resultado(fsm_cmd_p(s[2], n), (s[2] == 'I') ? "OK:I," : "OK:Q,", n, true);
        }
    } else {
        responder_error_comando();
    }
}

void proto_procesar(void)
{
    static char linea[PROTO_LINEA_RX_MAX];
    static uint8_t len;
    static bool excedida;
    uint8_t c;

    while (EUSART1_Read(&c)) {
        if (c == (uint8_t)'\r') {
            continue;
        }
        if (c != (uint8_t)'\n') {
            if (len < PROTO_LINEA_RX_MAX) {
                linea[len++] = (char)c;
            } else {
                excedida = true;
            }
            continue;
        }
        if (excedida) {
            responder_error_comando();
        } else if (len != 0u) {
            ejecutar(linea, len);
        }
        len = 0;
        excedida = false;
    }
}
