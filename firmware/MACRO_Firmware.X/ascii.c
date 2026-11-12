/* ascii.c - ver ascii.h */
#include "ascii.h"

static const uint16_t POTENCIAS_10[ASCII_MAX_DIGITOS_U16] = {10000u, 1000u, 100u, 10u, 1u};

uint8_t ascii_u16(char *dst, uint16_t v)
{
    uint8_t n = 0;
    uint8_t k;
    for (k = 0; k < ASCII_MAX_DIGITOS_U16; k++) {
        uint8_t d = 0;
        while (v >= POTENCIAS_10[k]) {      /* resta repetida: sin division de 16 bits */
            v -= POTENCIAS_10[k];
            d++;
        }
        /* se omiten los ceros a la izquierda, salvo la ultima cifra */
        if (n != 0 || d != 0 || k == (ASCII_MAX_DIGITOS_U16 - 1u)) {
            dst[n++] = (char)('0' + d);
        }
    }
    return n;
}

uint8_t ascii_i16_signo(char *dst, int16_t v)
{
    uint16_t mag;
    if (v < 0) {
        dst[0] = '-';
        mag = (uint16_t)(-(int32_t)v);
    } else {
        dst[0] = '+';
        mag = (uint16_t)v;
    }
    return (uint8_t)(1u + ascii_u16(&dst[1], mag));
}

bool ascii_a_u16(const char *s, uint8_t len, uint16_t *valor)
{
    uint16_t acc = 0;
    bool desborda = false;
    uint8_t k;
    if (len == 0) {
        return false;
    }
    for (k = 0; k < len; k++) {
        uint8_t d;
        if (s[k] < '0' || s[k] > '9') {
            return false;
        }
        d = (uint8_t)(s[k] - '0');
        if (acc > (uint16_t)((65535u - d) / 10u)) {
            desborda = true;
        } else {
            acc = (uint16_t)(acc * 10u + d);
        }
    }
    *valor = desborda ? 65535u : acc;
    return true;
}
