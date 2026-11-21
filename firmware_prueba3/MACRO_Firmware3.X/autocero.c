/* autocero.c - ver autocero.h */
#include "autocero.h"

static uint16_t decidido_i;
static uint16_t decidido_q;
static uint8_t  pasos;
static uint16_t consigna = 2048u;      /* [PRUEBA3] la FSM la fija al arrancar */

static uint16_t bit_de_prueba(void)
{
    return (pasos < AZ_PASOS) ? (uint16_t)(1u << (AZ_PASOS - 1u - pasos)) : 0u;
}

/* [PRUEBA3] consigna = redondear(4096 x V_objetivo / FVR_real) */
uint16_t az_calcular_consigna(uint16_t fvra2x_mv)
{
    uint32_t c;

    if (fvra2x_mv < AZ_FVR_MIN_MV || fvra2x_mv > AZ_FVR_MAX_MV) {
        fvra2x_mv = AZ_FVR_NOMINAL_MV;
    }
    c = (4096UL * (uint32_t)AZ_V_OBJETIVO_MV + (uint32_t)fvra2x_mv / 2u) / (uint32_t)fvra2x_mv;
    if (c < AZ_CONSIGNA_MIN) {
        c = AZ_CONSIGNA_MIN;
    }
    if (c > AZ_CONSIGNA_MAX) {
        c = AZ_CONSIGNA_MAX;
    }
    return (uint16_t)c;
}

void az_fijar_consigna(uint16_t codigos) { consigna = codigos; }
uint16_t az_consigna(void) { return consigna; }

void az_iniciar(void)
{
    decidido_i = 0;
    decidido_q = 0;
    pasos = 0;
}

uint16_t az_duty_i(void) { return decidido_i | bit_de_prueba(); }
uint16_t az_duty_q(void) { return decidido_q | bit_de_prueba(); }
uint16_t az_decidido_i(void) { return decidido_i; }
uint16_t az_decidido_q(void) { return decidido_q; }
uint8_t  az_pasos_hechos(void) { return pasos; }

bool az_decidir(uint16_t codigo_i, uint16_t codigo_q)
{
    uint16_t bit = bit_de_prueba();
    int16_t err_i = (int16_t)codigo_i - (int16_t)consigna;
    int16_t err_q = (int16_t)codigo_q - (int16_t)consigna;

    if (pasos >= AZ_PASOS) {
        return true;
    }
    if ((AZ_SIGNO_I * err_i) > 0) {
        decidido_i |= bit;
    }
    if ((AZ_SIGNO_Q * err_q) > 0) {
        decidido_q |= bit;
    }
    pasos++;
    return (pasos >= AZ_PASOS);
}
