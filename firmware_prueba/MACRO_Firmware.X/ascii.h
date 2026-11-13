/* ascii.h - conversion entero <-> ASCII hecha a mano (sec. 7.4, regla 5 de CLAUDE.md).
 * Sin printf/sprintf/scanf. Nada de aqui toca hardware. */
#ifndef ASCII_H
#define ASCII_H

#include <stdint.h>
#include <stdbool.h>

#define ASCII_MAX_DIGITOS_U16   5u   /* 65535 */

/* Escribe v en decimal, sin ceros a la izquierda y sin '\0'. Devuelve cuantos
 * caracteres escribio (1..5). dst debe tener 5 bytes libres. */
uint8_t ascii_u16(char *dst, uint16_t v);

/* Igual, pero con signo siempre ('+' o '-'): 1..6 caracteres. Sirve para los
 * residuos de S:MEDIR (ej. "+6", "-3"). */
uint8_t ascii_i16_signo(char *dst, int16_t v);

/* Lee len caracteres '0'..'9' como entero. Devuelve false si len es 0 o hay un
 * caracter que no es digito. Si el valor pasa de 65535 devuelve true y SATURA en
 * 65535 (el llamador lo rechazara por rango). */
bool ascii_a_u16(const char *s, uint8_t len, uint16_t *valor);

#endif
