/* [PRUEBA] Copia de diagnostico de MACRO (firmware_prueba). Ver LEEME_PRUEBA.md.
 * main.c - MACRO. Arranque y lazo principal. Ver docs/macro/firmware_funcionamiento.md. */
#include "mcc_generated_files/mcc.h"
#include "adquisicion.h"
#include "fsm.h"
#include "protocolo.h"

void main(void)
{
    adq_par_t par;

    SYSTEM_Initialize();            /* MCC: EN_AZ_PIC = 0, Timer4 parado, PWM 512/512 */
    adq_iniciar();                  /* handlers de ADCC y Timer6 */
    fsm_iniciar();

    INTERRUPT_GlobalInterruptEnable();      /* sec. 6.12: GIE y PEIE al final de la inicializacion */
    INTERRUPT_PeripheralInterruptEnable();

    while (1) {
        proto_procesar();                   /* comandos del PC */

        while (adq_tomar_par(&par)) {       /* un par cada 2 ms */
            bool enviado = proto_par(par.i, par.q);     /* [PRUEBA] flujo normal, silencio o rafaga */
            fsm_par(&par, enviado);
        }

        proto_diag_bombear();               /* [PRUEBA] vuelca la rafaga capturada, sin esperar */

        while (adq_tick_nuevo()) {          /* un tick cada 10 ms */
            fsm_tick();
        }
    }
}
