<!-- Fuente: PIC16-L-F18426-46-Family-Silicon-Errata-and-Data-Sheet-Clarification-80000799.pdf | Convertido con MarkItDown 0.1.7 el 2026-11-11 -->

PIC16(L)F18426/46
PIC16(L)F18426/46 Family Silicon Errata and Data Sheet
Clarification
The PIC16(L)F18426/46 devices that you have received conform functionally to the current device data sheet
(DS40001985C), except for the anomalies described in this document. The silicon issues discussed in the following
pages are for silicon revisions with the Device and Revision IDs listed in the table below. The errata described in this
document will be addressed in future revisions of the PIC16(L)F18426/46 silicon.
Notice: This document summarizes all silicon errata issues from all revisions of silicon, previous as well
CAUTION
as current. Only the issues indicated in the last column of the ‘Silicon Issue Summary’ table apply to the
current silicon revision (A4).
The silicon revision level can be identified using the current version of MPLAB® IDE and Microchip’s programmers,
debuggers, and emulation tools, which are available at the Microchip corporate website (www.microchip.com).
For example, to identify the silicon revision level using MPLAB IDE in conjunction with a hardware debugger:
1. Using the appropriate interface, connect the device to the hardware debugger.
2. Open an MPLAB IDE project.
3. Configure the MPLAB IDE project for the appropriate device and hardware debugger.
4. Based on the version of MPLAB IDE you are using, do one of the following:
a. For MPLAB IDE 8, select Programmer > Reconnect.
b. For MPLAB X IDE, select Window > Dashboard and click the Refresh Debug Tool Status icon ( ).
5. Depending on the development tool used, the part number and Device Revision ID value appear in the Output
window.
Table 1. Silicon Device Identification
Revision ID
Part Number Device ID
A1 A2 A4
PIC16F18426 0x30D2 0x2001 0x2002 0x2004
PIC16LF18426 0x30D3 0x2001 0x2002 0x2004
PIC16F18446 0x30D4 0x2001 0x2002 0x2004
PIC16LF18446 0x30D5 0x2001 0x2002 0x2004
Note: Refer to the Device/Revision ID section in the current “PIC16(L)F184XX Memory Programming Specification” (DS40001970) for detailed
information on Device Identification and Revision IDs for your specific device.
© 2018-2023 Microchip Technology Inc. Errata DS80000799D-page 1
and its subsidiaries

 PIC16(L)F18426/46
Silicon Issue Summary
Affected Revisions
| Module | Feature | Item No. Issue Summary |       |     |
| ------ | ------- | ---------------------- | ----- | --- |
|        |         |                        | A1 A2 | A4  |
ADCC Burst Average mode
ADCC Burst Average while in "Non-Continuous Double
|     |     | 1.1.1 | X X | -   |
| --- | --- | ----- | --- | --- |
mode Sample" mode may not operate
Analog-to-Digital
as intended
Converter With
Computation (ADCC)
An unexpected acquisition time
Double Sample
|     |     | 1.1.2 is added between the first and | X X | X   |
| --- | --- | ------------------------------------ | --- | --- |
Conversion
second conversions
A race condition can cause the
Start and Stop
| I2C |     | 1.2.1 Start and/or Stop flags to be set | X X | X   |
| --- | --- | --------------------------------------- | --- | --- |
Interrupt Functions
when I2C is enabled
| Electrical     | Minimum V DD  | V DD  Min. specifications are     |     |     |
| -------------- | ------------- | --------------------------------- | --- | --- |
|                |               | 1.3.1                             | X X | X   |
| Specifications | Specification | changed for LF devices only       |     |     |
| MSSP           | SPI           | 1.4.1 SSPBUF may become corrupted | X - | -   |
NVMERR bit is set by device
NVM WRERR bit Operation 1.5.1 Reset after being cleared by X - -
software
The PFM endurance is lower
|     | PFM Endurance | 1.6.1 | X X | X   |
| --- | ------------- | ----- | --- | --- |
than specified
Program Flash Memory
(PFM) Repetitive writes may cause
|     | Back to Back Writes | 1.6.2 | X X | -   |
| --- | ------------------- | ----- | --- | --- |
write/erase failures
Capture/
|     | PWM mode | 1.7.1 Duty cycle values are incorrect | X X | -   |
| --- | -------- | ------------------------------------- | --- | --- |
Compare/PWM (CCP)
Module stops working if RST is
Signal Measurement
|     | Reset Bit | 1.8.1 set while prescaler setting is not | X X | X   |
| --- | --------- | ---------------------------------------- | --- | --- |
Timer (SMT)
zero
| Universal    | Synchronous Mode | Loss of second byte written in |     |     |
| ------------ | ---------------- | ------------------------------ | --- | --- |
|              |                  | 1.9.1                          | X X | -   |
| Asynchronous | Transmissions    | TXREG                          |     |     |
Receiver Transmitter
| (UART) | Transmit mode | 1.9.2 Double byte transmit | X X | -   |
| ------ | ------------- | -------------------------- | --- | --- |
Window feature of the WWDT
Windowed Watchdog
|     | Window Operation | 1.10.1 does not operate correctly in | X - | -   |
| --- | ---------------- | ------------------------------------ | --- | --- |
Timer
DOZE mode
Bit 2 of PWRTS[1:0] in
Device Configuration CONFIG2 1.11.1 the CONFIG2 register is not X - -
functional
Note:  Only those issues indicated in the last column apply to the current silicon revision.
© 2018-2023 Microchip Technology Inc.  Errata DS80000799D-page 2
and its subsidiaries

PIC16(L)F18426/46
Silicon Errata Issues
1. Silicon Errata Issues
Notice: This document summarizes all silicon errata issues from all revisions of silicon, previous and
CAUTION
current. Only the issues indicated by the bold font in the following tables apply to the current silicon
revision.
1.1 Module: Analog-to-Digital Converter with Computation (ADCC)
1.1.1 ADCC Burst Average Mode
When the ADCC is operated in Burst Average mode (ADMD = 0b011 in the ADCON2 register) while enabling
noncontinuous operation and double-sampling (ADCONT = 0 in the ADCON0 register and ADDSEN = 1 in the
ADCON1 register), the value in the ADCNT register does not increment beyond ‘0b1’ toward the value in the ADRPT
register.
Work around
When operating the ADCC in Burst Average mode with double-sampling, enable continuous module operation
(ADCONT = 1 in the ADCON0 register) and set the Stop-on-Interrupt bit (the ADSOI bit in the ADCON3 register).
After the interrupt occurs, perform appropriate threshold calculations in the software and retrigger ADCC as
necessary.
Alternatively, if the CPU is in Low-Power Sleep mode, the ADCC in noncontinuous Burst Average mode can be
operated with a single ADC conversion (ADDSEN = 0 in the ADCON1 register). Doing so compromises noise
immunity for lower power consumption by preventing the device from waking up to perform threshold calculations in
the software.
Affected Silicon Revisions
A1 A2 A4
X X —
1.1.2 Double Sample Conversions
When enabling a Double Sample Conversion (DSEN = 1), with no Precharge time (ADPRE = 0) and no Acquisition
time (ADACQ = 0), the maximum number of cycles of acquisition time is inserted prior to the second conversion. The
first conversion will be performed as expected with no Precharge time and no Acquisition time. It is only between the
first and second conversions where a maximum number of cycles of Acquisition time is performed unexpectedly.
Work around
Method 1:
Disable Double Sample Conversion (DSEN = 0) and perform two single conversions back to back.
Method 2:
If adding acquisition time is acceptable, then select no Precharge time, along with the desired Acquisition time.
Affected Silicon Revisions
A1 A2 A4
X X X
© 2018-2023 Microchip Technology Inc. Errata DS80000799D-page 3
and its subsidiaries

PIC16(L)F18426/46
Silicon Errata Issues
1.2 Module: Inter-Integrated Circuit (I2C)
1.2.1 The I2C Start and/or Stop Flags May Be Set When I2C Is Enabled
When I2C is enabled, erroneous Start and/or Stop conditions may be detected. This can generate erroneous I2C
interrupts if enabled.
Work around
Use the following procedure to correctly detect the Start and Stop conditions:
1. Disable the Start and Stop conditions interrupt functions.
2. Enable the I2C module.
3. Wait 250 ns + six instructions cycles (F /4).
OSC
4. Clear the Start and Stop conditions interrupt flags.
5. Enable the Start and Stop conditions interrupt functions if used.
I2CxPIEbits.SCIE = 0; // Disable Start condition interrupt
I2CxPIEbits.PCIE = 0; // Disable Stop condition interrupt
I2CxCON0bits.EN = 1; // Enable I2C
Delay(); // Wait for 250nS + 6 instruction cycles (FOSC/4)
I2CxPIRbits.SCIF = 0; // Clear the Start condition interrupt flags
I2CxPIRbits.PCIF = 0; // Clear the Stop condition interrupt flags
I2CxPIEbits.SCIE = 1; // Enable Start condition interrupt if used
I2CxPIEbits.PCIE = 1; // Enable Stop condition interrupt if used
Affected Silicon Revisions
A1 A2 A4
X X X
1.3 Module: Electrical Specifications
1.3.1 Min V Specification (LF Devices Only)
DD
V specifications are changed for LF devices only at -40°C and 0°C as below.
DDMIN
V for -40°C to 0°C = 2.3V
DDMIN
V for 0°C to 25°C = 2.1V
DDMIN
Work around
None.
Affected Silicon Revisions
A1 A2 A4
X X X
1.4 Module: Host Synchronous Serial Port (MSSP)
1.4.1 MSSP SPI Client Mode
When operating in SPI Client mode, if the incoming SCK clock signal arrives during any of the conditions below, the
SSPBUF Transmit Shift Register (TSR) may become corrupted. The byte transmitted to the client cannot be ensured
to be correct, and the state of the WCOL bit may or may not indicate a write collision.
© 2018-2023 Microchip Technology Inc. Errata DS80000799D-page 4
and its subsidiaries

PIC16(L)F18426/46
Silicon Errata Issues
These conditions include:
• A write to an SFR
• A write to RAM following an SFR read
• A write to RAM before an SFR read
Work around
Method 1 (Interrupt based using SS):
1. Connect the SS line to both the SS input and either an INT or IOC input pin.
2. Enable INT or IOC interrupts (interrupt on falling edge if available, otherwise, check that SS == 0 when the
interrupt occurs).
3. Load SSPBUF with the data to be transmitted.
4. Continue program execution.
5. When invoking the Interrupt Service Routine (ISR), do either of the following:
a. Add a delay that ensures the first SCK clock will be complete, or
b. Poll SSPSTAT.BF (while(BF == 0)), and wait for the transmission/reception to complete.
Method 2 (Bit polling based using SS):
1. Load SSPBUF with the data to be transmitted.
2. Poll the SS line and wait for the SS to go active (while(!PORTx.SS == 0)).
3. When SS is active (SS == 0), do either of the following:
a. Add a delay that ensures the first SCK clock will be complete, or
b. Poll SSPSTAT.BF (while(BF == 0)), and wait for the transmission/reception to complete.
Once one of these two methods is complete, it is safe to return to program execution.
Method 3 (SS not available):
1. Load SSPBUF with the data to be transmitted.
2. Poll SSPSTAT.BF (while(BF == 0)), and wait for the transmission/reception to complete.
Affected Silicon Revisions
A1 A2 A4
X — —
1.5 Module: Nonvolatile Memory (NVM)
1.5.1 WRERR Bit Operation
When a Reset is issued while an NVM high voltage operation is in progress, the WRERR bit in the NVMCON1
register is set as expected. After clearing the WRERR bit, if a Reset reoccurs, the WRERR bit is set again regardless
of whether an NVM operation is in progress or not. A successful write operation will clear the WRERR condition.
Work around
None.
Affected Silicon Revisions
A1 A2 A4
X — —
© 2018-2023 Microchip Technology Inc. Errata DS80000799D-page 5
and its subsidiaries

PIC16(L)F18426/46
Silicon Errata Issues
1.6 Module: Program Flash Memory (PFM)
1.6.1 Endurance of PFM is Lower than Specified
The minimum value for the Program Flash Memory (PFM) endurance specification called out as parameter number
MEM30 is 1K cycles.
Work around
None.
Affected Silicon Revisions
A1 A2 A4
X X X
1.6.2 PFM Back to Back Writes
When repetitive writes to non-volatile memory (Program Flash Memory) are performed, it could result in write/erase
failures at some locations. The issue is due to latent timing in the non-volatile memory controller which can cause the
write instruction to fail under certain conditions.
Work around
To avoid the issue, the customer needs to wait an additional 100 us after the NVMCON1.WR bit has been set,
allowing for the last word to be loaded into the latch. This delay is added only when the NVMCON1.LWLO bit is
cleared in the software.
if(i == (WRITE_FLASH_BLOCKSIZE-1))
{
// Start Flash program memory write
NVMCON1bits.LWLO = 0;
}
NVMCON2 = 0x55;
NVMCON2 = 0xAA;
NVMCON1bits.WR = 1;
if (NVMCON1bits.LWLO==0)
{
__delay_us(100);
}
NOP();
NOP();
writeAddr++;
}
Note: The __delay_us() function uses a #define macro definition. For the intrinsic __delay_us() function to work
correctly, the value of the _XTAL_FREQ must be clearly defined. This macro is defined in the device_config.h file if
the code is generated using MCC. The value of XTAL_FREQ is equal to the system clock frequency.
Affected Silicon Revisions
A1 A2 A4
X X —
© 2018-2023 Microchip Technology Inc. Errata DS80000799D-page 6
and its subsidiaries

 PIC16(L)F18426/46
Silicon Errata Issues
1.7  Module: Pulse-Width Modulation (PWM)
1.7.1  Wrong Duty Cycle for CCP Module
While in PWM mode and the Timer2 prescaler is configured to 1:1, the duty cycle of the PWM output is as expected.
When the Timer2 prescaler is changed to a value other than 1:1, while T2PR = 0 (PWM resolution of two bits), the
expected duty cycle is wrong. The corrected duty cycle values are shown in the table below.
Table 1-1. Corrected Duty Cycle Values
| Prescaler/CCPR |     | 0   | 1   |     | 2   | 3   |     | 4    |
| -------------- | --- | --- | --- | --- | --- | --- | --- | ---- |
| 1:1            |     | 0%  | 25% |     | 50% | 75% |     | 100% |
| 1:2            |     | 50% | 75% |     | 50% | 75% |     | 100% |
| 1:4...1:128    |     | 75% | 75% |     | 75% | 75% |     | 100% |
Work around
None.
Affected Silicon Revisions
|     | A1  |     |     | A2  |     |     | A4  |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
|     | X   |     |     | X   |     |     | —   |     |
1.8  Module: Signal Measurement Timer (SMT)
1.8.1  Reset Bit
If the SMT clock prescaler is set to any value other than '00', setting the RST bit will cause the module to stop
working. The RST bit will remain at the value '1', the counter will not increment, and no interrupts will be generated.
The problem is cleared by turning the module off and on, or by a device reset.
Work around
Method 1:
Do not set the RST bit; manual reset is usually not required for typical operation because the measurement logic will
reset the counter automatically.
Method 2:
Write zero to the counter manually. The module enable or the clock should be disabled when using this method.
Method 3:
Use 1:1 prescaler (PS = 00).
Method 4:
Use the CLKREF subsystem to provide a prescaled clock and set PS = 00.
Affected Silicon Revisions
|     | A1  |     |     | A2  |     |     | A4  |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
|     | X   |     |     | X   |     |     | X   |     |
© 2018-2023 Microchip Technology Inc.  Errata DS80000799D-page 7
and its subsidiaries

PIC16(L)F18426/46
Silicon Errata Issues
1.9 Module: Universal Asynchronous Receiver Transmitter (UART)
1.9.1 Synchronous Mode Transmissions
In synchronous mode, if the TXREG is loaded with a new byte while the EUSART is shifting out the 8th bit of the
previous byte, then only one bit of the new byte is shifted out. After this bit is shifted out, the transmission stops and
the data is lost. If using 9-bit transmission, then this occurs on the 9th bit.
Work around
Write to the TXREG earlier in the transmission or wait for the TXIF flag bit to be set before writing a second byte.
Affected Silicon Revisions
A1 A2 A4
X X —
1.9.2 Double Byte Transmit
Under certain conditions, a byte written to the TXREG register can be transmitted twice. This happens when a byte
is written to TXREG just as the TSR register becomes empty. This new byte is immediately transferred to the TSR
register, but also remains in the TXREG register until the completion of the current instruction cycle. If the new byte
in the TSR register is transmitted before this instruction cycle has completed, the duplicate in the TXREG register will
subsequently be transferred to the TSR register on the following instruction clock cycle and transmitted.
Work around
Method 1:
Monitor the Transmit Interrupt Flag (TXIF) bit. Writes to the TXREG register can be performed once the TXIF bit is
set, indicating that the TXREG register is empty. If using this method, ensure that the second byte is filled in the
TXREG before bit 6 of the first byte is transmitted. If the delay is more than six bit times, there is a possibility of
double byte transmission.
Method 2:
Monitor the TMRT bit of the TXxSTA register. Writes to the TXREG register can be performed once the TMRT bit
is set, indicating that the Transmit Shift Register (TSR) is empty. This work around can be applied if back-to-back
transmissions are not necessary.
Affected Silicon Revisions
A1 A2 A4
X X —
1.10 Module: Windowed Watchdog Timer (WWDT)
1.10.1 Window Operation in Doze Mode
When enabling the Windowed operation mode in Doze mode, a window violation error is issued even though the
window is open and armed. This condition occurs only when the window size is set to a value other than 100% open.
Work around
Method 1:
Use the Windowed operation mode in any mode other than Doze. If disabling the Doze mode is not an option, use
the WWDT module without enabling the window.
Method 2:
© 2018-2023 Microchip Technology Inc. Errata DS80000799D-page 8
and its subsidiaries

PIC16(L)F18426/46
Silicon Errata Issues
If the device is in Doze mode, perform the arming process for the window in Normal mode and return to the Doze
mode.
Method 3:
If there is an Interrupt Service Routine (ISR) in the application code, the arming within the window can be done inside
the ISR with the ROI bit of the CPUDOZE register being set.
Affected Silicon Revisions
A1 A2 A4
X — —
1.11 Module: Device Configuration
1.11.1 PWRTS[1] Power-up Timer Selection Not Implemented
Bit 2 of PWRTS[1:0] in the CONFIG2 register is not functional. This bit is the upper bit of the Power-Up Timer
Selection bits, PWRTS[1:0]. This means that the functions selected by PWRTS = 11 and PWRTS = 10 are not
available.
Work around
The other functions selected by PWRTS = 01 and PWRTS = 00 are available.
Affected Silicon Revisions
A1 A2 A4
X — —
© 2018-2023 Microchip Technology Inc. Errata DS80000799D-page 9
and its subsidiaries

PIC16(L)F18426/46
Data Sheet Clarifications
2. Data Sheet Clarifications
The following typographic corrections and clarifications are to be noted for the latest version of the device data sheet
(DS40001985C):
Note:
Corrections are shown in bold. Where possible, the original bold text formatting has been removed for clarity.
2.1 None
There are no known data sheet clarifications as of this publication date.
© 2018-2023 Microchip Technology Inc. Errata DS80000799D-page 10
and its subsidiaries

PIC16(L)F18426/46
Appendix A: Revision History
3. Appendix A: Revision History
Doc Rev. Date Comments
D 03/2023 Add silicon errata for A2 and A4 which includes: 1.1.2, 1.2.1, 1.6.2, 1.7.1, 1.8.1, 1.9.1, and
1.9.2; Minor editorial updates.
C 11/2020 Updating Electrical Spec. 1.3.1 description and added 1.3.2 Electrical Spec. silicon issue;
Other minor corrections.
B 07/2018 Fixed typo in Table 1.
A 07/2018 Initial document release.
© 2018-2023 Microchip Technology Inc. Errata DS80000799D-page 11
and its subsidiaries

PIC16(L)F18426/46
Microchip Information
The Microchip Website
Microchip provides online support via our website at www.microchip.com/. This website is used to make files and
information easily available to customers. Some of the content available includes:
• Product Support – Data sheets and errata, application notes and sample programs, design resources, user’s
guides and hardware support documents, latest software releases and archived software
• General Technical Support – Frequently Asked Questions (FAQs), technical support requests, online
discussion groups, Microchip design partner program member listing
• Business of Microchip – Product selector and ordering guides, latest Microchip press releases, listing of
seminars and events, listings of Microchip sales offices, distributors and factory representatives
Product Change Notification Service
Microchip’s product change notification service helps keep customers current on Microchip products. Subscribers will
receive email notification whenever there are changes, updates, revisions or errata related to a specified product
family or development tool of interest.
To register, go to www.microchip.com/pcn and follow the registration instructions.
Customer Support
Users of Microchip products can receive assistance through several channels:
• Distributor or Representative
• Local Sales Office
• Embedded Solutions Engineer (ESE)
• Technical Support
Customers should contact their distributor, representative or ESE for support. Local sales offices are also available to
help customers. A listing of sales offices and locations is included in this document.
Technical support is available through the website at: www.microchip.com/support
Microchip Devices Code Protection Feature
Note the following details of the code protection feature on Microchip products:
• Microchip products meet the specifications contained in their particular Microchip Data Sheet.
• Microchip believes that its family of products is secure when used in the intended manner, within operating
specifications, and under normal conditions.
• Microchip values and aggressively protects its intellectual property rights. Attempts to breach the code
protection features of Microchip product is strictly prohibited and may violate the Digital Millennium Copyright
Act.
• Neither Microchip nor any other semiconductor manufacturer can guarantee the security of its code. Code
protection does not mean that we are guaranteeing the product is “unbreakable”. Code protection is constantly
evolving. Microchip is committed to continuously improving the code protection features of our products.
Legal Notice
This publication and the information herein may be used only with Microchip products, including to design, test,
and integrate Microchip products with your application. Use of this information in any other manner violates these
terms. Information regarding device applications is provided only for your convenience and may be superseded
© 2018-2023 Microchip Technology Inc. Errata DS80000799D-page 12
and its subsidiaries

PIC16(L)F18426/46
by updates. It is your responsibility to ensure that your application meets with your specifications. Contact your
local Microchip sales office for additional support or, obtain additional support at www.microchip.com/en-us/support/
design-help/client-support-services.
THIS INFORMATION IS PROVIDED BY MICROCHIP "AS IS". MICROCHIP MAKES NO REPRESENTATIONS
OR WARRANTIES OF ANY KIND WHETHER EXPRESS OR IMPLIED, WRITTEN OR ORAL, STATUTORY
OR OTHERWISE, RELATED TO THE INFORMATION INCLUDING BUT NOT LIMITED TO ANY IMPLIED
WARRANTIES OF NON-INFRINGEMENT, MERCHANTABILITY, AND FITNESS FOR A PARTICULAR PURPOSE,
OR WARRANTIES RELATED TO ITS CONDITION, QUALITY, OR PERFORMANCE.
IN NO EVENT WILL MICROCHIP BE LIABLE FOR ANY INDIRECT, SPECIAL, PUNITIVE, INCIDENTAL, OR
CONSEQUENTIAL LOSS, DAMAGE, COST, OR EXPENSE OF ANY KIND WHATSOEVER RELATED TO THE
INFORMATION OR ITS USE, HOWEVER CAUSED, EVEN IF MICROCHIP HAS BEEN ADVISED OF THE
POSSIBILITY OR THE DAMAGES ARE FORESEEABLE. TO THE FULLEST EXTENT ALLOWED BY LAW,
MICROCHIP'S TOTAL LIABILITY ON ALL CLAIMS IN ANY WAY RELATED TO THE INFORMATION OR ITS USE
WILL NOT EXCEED THE AMOUNT OF FEES, IF ANY, THAT YOU HAVE PAID DIRECTLY TO MICROCHIP FOR
THE INFORMATION.
Use of Microchip devices in life support and/or safety applications is entirely at the buyer's risk, and the buyer agrees
to defend, indemnify and hold harmless Microchip from any and all damages, claims, suits, or expenses resulting
from such use. No licenses are conveyed, implicitly or otherwise, under any Microchip intellectual property rights
unless otherwise stated.
Trademarks
The Microchip name and logo, the Microchip logo, Adaptec, AVR, AVR logo, AVR Freaks, BesTime, BitCloud,
CryptoMemory, CryptoRF, dsPIC, flexPWR, HELDO, IGLOO, JukeBlox, KeeLoq, Kleer, LANCheck, LinkMD,
maXStylus, maXTouch, MediaLB, megaAVR, Microsemi, Microsemi logo, MOST, MOST logo, MPLAB, OptoLyzer,
PIC, picoPower, PICSTART, PIC32 logo, PolarFire, Prochip Designer, QTouch, SAM-BA, SenGenuity, SpyNIC, SST,
SST Logo, SuperFlash, Symmetricom, SyncServer, Tachyon, TimeSource, tinyAVR, UNI/O, Vectron, and XMEGA are
registered trademarks of Microchip Technology Incorporated in the U.S.A. and other countries.
AgileSwitch, APT, ClockWorks, The Embedded Control Solutions Company, EtherSynch, Flashtec, Hyper Speed
Control, HyperLight Load, Libero, motorBench, mTouch, Powermite 3, Precision Edge, ProASIC, ProASIC Plus,
ProASIC Plus logo, Quiet- Wire, SmartFusion, SyncWorld, Temux, TimeCesium, TimeHub, TimePictra, TimeProvider,
TrueTime, and ZL are registered trademarks of Microchip Technology Incorporated in the U.S.A.
Adjacent Key Suppression, AKS, Analog-for-the-Digital Age, Any Capacitor, AnyIn, AnyOut, Augmented Switching,
BlueSky, BodyCom, Clockstudio, CodeGuard, CryptoAuthentication, CryptoAutomotive, CryptoCompanion,
CryptoController, dsPICDEM, dsPICDEM.net, Dynamic Average Matching, DAM, ECAN, Espresso T1S,
EtherGREEN, GridTime, IdealBridge, In-Circuit Serial Programming, ICSP, INICnet, Intelligent Paralleling, IntelliMOS,
Inter-Chip Connectivity, JitterBlocker, Knob-on-Display, KoD, maxCrypto, maxView, memBrain, Mindi, MiWi, MPASM,
MPF, MPLAB Certified logo, MPLIB, MPLINK, MultiTRAK, NetDetach, Omniscient Code Generation, PICDEM,
PICDEM.net, PICkit, PICtail, PowerSmart, PureSilicon, QMatrix, REAL ICE, Ripple Blocker, RTAX, RTG4, SAM-
ICE, Serial Quad I/O, simpleMAP, SimpliPHY, SmartBuffer, SmartHLS, SMART-I.S., storClad, SQI, SuperSwitcher,
SuperSwitcher II, Switchtec, SynchroPHY, Total Endurance, Trusted Time, TSHARC, USBCheck, VariSense,
VectorBlox, VeriPHY, ViewSpan, WiperLock, XpressConnect, and ZENA are trademarks of Microchip Technology
Incorporated in the U.S.A. and other countries.
SQTP is a service mark of Microchip Technology Incorporated in the U.S.A.
The Adaptec logo, Frequency on Demand, Silicon Storage Technology, and Symmcom are registered trademarks of
Microchip Technology Inc. in other countries.
GestIC is a registered trademark of Microchip Technology Germany II GmbH & Co. KG, a subsidiary of Microchip
Technology Inc., in other countries.
All other trademarks mentioned herein are property of their respective companies.
© 2018-2023, Microchip Technology Incorporated and its subsidiaries. All Rights Reserved.
ISBN: 978-1-6683-2289-5
© 2018-2023 Microchip Technology Inc. Errata DS80000799D-page 13
and its subsidiaries

PIC16(L)F18426/46
Quality Management System
For information regarding Microchip’s Quality Management Systems, please visit www.microchip.com/quality.
© 2018-2023 Microchip Technology Inc. Errata DS80000799D-page 14
and its subsidiaries

Worldwide Sales and Service
| AMERICAS | ASIA/PACIFIC | ASIA/PACIFIC | EUROPE |
| -------- | ------------ | ------------ | ------ |
Corporate Office Australia - Sydney India - Bangalore Austria - Wels
2355 West Chandler Blvd. Tel: 61-2-9868-6733 Tel: 91-80-3090-4444 Tel: 43-7242-2244-39
Chandler, AZ 85224-6199 China - Beijing India - New Delhi Fax: 43-7242-2244-393
Tel: 480-792-7200 Tel: 86-10-8569-7000 Tel: 91-11-4160-8631 Denmark - Copenhagen
Fax: 480-792-7277 China - Chengdu India - Pune Tel: 45-4485-5910
Technical Support: Tel: 86-28-8665-5511 Tel: 91-20-4121-0141 Fax: 45-4485-2829
www.microchip.com/support China - Chongqing Japan - Osaka Finland - Espoo
Web Address: Tel: 86-23-8980-9588 Tel: 81-6-6152-7160 Tel: 358-9-4520-820
www.microchip.com China - Dongguan Japan - Tokyo France - Paris
Atlanta Tel: 86-769-8702-9880 Tel: 81-3-6880- 3770 Tel: 33-1-69-53-63-20
Duluth, GA China - Guangzhou Korea - Daegu Fax: 33-1-69-30-90-79
Tel: 678-957-9614 Tel: 86-20-8755-8029 Tel: 82-53-744-4301 Germany - Garching
Fax: 678-957-1455 China - Hangzhou Korea - Seoul Tel: 49-8931-9700
Austin, TX Tel: 86-571-8792-8115 Tel: 82-2-554-7200 Germany - Haan
Tel: 512-257-3370 China - Hong Kong SAR Malaysia - Kuala Lumpur Tel: 49-2129-3766400
Boston Tel: 852-2943-5100 Tel: 60-3-7651-7906 Germany - Heilbronn
Westborough, MA China - Nanjing Malaysia - Penang Tel: 49-7131-72400
Tel: 774-760-0087 Tel: 86-25-8473-2460 Tel: 60-4-227-8870 Germany - Karlsruhe
Fax: 774-760-0088 China - Qingdao Philippines - Manila Tel: 49-721-625370
Chicago Tel: 86-532-8502-7355 Tel: 63-2-634-9065 Germany - Munich
| Itasca, IL | China - Shanghai | Singapore | Tel: 49-89-627-144-0 |
| ---------- | ---------------- | --------- | -------------------- |
Tel: 630-285-0071 Tel: 86-21-3326-8000 Tel: 65-6334-8870 Fax: 49-89-627-144-44
Fax: 630-285-0075 China - Shenyang Taiwan - Hsin Chu Germany - Rosenheim
Dallas Tel: 86-24-2334-2829 Tel: 886-3-577-8366 Tel: 49-8031-354-560
Addison, TX China - Shenzhen Taiwan - Kaohsiung Israel - Ra’anana
Tel: 972-818-7423 Tel: 86-755-8864-2200 Tel: 886-7-213-7830 Tel: 972-9-744-7705
Fax: 972-818-2924 China - Suzhou Taiwan - Taipei Italy - Milan
Detroit Tel: 86-186-6233-1526 Tel: 886-2-2508-8600 Tel: 39-0331-742611
Novi, MI China - Wuhan Thailand - Bangkok Fax: 39-0331-466781
Tel: 248-848-4000 Tel: 86-27-5980-5300 Tel: 66-2-694-1351 Italy - Padova
Houston, TX China - Xian Vietnam - Ho Chi Minh Tel: 39-049-7625286
Tel: 281-894-5983 Tel: 86-29-8833-7252 Tel: 84-28-5448-2100 Netherlands - Drunen
| Indianapolis      | China - Xiamen      |     | Tel: 31-416-690399   |
| ----------------- | ------------------- | --- | -------------------- |
| Noblesville, IN   | Tel: 86-592-2388138 |     | Fax: 31-416-690340   |
| Tel: 317-773-8323 | China - Zhuhai      |     | Norway - Trondheim   |
| Fax: 317-773-5453 | Tel: 86-756-3210040 |     | Tel: 47-72884388     |
| Tel: 317-536-2380 |                     |     | Poland - Warsaw      |
| Los Angeles       |                     |     | Tel: 48-22-3325737   |
| Mission Viejo, CA |                     |     | Romania - Bucharest  |
| Tel: 949-462-9523 |                     |     | Tel: 40-21-407-87-50 |
| Fax: 949-462-9608 |                     |     | Spain - Madrid       |
| Tel: 951-273-7800 |                     |     | Tel: 34-91-708-08-90 |
| Raleigh, NC       |                     |     | Fax: 34-91-708-08-91 |
| Tel: 919-844-7510 |                     |     | Sweden - Gothenberg  |
| New York, NY      |                     |     | Tel: 46-31-704-60-40 |
| Tel: 631-435-6000 |                     |     | Sweden - Stockholm   |
| San Jose, CA      |                     |     | Tel: 46-8-5090-4654  |
| Tel: 408-735-9110 |                     |     | UK - Wokingham       |
| Tel: 408-436-4270 |                     |     | Tel: 44-118-921-5800 |
| Canada - Toronto  |                     |     | Fax: 44-118-921-5820 |
Tel: 905-695-1980
Fax: 905-695-2078
© 2018-2023 Microchip Technology Inc.  Errata DS80000799D-page 15
and its subsidiaries
