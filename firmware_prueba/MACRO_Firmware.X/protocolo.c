/* protocolo.c - ver protocolo.h */
#include "protocolo.h"
#include "ascii.h"
#include "fsm.h"
#include "mcc_generated_files/eusart1.h"

#define PROTO_BUF_TX         40u   /* el mensaje mas largo, S:MEDIR con residuos de 4 cifras, mide 31 */
#define PROTO_DUTY_MAX       1023u /* sec. 7.4: duty 0-1023 */
#define PROTO_MENSAJES       1     /* 1 = con mensajes: los comandos de diagnostico (B, E?) necesitan sus respuestas; 0 = solo "I,Q" */

static char buf_tx[PROTO_BUF_TX];

/* ---- [PRUEBA] flujo de datos, rafaga en silencio y contador de TXOVR ---- */
#define RAF_PARES_ESPERA     50u   /* 100 ms sin encolar nada: la FIFO de 64 bytes se vacia en 5,6 ms */

typedef enum {
    RAF_INACTIVA = 0,
    RAF_ESPERA,         /* la UART se calla y se deja pasar RAF_PARES_ESPERA pares */
    RAF_CAPTURA,        /* se guardan PROTO_RAFAGA_PARES pares en RAM, sin transmitir */
    RAF_CABECERA,       /* falta enviar S:RAFAGA,n */
    RAF_VOLCADO,        /* se envian los pares guardados */
    RAF_FIN             /* falta enviar S:FIN */
} raf_estado_t;

static uint16_t     raf_i[PROTO_RAFAGA_PARES];
static uint16_t     raf_q[PROTO_RAFAGA_PARES];
static raf_estado_t raf_estado;
static uint16_t     raf_k;
static bool         flujo_apagado;
static uint16_t     n_txovr;

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

/* ---- [PRUEBA] ---- */
bool proto_par(uint16_t i, uint16_t q)
{
    switch (raf_estado) {
    case RAF_INACTIVA:
        if (flujo_apagado) {
            return true;
        }
        if (proto_datos(i, q)) {
            return true;
        }
        n_txovr++;
        return false;
    case RAF_ESPERA:
        raf_k++;
        if (raf_k >= RAF_PARES_ESPERA) {
            raf_k = 0;
            raf_estado = RAF_CAPTURA;
        }
        return true;
    case RAF_CAPTURA:
        raf_i[raf_k] = i;
        raf_q[raf_k] = q;
        raf_k++;
        if (raf_k >= PROTO_RAFAGA_PARES) {
            raf_k = 0;
            raf_estado = RAF_CABECERA;
        }
        return true;
    default:                        /* volcando: los pares en vivo no se envian */
        return true;
    }
}

void proto_diag_bombear(void)
{
    switch (raf_estado) {
    case RAF_CABECERA:
        if (enviar_linea(add_u16(add_str(0, "S:RAFAGA,"), PROTO_RAFAGA_PARES))) {
            raf_estado = RAF_VOLCADO;
        }
        break;
    case RAF_VOLCADO:
        if (raf_k < PROTO_RAFAGA_PARES) {
            if (proto_datos(raf_i[raf_k], raf_q[raf_k])) {
                raf_k++;
            }
        } else {
            raf_estado = RAF_FIN;
        }
        break;
    case RAF_FIN:
        if (enviar_linea(add_str(0, "S:FIN"))) {
            raf_estado = RAF_INACTIVA;
        }
        break;
    default:
        break;
    }
}

void proto_diag_flujo(bool encendido)
{
    flujo_apagado = !encendido;
}

static void responder_contadores(void)
{
    uint8_t n = add_str(0, "S:CNT,");      /* pares perdidos, pares descartados, lineas TXOVR */
    n = add_u16(n, adq_pares_perdidos());
    n = add_str(n, ",");
    n = add_u16(n, adq_pares_descartados());
    n = add_str(n, ",");
    (void)enviar_linea(add_u16(n, n_txovr));
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
    } else if (len == 3u && s[0] == 'D' && s[1] == ':' && (s[2] == '1' || s[2] == '0')) {
        /* [PRUEBA] D:1 = canales internos AVSS / FVR2 (1,024 V); D:0 = ANC0 / ANC1 */
        responder_resultado(fsm_cmd_diag_canales(s[2] == '1'),
                            (s[2] == '1') ? "OK:D,1" : "OK:D,0", 0, false);
    } else if (len == 5u && s[0] == 'X' && s[1] == ':' && s[3] == ',' && (s[4] == '1' || s[4] == '0')) {
        /* [PRUEBA] X:P|C|M|L|T,1|0 = enciende o apaga una fuente de ruido interna */
        responder_resultado(fsm_cmd_diag_x(s[2], s[4] == '1'), "OK:X", 0, false);
    } else if (len == 1u && s[0] == 'B') {
        /* [PRUEBA] B = rafaga: 256 pares capturados con la UART en silencio */
        if (fsm_estado() != FSM_REPOSO || raf_estado != RAF_INACTIVA) {
            responder_resultado(FSM_RES_ESTADO, "", 0, false);
        } else {
            responder_resultado(FSM_RES_OK, "OK:B", 0, false);
            raf_k = 0;
            raf_estado = RAF_ESPERA;
        }
    } else if (len == 2u && s[0] == 'E' && s[1] == '?') {
        responder_contadores();             /* [PRUEBA] E? = contadores de perdidas */
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
