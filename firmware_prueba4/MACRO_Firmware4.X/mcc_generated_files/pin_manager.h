/**
  @Generated Pin Manager Header File

  @Company:
    Microchip Technology Inc.

  @File Name:
    pin_manager.h

  @Summary:
    This is the Pin Manager file generated using PIC10 / PIC12 / PIC16 / PIC18 MCUs

  @Description
    This header file provides APIs for driver for .
    Generation Information :
        Product Revision  :  PIC10 / PIC12 / PIC16 / PIC18 MCUs - 1.81.8
        Device            :  PIC16F18446
        Driver Version    :  2.11
    The generated drivers are tested against the following:
        Compiler          :  XC8 2.36 and above
        MPLAB 	          :  MPLAB X 6.00	
*/

/*
    (c) 2018 Microchip Technology Inc. and its subsidiaries. 
    
    Subject to your compliance with these terms, you may use Microchip software and any 
    derivatives exclusively with Microchip products. It is your responsibility to comply with third party 
    license terms applicable to your use of third party software (including open source software) that 
    may accompany Microchip software.
    
    THIS SOFTWARE IS SUPPLIED BY MICROCHIP "AS IS". NO WARRANTIES, WHETHER 
    EXPRESS, IMPLIED OR STATUTORY, APPLY TO THIS SOFTWARE, INCLUDING ANY 
    IMPLIED WARRANTIES OF NON-INFRINGEMENT, MERCHANTABILITY, AND FITNESS 
    FOR A PARTICULAR PURPOSE.
    
    IN NO EVENT WILL MICROCHIP BE LIABLE FOR ANY INDIRECT, SPECIAL, PUNITIVE, 
    INCIDENTAL OR CONSEQUENTIAL LOSS, DAMAGE, COST OR EXPENSE OF ANY KIND 
    WHATSOEVER RELATED TO THE SOFTWARE, HOWEVER CAUSED, EVEN IF MICROCHIP 
    HAS BEEN ADVISED OF THE POSSIBILITY OR THE DAMAGES ARE FORESEEABLE. TO 
    THE FULLEST EXTENT ALLOWED BY LAW, MICROCHIP'S TOTAL LIABILITY ON ALL 
    CLAIMS IN ANY WAY RELATED TO THIS SOFTWARE WILL NOT EXCEED THE AMOUNT 
    OF FEES, IF ANY, THAT YOU HAVE PAID DIRECTLY TO MICROCHIP FOR THIS 
    SOFTWARE.
*/

#ifndef PIN_MANAGER_H
#define PIN_MANAGER_H

/**
  Section: Included Files
*/

#include <xc.h>

#define INPUT   1
#define OUTPUT  0

#define HIGH    1
#define LOW     0

#define ANALOG      1
#define DIGITAL     0

#define PULL_UP_ENABLED      1
#define PULL_UP_DISABLED     0

// get/set RA2 procedures
#define RA2_SetHigh()            do { LATAbits.LATA2 = 1; } while(0)
#define RA2_SetLow()             do { LATAbits.LATA2 = 0; } while(0)
#define RA2_Toggle()             do { LATAbits.LATA2 = ~LATAbits.LATA2; } while(0)
#define RA2_GetValue()              PORTAbits.RA2
#define RA2_SetDigitalInput()    do { TRISAbits.TRISA2 = 1; } while(0)
#define RA2_SetDigitalOutput()   do { TRISAbits.TRISA2 = 0; } while(0)
#define RA2_SetPullup()             do { WPUAbits.WPUA2 = 1; } while(0)
#define RA2_ResetPullup()           do { WPUAbits.WPUA2 = 0; } while(0)
#define RA2_SetAnalogMode()         do { ANSELAbits.ANSA2 = 1; } while(0)
#define RA2_SetDigitalMode()        do { ANSELAbits.ANSA2 = 0; } while(0)

// get/set RA4 procedures
#define RA4_SetHigh()            do { LATAbits.LATA4 = 1; } while(0)
#define RA4_SetLow()             do { LATAbits.LATA4 = 0; } while(0)
#define RA4_Toggle()             do { LATAbits.LATA4 = ~LATAbits.LATA4; } while(0)
#define RA4_GetValue()              PORTAbits.RA4
#define RA4_SetDigitalInput()    do { TRISAbits.TRISA4 = 1; } while(0)
#define RA4_SetDigitalOutput()   do { TRISAbits.TRISA4 = 0; } while(0)
#define RA4_SetPullup()             do { WPUAbits.WPUA4 = 1; } while(0)
#define RA4_ResetPullup()           do { WPUAbits.WPUA4 = 0; } while(0)
#define RA4_SetAnalogMode()         do { ANSELAbits.ANSA4 = 1; } while(0)
#define RA4_SetDigitalMode()        do { ANSELAbits.ANSA4 = 0; } while(0)

// get/set LED_STATUS aliases
#define LED_STATUS_TRIS                 TRISAbits.TRISA5
#define LED_STATUS_LAT                  LATAbits.LATA5
#define LED_STATUS_PORT                 PORTAbits.RA5
#define LED_STATUS_WPU                  WPUAbits.WPUA5
#define LED_STATUS_OD                   ODCONAbits.ODCA5
#define LED_STATUS_ANS                  ANSELAbits.ANSA5
#define LED_STATUS_SetHigh()            do { LATAbits.LATA5 = 1; } while(0)
#define LED_STATUS_SetLow()             do { LATAbits.LATA5 = 0; } while(0)
#define LED_STATUS_Toggle()             do { LATAbits.LATA5 = ~LATAbits.LATA5; } while(0)
#define LED_STATUS_GetValue()           PORTAbits.RA5
#define LED_STATUS_SetDigitalInput()    do { TRISAbits.TRISA5 = 1; } while(0)
#define LED_STATUS_SetDigitalOutput()   do { TRISAbits.TRISA5 = 0; } while(0)
#define LED_STATUS_SetPullup()          do { WPUAbits.WPUA5 = 1; } while(0)
#define LED_STATUS_ResetPullup()        do { WPUAbits.WPUA5 = 0; } while(0)
#define LED_STATUS_SetPushPull()        do { ODCONAbits.ODCA5 = 0; } while(0)
#define LED_STATUS_SetOpenDrain()       do { ODCONAbits.ODCA5 = 1; } while(0)
#define LED_STATUS_SetAnalogMode()      do { ANSELAbits.ANSA5 = 1; } while(0)
#define LED_STATUS_SetDigitalMode()     do { ANSELAbits.ANSA5 = 0; } while(0)

// get/set EXP_RB4 aliases
#define EXP_RB4_TRIS                 TRISBbits.TRISB4
#define EXP_RB4_LAT                  LATBbits.LATB4
#define EXP_RB4_PORT                 PORTBbits.RB4
#define EXP_RB4_WPU                  WPUBbits.WPUB4
#define EXP_RB4_OD                   ODCONBbits.ODCB4
#define EXP_RB4_ANS                  ANSELBbits.ANSB4
#define EXP_RB4_SetHigh()            do { LATBbits.LATB4 = 1; } while(0)
#define EXP_RB4_SetLow()             do { LATBbits.LATB4 = 0; } while(0)
#define EXP_RB4_Toggle()             do { LATBbits.LATB4 = ~LATBbits.LATB4; } while(0)
#define EXP_RB4_GetValue()           PORTBbits.RB4
#define EXP_RB4_SetDigitalInput()    do { TRISBbits.TRISB4 = 1; } while(0)
#define EXP_RB4_SetDigitalOutput()   do { TRISBbits.TRISB4 = 0; } while(0)
#define EXP_RB4_SetPullup()          do { WPUBbits.WPUB4 = 1; } while(0)
#define EXP_RB4_ResetPullup()        do { WPUBbits.WPUB4 = 0; } while(0)
#define EXP_RB4_SetPushPull()        do { ODCONBbits.ODCB4 = 0; } while(0)
#define EXP_RB4_SetOpenDrain()       do { ODCONBbits.ODCB4 = 1; } while(0)
#define EXP_RB4_SetAnalogMode()      do { ANSELBbits.ANSB4 = 1; } while(0)
#define EXP_RB4_SetDigitalMode()     do { ANSELBbits.ANSB4 = 0; } while(0)

// get/set EXP_RB6 aliases
#define EXP_RB6_TRIS                 TRISBbits.TRISB6
#define EXP_RB6_LAT                  LATBbits.LATB6
#define EXP_RB6_PORT                 PORTBbits.RB6
#define EXP_RB6_WPU                  WPUBbits.WPUB6
#define EXP_RB6_OD                   ODCONBbits.ODCB6
#define EXP_RB6_ANS                  ANSELBbits.ANSB6
#define EXP_RB6_SetHigh()            do { LATBbits.LATB6 = 1; } while(0)
#define EXP_RB6_SetLow()             do { LATBbits.LATB6 = 0; } while(0)
#define EXP_RB6_Toggle()             do { LATBbits.LATB6 = ~LATBbits.LATB6; } while(0)
#define EXP_RB6_GetValue()           PORTBbits.RB6
#define EXP_RB6_SetDigitalInput()    do { TRISBbits.TRISB6 = 1; } while(0)
#define EXP_RB6_SetDigitalOutput()   do { TRISBbits.TRISB6 = 0; } while(0)
#define EXP_RB6_SetPullup()          do { WPUBbits.WPUB6 = 1; } while(0)
#define EXP_RB6_ResetPullup()        do { WPUBbits.WPUB6 = 0; } while(0)
#define EXP_RB6_SetPushPull()        do { ODCONBbits.ODCB6 = 0; } while(0)
#define EXP_RB6_SetOpenDrain()       do { ODCONBbits.ODCB6 = 1; } while(0)
#define EXP_RB6_SetAnalogMode()      do { ANSELBbits.ANSB6 = 1; } while(0)
#define EXP_RB6_SetDigitalMode()     do { ANSELBbits.ANSB6 = 0; } while(0)

// get/set CANAL_I aliases
#define CANAL_I_TRIS                 TRISCbits.TRISC0
#define CANAL_I_LAT                  LATCbits.LATC0
#define CANAL_I_PORT                 PORTCbits.RC0
#define CANAL_I_WPU                  WPUCbits.WPUC0
#define CANAL_I_OD                   ODCONCbits.ODCC0
#define CANAL_I_ANS                  ANSELCbits.ANSC0
#define CANAL_I_SetHigh()            do { LATCbits.LATC0 = 1; } while(0)
#define CANAL_I_SetLow()             do { LATCbits.LATC0 = 0; } while(0)
#define CANAL_I_Toggle()             do { LATCbits.LATC0 = ~LATCbits.LATC0; } while(0)
#define CANAL_I_GetValue()           PORTCbits.RC0
#define CANAL_I_SetDigitalInput()    do { TRISCbits.TRISC0 = 1; } while(0)
#define CANAL_I_SetDigitalOutput()   do { TRISCbits.TRISC0 = 0; } while(0)
#define CANAL_I_SetPullup()          do { WPUCbits.WPUC0 = 1; } while(0)
#define CANAL_I_ResetPullup()        do { WPUCbits.WPUC0 = 0; } while(0)
#define CANAL_I_SetPushPull()        do { ODCONCbits.ODCC0 = 0; } while(0)
#define CANAL_I_SetOpenDrain()       do { ODCONCbits.ODCC0 = 1; } while(0)
#define CANAL_I_SetAnalogMode()      do { ANSELCbits.ANSC0 = 1; } while(0)
#define CANAL_I_SetDigitalMode()     do { ANSELCbits.ANSC0 = 0; } while(0)

// get/set CANAL_Q aliases
#define CANAL_Q_TRIS                 TRISCbits.TRISC1
#define CANAL_Q_LAT                  LATCbits.LATC1
#define CANAL_Q_PORT                 PORTCbits.RC1
#define CANAL_Q_WPU                  WPUCbits.WPUC1
#define CANAL_Q_OD                   ODCONCbits.ODCC1
#define CANAL_Q_ANS                  ANSELCbits.ANSC1
#define CANAL_Q_SetHigh()            do { LATCbits.LATC1 = 1; } while(0)
#define CANAL_Q_SetLow()             do { LATCbits.LATC1 = 0; } while(0)
#define CANAL_Q_Toggle()             do { LATCbits.LATC1 = ~LATCbits.LATC1; } while(0)
#define CANAL_Q_GetValue()           PORTCbits.RC1
#define CANAL_Q_SetDigitalInput()    do { TRISCbits.TRISC1 = 1; } while(0)
#define CANAL_Q_SetDigitalOutput()   do { TRISCbits.TRISC1 = 0; } while(0)
#define CANAL_Q_SetPullup()          do { WPUCbits.WPUC1 = 1; } while(0)
#define CANAL_Q_ResetPullup()        do { WPUCbits.WPUC1 = 0; } while(0)
#define CANAL_Q_SetPushPull()        do { ODCONCbits.ODCC1 = 0; } while(0)
#define CANAL_Q_SetOpenDrain()       do { ODCONCbits.ODCC1 = 1; } while(0)
#define CANAL_Q_SetAnalogMode()      do { ANSELCbits.ANSC1 = 1; } while(0)
#define CANAL_Q_SetDigitalMode()     do { ANSELCbits.ANSC1 = 0; } while(0)

// get/set EN_AZ_PIC aliases
#define EN_AZ_PIC_TRIS                 TRISCbits.TRISC2
#define EN_AZ_PIC_LAT                  LATCbits.LATC2
#define EN_AZ_PIC_PORT                 PORTCbits.RC2
#define EN_AZ_PIC_WPU                  WPUCbits.WPUC2
#define EN_AZ_PIC_OD                   ODCONCbits.ODCC2
#define EN_AZ_PIC_ANS                  ANSELCbits.ANSC2
#define EN_AZ_PIC_SetHigh()            do { LATCbits.LATC2 = 1; } while(0)
#define EN_AZ_PIC_SetLow()             do { LATCbits.LATC2 = 0; } while(0)
#define EN_AZ_PIC_Toggle()             do { LATCbits.LATC2 = ~LATCbits.LATC2; } while(0)
#define EN_AZ_PIC_GetValue()           PORTCbits.RC2
#define EN_AZ_PIC_SetDigitalInput()    do { TRISCbits.TRISC2 = 1; } while(0)
#define EN_AZ_PIC_SetDigitalOutput()   do { TRISCbits.TRISC2 = 0; } while(0)
#define EN_AZ_PIC_SetPullup()          do { WPUCbits.WPUC2 = 1; } while(0)
#define EN_AZ_PIC_ResetPullup()        do { WPUCbits.WPUC2 = 0; } while(0)
#define EN_AZ_PIC_SetPushPull()        do { ODCONCbits.ODCC2 = 0; } while(0)
#define EN_AZ_PIC_SetOpenDrain()       do { ODCONCbits.ODCC2 = 1; } while(0)
#define EN_AZ_PIC_SetAnalogMode()      do { ANSELCbits.ANSC2 = 1; } while(0)
#define EN_AZ_PIC_SetDigitalMode()     do { ANSELCbits.ANSC2 = 0; } while(0)

// get/set AZ_BUTTON aliases
#define AZ_BUTTON_TRIS                 TRISCbits.TRISC3
#define AZ_BUTTON_LAT                  LATCbits.LATC3
#define AZ_BUTTON_PORT                 PORTCbits.RC3
#define AZ_BUTTON_WPU                  WPUCbits.WPUC3
#define AZ_BUTTON_OD                   ODCONCbits.ODCC3
#define AZ_BUTTON_ANS                  ANSELCbits.ANSC3
#define AZ_BUTTON_SetHigh()            do { LATCbits.LATC3 = 1; } while(0)
#define AZ_BUTTON_SetLow()             do { LATCbits.LATC3 = 0; } while(0)
#define AZ_BUTTON_Toggle()             do { LATCbits.LATC3 = ~LATCbits.LATC3; } while(0)
#define AZ_BUTTON_GetValue()           PORTCbits.RC3
#define AZ_BUTTON_SetDigitalInput()    do { TRISCbits.TRISC3 = 1; } while(0)
#define AZ_BUTTON_SetDigitalOutput()   do { TRISCbits.TRISC3 = 0; } while(0)
#define AZ_BUTTON_SetPullup()          do { WPUCbits.WPUC3 = 1; } while(0)
#define AZ_BUTTON_ResetPullup()        do { WPUCbits.WPUC3 = 0; } while(0)
#define AZ_BUTTON_SetPushPull()        do { ODCONCbits.ODCC3 = 0; } while(0)
#define AZ_BUTTON_SetOpenDrain()       do { ODCONCbits.ODCC3 = 1; } while(0)
#define AZ_BUTTON_SetAnalogMode()      do { ANSELCbits.ANSC3 = 1; } while(0)
#define AZ_BUTTON_SetDigitalMode()     do { ANSELCbits.ANSC3 = 0; } while(0)

// get/set RC4 procedures
#define RC4_SetHigh()            do { LATCbits.LATC4 = 1; } while(0)
#define RC4_SetLow()             do { LATCbits.LATC4 = 0; } while(0)
#define RC4_Toggle()             do { LATCbits.LATC4 = ~LATCbits.LATC4; } while(0)
#define RC4_GetValue()              PORTCbits.RC4
#define RC4_SetDigitalInput()    do { TRISCbits.TRISC4 = 1; } while(0)
#define RC4_SetDigitalOutput()   do { TRISCbits.TRISC4 = 0; } while(0)
#define RC4_SetPullup()             do { WPUCbits.WPUC4 = 1; } while(0)
#define RC4_ResetPullup()           do { WPUCbits.WPUC4 = 0; } while(0)
#define RC4_SetAnalogMode()         do { ANSELCbits.ANSC4 = 1; } while(0)
#define RC4_SetDigitalMode()        do { ANSELCbits.ANSC4 = 0; } while(0)

// get/set RC5 procedures
#define RC5_SetHigh()            do { LATCbits.LATC5 = 1; } while(0)
#define RC5_SetLow()             do { LATCbits.LATC5 = 0; } while(0)
#define RC5_Toggle()             do { LATCbits.LATC5 = ~LATCbits.LATC5; } while(0)
#define RC5_GetValue()              PORTCbits.RC5
#define RC5_SetDigitalInput()    do { TRISCbits.TRISC5 = 1; } while(0)
#define RC5_SetDigitalOutput()   do { TRISCbits.TRISC5 = 0; } while(0)
#define RC5_SetPullup()             do { WPUCbits.WPUC5 = 1; } while(0)
#define RC5_ResetPullup()           do { WPUCbits.WPUC5 = 0; } while(0)
#define RC5_SetAnalogMode()         do { ANSELCbits.ANSC5 = 1; } while(0)
#define RC5_SetDigitalMode()        do { ANSELCbits.ANSC5 = 0; } while(0)

// get/set RC6 procedures
#define RC6_SetHigh()            do { LATCbits.LATC6 = 1; } while(0)
#define RC6_SetLow()             do { LATCbits.LATC6 = 0; } while(0)
#define RC6_Toggle()             do { LATCbits.LATC6 = ~LATCbits.LATC6; } while(0)
#define RC6_GetValue()              PORTCbits.RC6
#define RC6_SetDigitalInput()    do { TRISCbits.TRISC6 = 1; } while(0)
#define RC6_SetDigitalOutput()   do { TRISCbits.TRISC6 = 0; } while(0)
#define RC6_SetPullup()             do { WPUCbits.WPUC6 = 1; } while(0)
#define RC6_ResetPullup()           do { WPUCbits.WPUC6 = 0; } while(0)
#define RC6_SetAnalogMode()         do { ANSELCbits.ANSC6 = 1; } while(0)
#define RC6_SetDigitalMode()        do { ANSELCbits.ANSC6 = 0; } while(0)

// get/set DBG_ISR aliases
#define DBG_ISR_TRIS                 TRISCbits.TRISC7
#define DBG_ISR_LAT                  LATCbits.LATC7
#define DBG_ISR_PORT                 PORTCbits.RC7
#define DBG_ISR_WPU                  WPUCbits.WPUC7
#define DBG_ISR_OD                   ODCONCbits.ODCC7
#define DBG_ISR_ANS                  ANSELCbits.ANSC7
#define DBG_ISR_SetHigh()            do { LATCbits.LATC7 = 1; } while(0)
#define DBG_ISR_SetLow()             do { LATCbits.LATC7 = 0; } while(0)
#define DBG_ISR_Toggle()             do { LATCbits.LATC7 = ~LATCbits.LATC7; } while(0)
#define DBG_ISR_GetValue()           PORTCbits.RC7
#define DBG_ISR_SetDigitalInput()    do { TRISCbits.TRISC7 = 1; } while(0)
#define DBG_ISR_SetDigitalOutput()   do { TRISCbits.TRISC7 = 0; } while(0)
#define DBG_ISR_SetPullup()          do { WPUCbits.WPUC7 = 1; } while(0)
#define DBG_ISR_ResetPullup()        do { WPUCbits.WPUC7 = 0; } while(0)
#define DBG_ISR_SetPushPull()        do { ODCONCbits.ODCC7 = 0; } while(0)
#define DBG_ISR_SetOpenDrain()       do { ODCONCbits.ODCC7 = 1; } while(0)
#define DBG_ISR_SetAnalogMode()      do { ANSELCbits.ANSC7 = 1; } while(0)
#define DBG_ISR_SetDigitalMode()     do { ANSELCbits.ANSC7 = 0; } while(0)

/**
   @Param
    none
   @Returns
    none
   @Description
    GPIO and peripheral I/O initialization
   @Example
    PIN_MANAGER_Initialize();
 */
void PIN_MANAGER_Initialize (void);

/**
 * @Param
    none
 * @Returns
    none
 * @Description
    Interrupt on Change Handling routine
 * @Example
    PIN_MANAGER_IOC();
 */
void PIN_MANAGER_IOC(void);



#endif // PIN_MANAGER_H
/**
 End of File
*/