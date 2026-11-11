<!-- Fuente: MPLAB Snap In-Circuit Debugger IS DS50002787A.pdf | Convertido con MarkItDown 0.1.7 el 2026-11-11 -->

MPLAB® SNAP IN-CIRCUIT
DEBUGGER
®
MPLAB Snap In-Circuit Debugger Information Sheet
INTRODUCTION
The MPLAB® Snap In-Circuit Debugger (PG164100) is an ultra-low priced debugging
solution for projects not requiring high-voltage programming or advanced debug
features. Therefore, it supports many of Microchip’s newer MCU offerings but not some
legacy products. With a nominal feature set, the debugger is geared toward developers
who don’t require advanced features. It is not intended for production programming.
Note: Refer to the MPLAB® PICkit™ 4 In-Circuit Debugger and the MPLAB X IDE
User’s Guides or online help for additional information.
• Description
• Features
• MPLAB Snap In-Circuit Debugger Components
• Additional Items Needed
• MPLAB Snap vs. MPLAB PICkit 4 Comparison
• Pinout Information
• LEDs
• Debugger to Target Communication
• Debugger Options Selection
• Troubleshooting
DESCRIPTION
The MPLAB Snap In-Circuit Debugger allows fast and easy debugging and
programming using the powerful graphical user interface of MPLAB X IDE (Integrated
Development Environment) or MPLAB IPE (Integrated Programming Environment).
The debugger works with Microchip PIC®, dsPIC® Flash, AVR®, or DSC® devices. It
will also work with 32-bit based microcontroller, such as SAM, CEC and PIC32 devices.
The MPLAB Snap connects to the computer using a high-speed 2.0 USB interface and
connects to the target via a Microchip debug 8-pin Single In-Line (SIL) connector. The
SIL connector uses two device I/O pins and the reset line to implement in-circuit
debugging and In-Circuit Serial Programming™ (ICSP™).
The MPLAB Snap supports advanced interfaces such as 4-wire JTAG and Serial Wire
Debug with streaming Data Gateway, while being backward compatible for demo
boards, headers and target systems using 2-wire JTAG and ICSP.
The debugger system executes code like an actual device because it uses the target
device’s built-in emulation circuitry, instead of a special debugger chip. All available
features of a given device are accessible interactively and can be set and modified by
the MPLAB X IDE interface.
The MPLAB Snap In-Circuit Debugger is compatible with Microsoft Windows® 7 or
later, Linux® and macOS™ platforms.
 2018 Microchip Technology Inc. DS50002787A-page 1

®
MPLAB Snap In-Circuit Debugger
FEATURES
Features/Capabilities:
• Connects to computer via high-speed USB 2.0 (480 Mbits/s) cable
• An 8-pin SIL programming connector and the option to use various interfaces
• Programs devices using MPLAB X IDE or MPLAB IPE
• Works with many Microchip PIC, dsPIC, AVR, or DSC devices, including 32-bit
microcontrollers such as SAM, CEC and PIC32 devices (refer to the device
support list found on your PC, for example, C:\Program Files (X86)\Microchip\
MPLABX\vx.xx\docs\Device Support.htm, where vx.xx is the version of MPLAB X
IDE)
• Supports 4-wire JTAG and Serial Wire Debug
• Backward compatibility for demo boards, headers and target systems using 2-wire
JTAG and ICSP (In-Circuit Serial Programming)
• Supports multiple hardware and software breakpoints, stopwatch and source
code file debugging
• Debugs your application on your own hardware in real time
• Sets breakpoints based on internal events
• Debugs at full target MCU speed
• Configures pin drivers
• Adds new device support and features by installing the latest version of MPLAB X
IDE (available as a free download at http://www.microchip.com/mplabx/)
• Indicates debugger status via the Active and Status LEDs
Performance/Speed:
• No firmware download delays incurred when switching devices
• 32-bit microcontroller using an ARM® Cortex®-M7 core running at 300 MHz
Safety:
• RoHS, CE, and China E compliant
• Supports target supply voltages from 1.2V to 5.5V +/-10%
Note: The MPLAB Snap In-Circuit Debugger is powered through its Micro-B USB
connector. The target board must be powered from its own power supply.
DS50002787A-page 2  2018 Microchip Technology Inc.

MPLAB® Snap In-Circuit Debugger
MPLAB SNAP IN-CIRCUIT DEBUGGER COMPONENTS
The components of the MPLAB Snap In-Circuit Debugger system are:
• an 8-pin SIL connector
• a Micro-B USB connector
• two LEDs
• Emergency Recovery Jumper (not populated)
FIGURE 1-1: MPLAB® SNAP IN-CIRCUIT DEBUGGER
ADDITIONAL ITEMS NEEDED
To use the MPLAB Snap In-Circuit Debugger, you will need to supply:
• a full-featured Micro-B USB cable (data and power), no longer than 1.5 meter, to
connect to a computer (for example, the Microchip Part Number
ATUSBMICROCABLE-XPRO)
• target board
• power supply for target board
 2018 Microchip Technology Inc. DS50002787A-page 3

®
 MPLAB Snap In-Circuit Debugger
• any wiring interfaces or cables needed for your application, some available
adapters and cables include:
- AC164110 - RJ-11 to ICSP Adapter
- AC002021 PM3 ICSP cable
• jumper, wire or tweezers for emergency recovery, if needed
MPLAB SNAP VS. MPLAB PICKIT 4 COMPARISON
The following table compares the MPLAB Snap to the PICkit 4.
| TABLE 1-1:                | FEATURES COMPARISON |                 |            |                |
| ------------------------- | ------------------- | --------------- | ---------- | -------------- |
|                           | Feature             |                 | MPLAB Snap | MPLAB PICkit 4 |
| Enclosure                 |                     | No, exposed PCB |            | Yes            |
| USB Powered               |                     | Yes             |            | Yes            |
| USB Speed                 |                     | High            |            | High           |
| USB Cable supplied        |                     | No              |            | Yes            |
| Programmable VPP          |                     | No              |            | Yes            |
| Programmable VDD          |                     | No              |            | Yes            |
| Emulator Power            |                     | No              |            | Yes            |
| Power to Target           |                     | No              |            | Yes - 50 mA    |
| Voltage Monitoring        |                     | No              |            | Yes            |
| Current Sensing           |                     | No              |            | Yes            |
| Target Power              |                     | Yes             |            | Yes            |
| Target Voltage Boost      |                     | No              |            | Yes            |
| RGB Indicators            |                     | LED             |            | Yes            |
| Software Breakpoints      |                     | Yes             |            | Yes            |
| Breakpoints               |                     | Complex         |            | Complex        |
| Buffered Pin Drivers      |                     | Yes             |            | Yes            |
| Configurable pull-ups     |                     | No              |            | Yes            |
| Drag and Drop Programming |                     | Yes             |            | Yes            |
| Programmer to Go          |                     | No              |            | Yes            |
| Production Programmer     |                     | No              |            | Yes            |
| Products Supported        |                     | Most Flash MCUs |            | All Flash MCUs |
| Pay-Per-Feature           |                     | No              |            | Yes            |
| I2C DGI                   |                     | Yes             |            | Yes            |
| CDD UART                  |                     | Yes             |            | Yes            |
| SEE configuration (boot)  |                     | Yes             |            | Yes            |
| SPI DGI                   |                     | Yes             |            | Yes            |
| USART DGI                 |                     | Yes             |            | Yes            |
| USB Serialization         |                     | Yes             |            | Yes            |
| Recovery Method           |                     | PCB pads        |            | Pushbutton     |
.
| TABLE 1-2:       | INTERFACES COMPARISON |            |     |                |
| ---------------- | --------------------- | ---------- | --- | -------------- |
|                  | Interface             | MPLAB Snap |     | MPLAB PICkit 4 |
| ICSP             |                       | Yes        |     | Yes            |
| MIPS EJTAG 2wire |                       | Yes        |     | Yes            |
DS50002787A-page 4  2018 Microchip Technology Inc.

MPLAB® Snap In-Circuit Debugger
| TABLE 1-2:       |           | INTERFACES COMPARISON (CONTINUED) |                       |            |     |                |
| ---------------- | --------- | --------------------------------- | --------------------- | ---------- | --- | -------------- |
|                  | Interface |                                   |                       | MPLAB Snap |     | MPLAB PICkit 4 |
| MIPS EJTAG 4wire |           |                                   | Yes                   |            |     | Yes            |
| ARM SWD          |           |                                   | Yes                   |            |     | Yes            |
| AVR32 JTAG 4wire |           |                                   | Yes                   |            |     | Yes            |
| PDI              |           |                                   | Yes, low voltage only |            |     | Yes            |
| UPDI             |           |                                   | Yes, low voltage only |            |     | Yes            |
| UPDI/HV          |           |                                   | No                    |            |     | Yes            |
| TPI              |           |                                   | Yes                   |            |     | Yes            |
| ISP Programming  |           |                                   | Yes                   |            |     | Yes            |
| DEBUGWIRE        |           |                                   | Yes                   |            |     | Yes            |
| AWIRE            |           |                                   | Yes                   |            |     | Yes            |
PINOUT INFORMATION
The pinouts for the MPLAB Snap are the same as the MPLAB PICkit 4 In-Circuit
Debugger. Refer to the MPLAB PICkit 4 online help in MPLAB X IDE (Help>Tool Help
Contents>PICkit 4 Help) for more information.
| FIGURE 1-2: |     | MPLAB SNAP PINOUTS |     |     |     |     |
| ----------- | --- | ------------------ | --- | --- | --- | --- |
MPLAB Snap Pin Description*
1
1 = MCLR
2
|     |     |     |     | 3   | 2 = VDD  |     |
| --- | --- | --- | --- | --- | -------- | --- |
4
MPLAB Snap
|     |     |     |     | 5   | 3 = Ground |     |
| --- | --- | --- | --- | --- | ---------- | --- |
6
|     |     |     |     | 7   | 4 = PGD |     |
| --- | --- | --- | --- | --- | ------- | --- |
8
5 = PGC
6 = Do not connect
7 = Unused
8 = Unused
LEDS
The MPLAB Snap has two fixed color LEDs. The Active LED is green and the Status
LED is yellow. The expected start-up LED sequence for the MPLAB Snap debugger is:
Green - steady on, yellow off. The debugger is ready.
The LEDs have the following significance.
| TABLE 1-3:  |     | NORMAL MODES LED DESCRIPTIONS |                                                 |     |             |     |
| ----------- | --- | ----------------------------- | ----------------------------------------------- | --- | ----------- | --- |
| LED         |     | Color                         |                                                 |     | Description |     |
| Active, on  |     | Green                         | Power is connected; debugger in standby.        |     |             |     |
| Status, on  |     | Yellow                        | Debugger is busy; activity during an operation. |     |             |     |
(or pulsing
activity)
 2018 Microchip Technology Inc. DS50002787A-page 5

®
MPLAB Snap In-Circuit Debugger
The following table provides LED descriptions for errors.
TABLE 1-4: ERROR LED DESCRIPTIONS
Errors Description
Status, on 3 seconds Bootloader problem accessing he serial EEPROM.
Status, on 10 seconds API commands cannot be processed by the Bootloader.
Active and Status, fast A runtime exception occurred in the tool firmware.
blink (alternating)
Active and Status, fast A runtime exception occurred in the Bootloader.
blink (in tandem)
DEBUGGER TO TARGET COMMUNICATION
Note: The MPLAB X IDE software must be installed prior to connecting the
MPLAB Snap In-Circuit Debugger.
The debugger is connected to the computer via a USB cable for communication and
debugger power.
The debugger is connected to the target application for communication and data
collection and optional debugger power.
CAUTION
Communication Failure.
Do not connect the hardware before installing the software and
USB drivers.
CAUTION
Debugger or Target Damage.
Do not change hardware connections while the debugger or target
is powered.
Note: Refer to the MPLAB PICkit 4 In-Circuit Debugger online help or user’s
guide for information on target communication connections, debugging,
requirements for debugging, programming, troubleshooting, etc.
DS50002787A-page 6  2018 Microchip Technology Inc.

MPLAB® Snap In-Circuit Debugger
The following figure shows a typical connection for the MPLAB Snap debugger.
FIGURE 1-3: MPLAB SNAP CONNECTIONS
DEBUGGER OPTIONS SELECTION
The MPLAB Snap project properties available in MPLAB X IDE are a subset of the
MPLAB PICkit 4 options.
Debugger options are set in the Project Properties dialog of MPLAB X IDE. Click on
Snap under “Categories” to display the “Options for Snap” (see Figure1-4). Use the
“Options categories” drop-down list to select various options. Click on an option name
to see its description in the Option Description box below. Click to the right of an option
name to select or change it.
Note: The available option categories and the options within those categories are
dependent on the device you have selected.
FIGURE 1-4: MPLAB X IDE OPTIONS FOR MPLAB SNAP
After setting the options, click Apply or OK. Also click the Refresh Debug Tool status
icon in the MPLAB X IDE dashboard display to update any changes made.
 2018 Microchip Technology Inc. DS50002787A-page 7

®
MPLAB Snap In-Circuit Debugger
For the MPLAB IPE, the options for MPLAB Snap are located in Settings>Advance
Mode>Settings. Refer to MPLAB IPE online help for more information.
The possible option categories may include:
• Memories to Program
• Debug Options
• Program Options
• Freeze Peripherals
• Power
• Firmware
TROUBLESHOOTING
If you are having problems with MPLAB Snap In-Circuit Debugger operation, start here.
Refer to the MPLAB PICkit 4 online help section on Troubleshooting First Steps. From
there you can navigate to “Some Questions to Answer First” and “Top Reasons Why
You Can’t Debug.” For general issues, invoking the bootloader mode and the
emergency boot firmware recovery, see the following sections.
General
1. It is possible the error was a one-time event. Try the operation again.
2. There may be a problem programming in general. As a test, switch to Run mode
in MPLAB X IDE using the icon and program the target with the simplest
application possible (e.g., a program to blink an LED). If the program will not run,
then you know that something is wrong with the target setup.
3. It is possible that the target device has been damaged in some way (e.g., over
current.) Development environments are notoriously hostile to components.
Consider trying another target board.
4. Microchip Technology Inc. offers demonstration boards to support most of its
microcontrollers. Consider using one of these applications, which are known to
work, to verify correct MPLAB Snap In-Circuit Debugger functionality.
5. Review debugger setup to ensure proper application setup. For more informa-
tion, see the “Operation” section of the MPLAB PICkit 4 help or PDF.
6. Your program speed may be set too high for your circuit. In MPLAB X IDE, go to
File>Project Properties, select Snap in Categories, then Program Options in
Option categories, Program Speed and select a slower speed from the
drop-down menu. The default is Normal. In MPLAB IPE, the Program Speed
option can be found in the Advanced Mode, Settings tab.
7. There may be certain situations where the debugger is not operating properly
and needs to be reprogrammed. See the following section.
DS50002787A-page 8  2018 Microchip Technology Inc.

MPLAB® Snap In-Circuit Debugger
The Hardware Tool Emergency Boot Firmware Recovery Utility
WARNING
Only use this utility to restore hardware tool boot firmware to its factory state.
Use only if your hardware tool no longer functions on any machine.
The debugger may need to be forced into recovery boot mode (reprogrammed) in rare
situations. For example, if none of the LEDs are lit when the debugger is connected to
the computer.
YOU MUST USE MPLAB X IDE V5.05 OR GREATER TO USE THE EMERGENCY
RECOVERY UTILITY FOR THE MPLAB SNAP.
Carefully follow the instructions found in MPLAB X IDE under the main menu
option Debug>Hardware Tool Emergency Boot Firmware Recovery. After the Warning
screen, select MPLAB Snap.
FIGURE 1-5: SELECTING EMERGENCY UTILITY
Figure1-6 shows where the emergency recovery jumper is located on the board.
FIGURE 1-6: EMERGENCY RECOVERY JUMPER
If the procedure was successful, the recovery wizard displays a success screen. The
MPLAB Snap will now be operational and able to communicate with the MPLAB X IDE.
If the procedure fails, try it again. If it fails a second time, contact Microchip Support at
http://support.microchip.com.
 2018 Microchip Technology Inc. DS50002787A-page 9

®
MPLAB Snap In-Circuit Debugger
NOTES:
DS50002787A-page 10  2018 Microchip Technology Inc.

Note the following details of the code protection feature on Microchip devices:
• Microchip products meet the specification contained in their particular Microchip Data Sheet.
• Microchip believes that its family of products is one of the most secure families of its kind on the market today, when used in the
intended manner and under normal conditions.
• There are dishonest and possibly illegal methods used to breach the code protection feature. All of these methods, to our
knowledge, require using the Microchip products in a manner outside the operating specifications contained in Microchip’s Data
Sheets. Most likely, the person doing so is engaged in theft of intellectual property.
• Microchip is willing to work with the customer who is concerned about the integrity of their code.
• Neither Microchip nor any other semiconductor manufacturer can guarantee the security of their code. Code protection does not
mean that we are guaranteeing the product as “unbreakable.”
Code protection is constantly evolving. We at Microchip are committed to continuously improving the code protection features of our
products. Attempts to break Microchip’s code protection feature may be a violation of the Digital Millennium Copyright Act. If such acts
allow unauthorized access to your software or other copyrighted work, you may have a right to sue for relief under that Act.
Information contained in this publication regarding device Trademarks
applications and the like is provided only for your convenience The Microchip name and logo, the Microchip logo, AnyRate, AVR,
and may be superseded by updates. It is your responsibility to AVR logo, AVR Freaks, BitCloud, chipKIT, chipKIT logo,
ensure that your application meets with your specifications. CryptoMemory, CryptoRF, dsPIC, FlashFlex, flexPWR, Heldo,
MICROCHIP MAKES NO REPRESENTATIONS OR JukeBlox, KeeLoq, Kleer, LANCheck, LINK MD, maXStylus,
WARRANTIES OF ANY KIND WHETHER EXPRESS OR maXTouch, MediaLB, megaAVR, MOST, MOST logo, MPLAB,
IMPLIED, WRITTEN OR ORAL, STATUTORY OR OptoLyzer, PIC, picoPower, PICSTART, PIC32 logo, Prochip
OTHERWISE, RELATED TO THE INFORMATION, Designer, QTouch, SAM-BA, SpyNIC, SST, SST Logo,
INCLUDING BUT NOT LIMITED TO ITS CONDITION, SuperFlash, tinyAVR, UNI/O, and XMEGA are registered
QUALITY, PERFORMANCE, MERCHANTABILITY OR trademarks of Microchip Technology Incorporated in the U.S.A.
FITNESS FOR PURPOSE. Microchip disclaims all liability and other countries.
arising from this information and its use. Use of Microchip ClockWorks, The Embedded Control Solutions Company,
devices in life support and/or safety applications is entirely at EtherSynch, Hyper Speed Control, HyperLight Load, IntelliMOS,
the buyer’s risk, and the buyer agrees to defend, indemnify and mTouch, Precision Edge, and Quiet-Wire are registered
hold harmless Microchip from any and all damages, claims, trademarks of Microchip Technology Incorporated in the U.S.A.
suits, or expenses resulting from such use. No licenses are Adjacent Key Suppression, AKS, Analog-for-the-Digital Age, Any
conveyed, implicitly or otherwise, under any Microchip Capacitor, AnyIn, AnyOut, BodyCom, CodeGuard,
intellectual property rights unless otherwise stated. CryptoAuthentication, CryptoAutomotive, CryptoCompanion,
CryptoController, dsPICDEM, dsPICDEM.net, Dynamic Average
AMBA, Arm, Arm7, Arm7TDMI, Arm9, Arm11, Artisan, Matching, DAM, ECAN, EtherGREEN, In-Circuit Serial
big.LITTLE, Cordio, CoreLink, CoreSight, Cortex, Design- Programming, ICSP, INICnet, Inter-Chip Connectivity,
Start, DynamIQ, Jazelle, Keil, Mali, Mbed, Mbed Enabled, JitterBlocker, KleerNet, KleerNet logo, memBrain, Mindi, MiWi,
NEON, POP, RealView, SecurCore, Socrates, Thumb, Trust- motorBench, MPASM, MPF, MPLAB Certified logo, MPLIB,
Zone, ULINK, ULINK2, ULINK-ME, ULINK-PLUS, ULINKpro, MPLINK, MultiTRAK, NetDetach, Omniscient Code Generation,
PICDEM, PICDEM.net, PICkit, PICtail, PowerSmart, PureSilicon,
µVision, Versatile are trademarks or registered trademarks of
QMatrix, REAL ICE, Ripple Blocker, SAM-ICE, Serial Quad I/O,
Arm Limited (or its subsidiaries) in the US and/or elsewhere.
SMART-I.S., SQI, SuperSwitcher, SuperSwitcher II, Total
Endurance, TSHARC, USBCheck, VariSense, ViewSpan,
WiperLock, Wireless DNA, and ZENA are trademarks of
Microchip Technology Incorporated in the U.S.A. and other
countries.
Microchip received ISO/TS-16949:2009 certification for its worldwide SQTP is a service mark of Microchip Technology Incorporated in
headquarters, design and wafer fabrication facilities in Chandler and the U.S.A.
Tempe, Arizona; Gresham, Oregon and design centers in California
and India. The Company’s quality system processes and procedures Silicon Storage Technology is a registered trademark of Microchip
are for its PIC® MCUs and dsPIC® DSCs, KEELOQ® code hopping Technology Inc. in other countries.
devices, Serial EEPROMs, microperipherals, nonvolatile memory and
GestIC is a registered trademark of Microchip Technology
analog products. In addition, Microchip’s quality system for the design
and manufacture of development systems is ISO 9001:2000 certified. Germany II GmbH & Co. KG, a subsidiary of Microchip
Technology Inc., in other countries.
All other trademarks mentioned herein are property of their
QUALITY MANAGEMENT SYSTEM respective companies.
© 2018, Microchip Technology Incorporated, All Rights Reserved.
CERTIFIED BY DNV
ISBN: 978-1-5224-3335-4
== ISO/TS 16949 ==
 2018 Microchip Technology Inc. DS50002787A-page 11

Worldwide Sales and Service
| AMERICAS | ASIA/PACIFIC | ASIA/PACIFIC | EUROPE |
| -------- | ------------ | ------------ | ------ |
Corporate Office Australia - Sydney India - Bangalore Austria - Wels
2355 West Chandler Blvd. Tel: 61-2-9868-6733 Tel: 91-80-3090-4444  Tel: 43-7242-2244-39
| Chandler, AZ 85224-6199 |                 |                   | Fax: 43-7242-2244-393 |
| ----------------------- | --------------- | ----------------- | --------------------- |
|                         | China - Beijing | India - New Delhi |                       |
Tel: 480-792-7200
|     | Tel: 86-10-8569-7000  | Tel: 91-11-4160-8631 | Denmark - Copenhagen |
| --- | --------------------- | -------------------- | -------------------- |
Fax: 480-792-7277
|     | China - Chengdu | India - Pune | Tel: 45-4450-2828  |
| --- | --------------- | ------------ | ------------------ |
Technical Support:
|     | Tel: 86-28-8665-5511 | Tel: 91-20-4121-0141 | Fax: 45-4485-2829 |
| --- | -------------------- | -------------------- | ----------------- |
http://www.microchip.com/
Finland - Espoo
| support | China - Chongqing    | Japan - Osaka        |                     |
| ------- | -------------------- | -------------------- | ------------------- |
|         | Tel: 86-23-8980-9588 | Tel: 81-6-6152-7160  | Tel: 358-9-4520-820 |
Web Address:
www.microchip.com China - Dongguan Japan - Tokyo France - Paris
Tel: 33-1-69-53-63-20
|         | Tel: 86-769-8702-9880  | Tel: 81-3-6880- 3770  |                        |
| ------- | ---------------------- | --------------------- | ---------------------- |
| Atlanta |                        |                       | Fax: 33-1-69-30-90-79  |
|         | China - Guangzhou      | Korea - Daegu         |                        |
Duluth, GA
|     | Tel: 86-20-8755-8029  | Tel: 82-53-744-4301 | Germany - Garching |
| --- | --------------------- | ------------------- | ------------------ |
Tel: 678-957-9614
Tel: 49-8931-9700
| Fax: 678-957-1455 | China - Hangzhou | Korea - Seoul |     |
| ----------------- | ---------------- | ------------- | --- |
Germany - Haan
| Austin, TX | Tel: 86-571-8792-8115  | Tel: 82-2-554-7200 |     |
| ---------- | ---------------------- | ------------------ | --- |
Tel: 49-2129-3766400
Tel: 512-257-3370  China - Hong Kong SAR Malaysia - Kuala Lumpur
|     | Tel: 852-2943-5100  | Tel: 60-3-7651-7906 | Germany - Heilbronn |
| --- | ------------------- | ------------------- | ------------------- |
Boston
| Westborough, MA  |                 |                   | Tel: 49-7131-67-3636 |
| ---------------- | --------------- | ----------------- | -------------------- |
|                  | China - Nanjing | Malaysia - Penang |                      |
Tel: 774-760-0087  Tel: 86-25-8473-2460 Tel: 60-4-227-8870 Germany - Karlsruhe
| Fax: 774-760-0088 |                 |                      | Tel: 49-721-625370 |
| ----------------- | --------------- | -------------------- | ------------------ |
|                   | China - Qingdao | Philippines - Manila |                    |
Chicago Tel: 86-532-8502-7355 Tel: 63-2-634-9065 Germany - Munich
Tel: 49-89-627-144-0
| Itasca, IL  | China - Shanghai | Singapore |     |
| ----------- | ---------------- | --------- | --- |
Fax: 49-89-627-144-44
| Tel: 630-285-0071  | Tel: 86-21-3326-8000   | Tel: 65-6334-8870   |                      |
| ------------------ | ---------------------- | ------------------- | -------------------- |
| Fax: 630-285-0075  |                        |                     | Germany - Rosenheim  |
|                    | China - Shenyang       | Taiwan - Hsin Chu   |                      |
| Dallas             |                        |                     | Tel: 49-8031-354-560 |
|                    | Tel: 86-24-2334-2829   | Tel: 886-3-577-8366 |                      |
| Addison, TX        |                        |                     | Israel - Ra’anana    |
|                    | China - Shenzhen       | Taiwan - Kaohsiung  |                      |
| Tel: 972-818-7423  |                        |                     | Tel: 972-9-744-7705  |
|                    | Tel: 86-755-8864-2200  | Tel: 886-7-213-7830 |                      |
Fax: 972-818-2924
Italy - Milan
|     | China - Suzhou | Taiwan - Taipei |     |
| --- | -------------- | --------------- | --- |
Detroit Tel: 86-186-6233-1526  Tel: 886-2-2508-8600  Tel: 39-0331-742611
| Novi, MI          |                      |                       | Fax: 39-0331-466781  |
| ----------------- | -------------------- | --------------------- | -------------------- |
|                   | China - Wuhan        | Thailand - Bangkok    |                      |
| Tel: 248-848-4000 |                      |                       | Italy - Padova       |
|                   | Tel: 86-27-5980-5300 | Tel: 66-2-694-1351    |                      |
| Houston, TX       |                      |                       | Tel: 39-049-7625286  |
|                   | China - Xian         | Vietnam - Ho Chi Minh |                      |
Tel: 281-894-5983
|     | Tel: 86-29-8833-7252 | Tel: 84-28-5448-2100 | Netherlands - Drunen |
| --- | -------------------- | -------------------- | -------------------- |
Tel: 31-416-690399
Indianapolis
| Noblesville, IN   | China - Xiamen       |     | Fax: 31-416-690340 |
| ----------------- | -------------------- | --- | ------------------ |
| Tel: 317-773-8323 | Tel: 86-592-2388138  |     |                    |
Norway - Trondheim
| Fax: 317-773-5453 | China - Zhuhai |     |     |
| ----------------- | -------------- | --- | --- |
Tel: 47-7289-7561
| Tel: 317-536-2380 | Tel: 86-756-3210040  |     |     |
| ----------------- | -------------------- | --- | --- |
Poland - Warsaw
| Los Angeles |     |     | Tel: 48-22-3325737  |
| ----------- | --- | --- | ------------------- |
Mission Viejo, CA
Romania - Bucharest
Tel: 949-462-9523
Tel: 40-21-407-87-50
Fax: 949-462-9608
Spain - Madrid
Tel: 951-273-7800
Tel: 34-91-708-08-90
Raleigh, NC
Fax: 34-91-708-08-91
Tel: 919-844-7510
Sweden - Gothenberg
| New York, NY  |     |     | Tel: 46-31-704-60-40 |
| ------------- | --- | --- | -------------------- |
Tel: 631-435-6000
Sweden - Stockholm
San Jose, CA
Tel: 46-8-5090-4654
Tel: 408-735-9110
UK - Wokingham
Tel: 408-436-4270
Tel: 44-118-921-5800
| Canada - Toronto |     |     | Fax: 44-118-921-5820 |
| ---------------- | --- | --- | -------------------- |
Tel: 905-695-1980
Fax: 905-695-2078
|  DS50002787A-page 12 |     |     |  2018 Microchip Technology Inc. |
| -------------------- | --- | --- | -------------------------------- |
10/25/17
