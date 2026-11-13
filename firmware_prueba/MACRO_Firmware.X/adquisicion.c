/* adquisicion.c - ver adquisicion.h */
#include "adquisicion.h"
#include "mcc_generated_files/mcc.h"

/* ---- Estado de la ISR ADI (solo la ISR lo escribe) ---- */
static uint16_t i_tmp;
static bool     i_sat;
static bool     i_pendiente;
static volatile uint16_t descartados;

/* ---- [PRUEBA] canales que alterna la ISR y marcador de RC7, cambiables por comando ---- */
static volatile uint8_t canal_i = ADQ_ADPCH_I;
static volatile uint8_t canal_q = ADQ_ADPCH_Q;
static volatile bool    marcador_isr = true;

/* ---- Par publicado. seq cambia en cada publicacion; main lo usa para leer sin cortar la ISR ---- */
static volatile uint16_t pub_i;
static volatile uint16_t pub_q;
static volatile uint8_t  pub_sat;        /* bit0 = I, bit1 = Q */
static volatile uint8_t  pub_seq;
static uint8_t  seq_visto;
static uint16_t perdidos;

/* ---- Tick de Timer6 ---- */
static volatile uint8_t ticks_isr;
static uint8_t ticks_atendidos;

/* ISR ADI (regla 10): identifica el canal con ADPCH, copia ADRES, lee y borra ADTIF,
 * deja en ADPCH el otro canal y, al terminar Q, publica el par. Nada de formato ni estados.
 * ADCC_ISR (MCC) ya borro ADIF antes de llamarnos. */
static void adq_isr_adi(void)
{
    uint8_t  canal;
    uint16_t codigo;
    bool     sat;

#if ADQ_MARCADOR_ISR_DBG
    if (marcador_isr) {
        DBG_ISR_SetHigh();
    }
#endif
    canal  = ADPCH;
    codigo = ADRES;
    sat    = (PIR1bits.ADTIF != 0);
    PIR1bits.ADTIF = 0;

    if (canal == canal_i) {
        if (i_pendiente) {
            descartados++;                 /* dos I seguidas: la anterior se pierde */
        }
        i_tmp = codigo;
        i_sat = sat;
        i_pendiente = true;
        ADPCH = canal_q;
    } else {
        if (canal == canal_q && i_pendiente) {
            pub_i   = i_tmp;
            pub_q   = codigo;
            pub_sat = (uint8_t)((i_sat ? 1u : 0u) | (sat ? 2u : 0u));
            pub_seq++;
        } else {
            descartados++;                 /* Q sin I, o ADPCH con un canal inesperado */
        }
        i_pendiente = false;
        ADPCH = canal_i;
    }
#if ADQ_MARCADOR_ISR_DBG
    DBG_ISR_SetLow();
#endif
}

/* ISR TMR6: solo cuenta (regla 9). 1 tick = 10 ms. */
static void adq_isr_tmr6(void)
{
    ticks_isr++;
}

void adq_iniciar(void)
{
    i_pendiente = false;
    ADCC_SetADIInterruptHandler(adq_isr_adi);
    TMR6_SetInterruptHandler(adq_isr_tmr6);
}

void adq_arrancar(void)
{
    ADPCH = ADQ_ADPCH_I;            /* tras el reset ADPCH apunta a RA0/ICSPDAT (sec. 3.3) */
    PIR1bits.ADIF  = 0;
    PIR1bits.ADTIF = 0;
    i_pendiente = false;
    TMR4_StartTimer();              /* desde aqui todas las conversiones las dispara el hardware */
}

/* [PRUEBA] Se cierra ADIE mientras se cambian los canales para que la ISR no vea una mezcla. */
void adq_diag_canales(uint8_t ci, uint8_t cq)
{
    PIE1bits.ADIE = 0;
    canal_i = ci;
    canal_q = cq;
    i_pendiente = false;
    ADPCH = ci;                     /* la proxima conversion (disparo de Timer4) ya es del canal nuevo */
    PIR1bits.ADIF = 0;
    PIE1bits.ADIE = 1;
}

void adq_diag_marcador(bool encendido)
{
    marcador_isr = encendido;
}

uint16_t adq_leer_fvra2x(void)
{
    uint16_t mv;
    NVMADR = ADQ_DIA_FVRA2X_DIR;
    NVMCON1bits.NVMREGS = 1;        /* espacio DIA/configuracion */
    NVMCON1bits.RD = 1;
    NOP();
    NOP();
    mv = NVMDAT;
    NVMCON1bits.NVMREGS = 0;
    return mv;
}

bool adq_tomar_par(adq_par_t *par)
{
    uint8_t s1, s2, sat;
    uint16_t i, q;

    do {                            /* lectura coherente: si la ISR publico a mitad, se repite */
        s1  = pub_seq;
        i   = pub_i;
        q   = pub_q;
        sat = pub_sat;
        s2  = pub_seq;
    } while (s1 != s2);

    if (s1 == seq_visto) {
        return false;
    }
    perdidos += (uint8_t)(s1 - seq_visto - 1u);
    seq_visto = s1;
    par->i = i;
    par->q = q;
    par->sat_i = ((sat & 1u) != 0);
    par->sat_q = ((sat & 2u) != 0);
    return true;
}

bool adq_tick_nuevo(void)
{
    if (ticks_isr == ticks_atendidos) {
        return false;
    }
    ticks_atendidos++;
    return true;
}

uint16_t adq_pares_perdidos(void)    { return perdidos; }
uint16_t adq_pares_descartados(void) { return descartados; }
