/* fsm.c - ver fsm.h. Tabla de referencia: sec. 7.3 del documento de diseno. */
#include "fsm.h"
#include "autocero.h"
#include "protocolo.h"
#include "mcc_generated_files/mcc.h"

/* ---- Tiempos, en ticks de Timer6 (1 tick = 10 ms, sec. 6.8) ---- */
#define TICKS_PREPARAR           50u    /* 500 ms para C40/C41, filtros PWM y practica 2 (sec. 7.3) */
#define TICKS_HABILITAR          50u    /* 500 ms con duty 512/512 y EN_AZ_PIC = 1 (sec. 7.3) */
#define TICKS_POR_PASO_CAL       50u    /* 500 ms de asentamiento por paso (sec. 7.3) */
#define TICKS_VALIDAR            100u   /* 1 s = 500 pares (sec. 7.3) */
#define TICKS_ALARMA_SIN_CAUSA   10u    /* 100 ms sin causa para volver a MEDIR (sec. 7.3) */
#define TICKS_SAT_PERSISTENTE    10u    /* 100 ms con causa para entrar a ALARMA (sec. 7.3) */
#define TICKS_FALLO              200u   /* 2 s de parpadeo antes de volver a REPOSO (sec. 7.5) */
#define TICKS_ENTRE_AVISOS       100u   /* S:ALARMA como maximo 1 por segundo (sec. 7.4) */
#define TICKS_ANTIRREBOTE        3u     /* 30 ms (sec. 7.5) */

/* ---- LED D3 (sec. 7.5): fase de 0 a 99 = 1 s ---- */
#define LED_PERIODO_TICKS        100u
#define LED_MEDIO_1HZ            50u    /* 1 Hz: 50 on / 50 off */
#define LED_PERIODO_2HZ          50u    /* 2 Hz: 25 on / 25 off */
#define LED_PERIODO_4HZ          25u    /* 4 Hz: 12 on / 13 off */
#define LED_ON_4HZ               12u
#define LED_PERIODO_8HZ          25u    /* 8 Hz = 2 destellos por cada 25 ticks (6 on, 6 off, 6 on, 7 off) */
#define LED_ON_8HZ               6u
#define LED_INICIO_2DO_8HZ       12u
#define LED_DESTELLO_TICKS       10u    /* ALARMA: dos destellos de 100 ms cada segundo */
#define LED_INICIO_2DO_ALARMA    20u

/* ---- Codigos del ADC (sec. 6.4, sec. 7.3) ---- */
#define COD_SAT_BAJO_MAX         7u     /* ADLTH = -2040 <=> codigo <= 7 */

/* ---- Bits de saturacion acumulados en un tick ---- */
#define SAT_BIT_I                0x01u
#define SAT_BIT_Q                0x02u

typedef enum {
    CAUSA_NINGUNA = 0,
    CAUSA_SAT_I,
    CAUSA_SAT_Q,
    CAUSA_SIN_SENAL,
    CAUSA_TXOVR
} causa_alarma_t;

typedef enum {
    FALLO_LIM_I = 0,
    FALLO_LIM_Q,
    FALLO_RESIDUO
} causa_fallo_t;

static fsm_estado_t   estado;
static uint8_t        t_estado;          /* ticks desde que se entro al estado (satura en 255) */
static uint16_t       duty_i;
static uint16_t       duty_q;
static uint8_t        led_fase;
static uint8_t        boton_cuenta;
static bool           boton_pulsado;     /* ya se acepto esta pulsacion: hay que soltar antes de otra */
static uint8_t        sat_tick;          /* SAT_BIT_* vistos desde el tick anterior */
static bool           txovr_tick;
static uint16_t       ultimo_i;
static uint16_t       ultimo_q;
static uint8_t        cont_causa;        /* ticks seguidos con causa (MEDIR) o sin causa (ALARMA) */
static causa_alarma_t causa_alarma;
static uint8_t        t_aviso;
static bool           cal_esperando;     /* termino la espera: el siguiente par cierra el paso */
static causa_fallo_t  causa_fallo;
static int16_t        residuo_i;         /* error de la ultima muestra de VALIDAR (sin promedio) */
static int16_t        residuo_q;

/* ---- Utilidades ---- */
static void aplicar_duty(void)
{
    PWM6_LoadDutyValue(duty_i);     /* I0 -> RA2 */
    PWM7_LoadDutyValue(duty_q);     /* Q0 -> RA4 */
}

static void duty_neutro(void)
{
    duty_i = AZ_DUTY_NEUTRO;
    duty_q = AZ_DUTY_NEUTRO;
    aplicar_duty();
}

static const char *texto_causa_alarma(causa_alarma_t c)
{
    switch (c) {
    case CAUSA_SAT_I:     return "SAT_I";
    case CAUSA_SAT_Q:     return "SAT_Q";
    case CAUSA_SIN_SENAL: return "SIN_SENAL";
    default:              return "TXOVR";
    }
}

static const char *texto_causa_fallo(causa_fallo_t c)
{
    switch (c) {
    case FALLO_LIM_I: return "LIM_I";
    case FALLO_LIM_Q: return "LIM_Q";
    default:          return "RESIDUO";
    }
}

static int16_t error_codigo(uint16_t codigo)
{
    return (int16_t)codigo - (int16_t)AZ_CONSIGNA_CODIGOS;
}

static bool dentro_de_tol(int16_t err)
{
    return (err >= -(int16_t)AZ_TOL_CODIGOS) && (err <= (int16_t)AZ_TOL_CODIGOS);
}

/* Causa de alarma de este tick (sec. 7.3). SIN_SENAL va primero: con el cable abierto
 * ambos canales quedan <= 7 y tambien activan ADTIF. */
static causa_alarma_t evaluar_causa(void)
{
    if (ultimo_i <= COD_SAT_BAJO_MAX && ultimo_q <= COD_SAT_BAJO_MAX) {
        return CAUSA_SIN_SENAL;
    }
    if ((sat_tick & SAT_BIT_I) != 0u) {
        return CAUSA_SAT_I;
    }
    if ((sat_tick & SAT_BIT_Q) != 0u) {
        return CAUSA_SAT_Q;
    }
    if (txovr_tick) {
        return CAUSA_TXOVR;
    }
    return CAUSA_NINGUNA;
}

/* ---- Acciones de entrada (columna "Al entrar" de sec. 7.3) ---- */
static void entrar(fsm_estado_t nuevo)
{
    estado = nuevo;
    t_estado = 0;
    cont_causa = 0;

    switch (nuevo) {
    case FSM_REPOSO:
        EN_AZ_PIC_SetLow();                         /* J3 = VREF_BUF */
        proto_s_estado("REPOSO");
        break;
    case FSM_MANUAL:
        EN_AZ_PIC_SetHigh();                        /* con los duty actuales */
        proto_s_estado("MANUAL");
        break;
    case FSM_HABILITAR:
        duty_neutro();
        EN_AZ_PIC_SetHigh();
        proto_s_estado("CAL");
        break;
    case FSM_CALIBRAR:
        az_iniciar();
        duty_i = az_duty_i();                       /* 512: el bit 9 de prueba */
        duty_q = az_duty_q();
        aplicar_duty();
        cal_esperando = false;
        break;
    case FSM_VALIDAR:
        break;
    case FSM_MEDIR:
        proto_s_medir(duty_i, duty_q, residuo_i, residuo_q);
        break;
    case FSM_ALARMA:
        t_aviso = 0;
        proto_s_alarma(texto_causa_alarma(causa_alarma));
        break;
    case FSM_FALLO:
        EN_AZ_PIC_SetLow();
        duty_neutro();
        proto_s_fallo(texto_causa_fallo(causa_fallo));
        break;
    default:                                        /* INICIO y PREPARAR no tienen accion de entrada */
        break;
    }
}

void fsm_iniciar(void)
{
    EN_AZ_PIC_SetLow();             /* ya vale 0 desde MCC; se repite por seguridad (regla 11) */
    duty_neutro();
    TMR4_StopTimer();
    LED_STATUS_SetLow();
    estado = FSM_INICIO;
    t_estado = 0;
}

/* ---- LED (sec. 7.5) ---- */
static void led_actualizar(void)
{
    bool on;
    uint8_t p;

    led_fase++;
    if (led_fase >= LED_PERIODO_TICKS) {
        led_fase = 0;
    }
    switch (estado) {
    case FSM_PREPARAR:
    case FSM_REPOSO:
        on = (led_fase < LED_MEDIO_1HZ);
        break;
    case FSM_MANUAL:
        on = ((led_fase % LED_PERIODO_2HZ) < (LED_PERIODO_2HZ / 2u));
        break;
    case FSM_HABILITAR:
    case FSM_CALIBRAR:
    case FSM_VALIDAR:
        on = ((led_fase % LED_PERIODO_4HZ) < LED_ON_4HZ);
        break;
    case FSM_MEDIR:
        on = true;
        break;
    case FSM_ALARMA:
        on = (led_fase < LED_DESTELLO_TICKS) ||
             (led_fase >= LED_INICIO_2DO_ALARMA && led_fase < (LED_INICIO_2DO_ALARMA + LED_DESTELLO_TICKS));
        break;
    case FSM_FALLO:
        p = led_fase % LED_PERIODO_8HZ;
        on = (p < LED_ON_8HZ) || (p >= LED_INICIO_2DO_8HZ && p < (LED_INICIO_2DO_8HZ + LED_ON_8HZ));
        break;
    default:
        on = false;
        break;
    }
    if (on) {
        LED_STATUS_SetHigh();
    } else {
        LED_STATUS_SetLow();
    }
}

/* ---- SW2 (sec. 7.5): true una sola vez por pulsacion aceptada ---- */
static bool boton_evento(void)
{
    if (AZ_BUTTON_GetValue() != 0u) {               /* suelto (activo en bajo) */
        boton_cuenta = 0;
        boton_pulsado = false;
        return false;
    }
    if (boton_pulsado) {
        return false;
    }
    if (boton_cuenta < TICKS_ANTIRREBOTE) {
        boton_cuenta++;
    }
    if (boton_cuenta >= TICKS_ANTIRREBOTE) {
        boton_pulsado = true;
        return true;
    }
    return false;
}

/* ---- Un tick de 10 ms ---- */
void fsm_tick(void)
{
    bool z = boton_evento();
    causa_alarma_t causa;

    if (t_estado < 255u) {
        t_estado++;
    }
    if (t_aviso < 255u) {
        t_aviso++;
    }
    led_actualizar();

    switch (estado) {
    case FSM_INICIO:
        entrar(FSM_PREPARAR);
        break;

    case FSM_PREPARAR:
        if (FVR_IsOutputReady() && t_estado >= TICKS_PREPARAR) {
            proto_s_macro(adq_leer_fvra2x());
            adq_arrancar();
            entrar(FSM_REPOSO);
        }
        break;

    case FSM_REPOSO:
    case FSM_MANUAL:
        if (z) {
            entrar(FSM_HABILITAR);
        }
        break;

    case FSM_HABILITAR:
        if (t_estado >= TICKS_HABILITAR) {
            entrar(FSM_CALIBRAR);
        }
        break;

    case FSM_CALIBRAR:
        if (t_estado >= TICKS_POR_PASO_CAL) {
            cal_esperando = true;                   /* fsm_par cierra el paso con la siguiente muestra */
        }
        break;

    case FSM_VALIDAR:
        if (t_estado >= TICKS_VALIDAR) {
            entrar(FSM_MEDIR);
        }
        break;

    case FSM_MEDIR:
        if (z) {
            entrar(FSM_HABILITAR);                  /* invalida la medida */
            break;
        }
        causa = evaluar_causa();
        if (causa != CAUSA_NINGUNA) {
            cont_causa++;
            if (cont_causa >= TICKS_SAT_PERSISTENTE) {
                causa_alarma = causa;
                entrar(FSM_ALARMA);
            }
        } else {
            cont_causa = 0;
        }
        break;

    case FSM_ALARMA:
        causa = evaluar_causa();
        if (causa == CAUSA_NINGUNA) {
            cont_causa++;
            if (cont_causa >= TICKS_ALARMA_SIN_CAUSA) {
                entrar(FSM_MEDIR);
            }
        } else {
            cont_causa = 0;
            if (causa != causa_alarma && t_aviso >= TICKS_ENTRE_AVISOS) {
                causa_alarma = causa;
                t_aviso = 0;
                proto_s_alarma(texto_causa_alarma(causa));
            }
        }
        break;

    case FSM_FALLO:
        if (t_estado >= TICKS_FALLO) {
            entrar(FSM_REPOSO);
        }
        break;

    default:
        break;
    }
    sat_tick = 0;
    txovr_tick = false;
}

/* ---- Un par nuevo (~500 por segundo) ---- */
void fsm_par(const adq_par_t *par, bool enviado)
{
    ultimo_i = par->i;
    ultimo_q = par->q;
    if (par->sat_i) {
        sat_tick |= SAT_BIT_I;
    }
    if (par->sat_q) {
        sat_tick |= SAT_BIT_Q;
    }
    if (!enviado) {
        txovr_tick = true;
    }

    if (estado == FSM_CALIBRAR && cal_esperando) {
        bool fin = az_decidir(par->i, par->q);
        cal_esperando = false;
        t_estado = 0;
        duty_i = az_duty_i();
        duty_q = az_duty_q();
        aplicar_duty();
        proto_s_cal(az_pasos_hechos(), az_decidido_i(), az_decidido_q());
        if (fin) {
            /* sec. 7.3 VALIDAR: ningun duty en 0 o 1023 */
            if (duty_i == 0u || duty_i == AZ_DUTY_MAX) {
                causa_fallo = FALLO_LIM_I;
                entrar(FSM_FALLO);
            } else if (duty_q == 0u || duty_q == AZ_DUTY_MAX) {
                causa_fallo = FALLO_LIM_Q;
                entrar(FSM_FALLO);
            } else {
                entrar(FSM_VALIDAR);
            }
        }
    } else if (estado == FSM_VALIDAR) {
        residuo_i = error_codigo(par->i);
        residuo_q = error_codigo(par->q);
        if (!dentro_de_tol(residuo_i) || !dentro_de_tol(residuo_q)) {
            causa_fallo = FALLO_RESIDUO;
            entrar(FSM_FALLO);
        }
    }
}

/* ---- Comandos del PC (sec. 7.4) ---- */
fsm_resultado_t fsm_cmd_z(void)
{
    if (estado == FSM_REPOSO || estado == FSM_MANUAL || estado == FSM_MEDIR) {
        entrar(FSM_HABILITAR);
        return FSM_RES_OK;
    }
    return FSM_RES_ESTADO;
}

fsm_resultado_t fsm_cmd_r(void)
{
    if (estado == FSM_INICIO || estado == FSM_PREPARAR) {
        return FSM_RES_ESTADO;      /* aun no arranco el ADC: no hay REPOSO al que volver */
    }
    if (estado != FSM_REPOSO) {
        entrar(FSM_REPOSO);
    }
    return FSM_RES_OK;
}

fsm_resultado_t fsm_cmd_a(bool entrar_manual)
{
    if (entrar_manual && estado == FSM_REPOSO) {
        entrar(FSM_MANUAL);
        return FSM_RES_OK;
    }
    if (!entrar_manual && estado == FSM_MANUAL) {
        entrar(FSM_REPOSO);
        return FSM_RES_OK;
    }
    return FSM_RES_ESTADO;
}

fsm_resultado_t fsm_cmd_p(char canal, uint16_t duty)
{
    if (estado != FSM_REPOSO && estado != FSM_MANUAL) {
        return FSM_RES_ESTADO;
    }
    if (duty > AZ_DUTY_MAX) {
        return FSM_RES_RANGO;
    }
    if (canal == 'I') {
        duty_i = duty;
    } else {
        duty_q = duty;
    }
    aplicar_duty();
    return FSM_RES_OK;
}

void fsm_duty_actual(uint16_t *di, uint16_t *dq)
{
    *di = duty_i;
    *dq = duty_q;
}

fsm_estado_t fsm_estado(void)
{
    return estado;
}
