<!-- Fuente: Preinforme Practica 2 Final- Sofia Aguilar_Sebastian Calderon_ Samuel Martinez.pdf | Convertido con MarkItDown 0.1.7 (motor pdfminer, texto corrido) el 2026-11-11 -->

PONTIFICIA UNIVERSIDAD JAVERIANA

Proyecto de Diseño en Electrónica 1

Concepción y diseño de un sistema para la detección de
discontinuidades en tuberías de cobre mediante corrientes
de Eddy

Práctica 2

Samuel Martínez
Juan Sebastián Calderón
Sofía Aguilar Parra

1 de octubre de 2026

Resumen

Se diseñó una cadena analógica de inspección por corrientes de Eddy que integra acondicionamiento
diferencial, excitación y demodulación en fase y cuadratura (I/Q). PCB1 amplifica el desbalance entre
dos bobinas y PCB2 genera la excitación, recupera las componentes de banda base, resta la referencia
sana y aplica ganancia final. Las simulaciones verificaron una excitación de 1,94 V pico a pico, un error
del canal alineado cercano al 0,3 %, con residuo cruzado del 7,5 %, y el funcionamiento del filtrado y la
calibración. La caracterización con bobinas anulares y procesamiento en LabVIEW a 10 kHz produjo
cambios procesados de 60 mV y 110 mV al comparar la discontinuidad con tubo sano. Finalmente, el
diseño fue trasladado a Altium.

Palabras clave: corrientes de Eddy, demodulación I/Q, tuberías de cobre, acondicionamiento analógico.

1. Concepción y diseño funcional

Una discontinuidad en una tubería conductora modifica las corrientes de Eddy inducidas y, con ellas, la
impedancia compleja de una bobina próxima (TWI Ltd., s. f.). Por eso se compara una bobina activa con
otra de referencia sobre cobre sano y su diferencia se procesa en dos ejes, para conservar amplitud y fase.
La Práctica 2 integra PCB1 con una PCB2 que genera la excitación y las referencias, demodula en I/Q,
filtra la conmutación y amplifica la diferencia respecto del estado sano.

La arquitectura mantiene el recorrido puente–PCB1–demodulación–filtrado–resta–salidas. El oscilador
de PCB2 genera tanto las referencias de demodulación como la excitación del puente, manteniendo
coherencia temporal. Los esquemáticos completos se presentan en los Anexos A y B.

1.1. PCB1: adquisición y acondicionamiento

Cada rama del puente contiene una resistencia de excitación y una bobina modelada mediante Z = R+jωL.
La rama activa emplea RBA = 100 Ω y la referencia un trimmer RBR de 500 Ω. El ajuste sobre cobre
sano busca minimizar Vd, y la salida de PCB1 es Vo:

Vd = V (IN_POS_155) − V (IN_NEG_155),

Vo(t) = Vref + Ao cos(ω0t + ϕo).

(1)

El INA155 y las etapas posteriores proporcionan aproximadamente 1018 V/V a 10 kHz, con corte global
cercano a 20,1 kHz. Así, un pequeño cambio de impedancia se convierte en una variación observable de
Vo, conservando información de amplitud y fase.

1.2. Alimentación y referencias continuas

La fuente Keysight E36233A alimenta el sistema entre GND y +3,7 V. Divisores resistivos, filtrado y
buffers generan Vref y Vref 2, cercanas a 1,85 V. Estas referencias actúan como tierra virtual y permiten
procesar las señales alternas sin una fuente negativa.

1.3. Demodulación síncrona I/Q

Para la componente alterna de Vo, x(t) = Ao cos(ω0t + ϕo), el producto por una referencia en fase es

x(t) cos(ω0t) = Ao
2

cos ϕo + Ao
2

cos(2ω0t + ϕo).

(2)

El término continuo contiene la información útil y el término a 2ω0 se elimina con filtrado. Una referencia
desplazada aproximadamente 90◦ obtiene la componente en cuadratura (Orozco, 2014).

La implementación utiliza señales cuadradas ±1. Para referencias ideales,

1

IRAW − Vref 2 =

2Ao
π

cos ϕo,

QRAW − Vref 2 =

2Ao
π

sin ϕo.

(3)

El LM2903B genera los relojes CLKI y CLKQ; sus salidas de colector abierto incorporan resistencias de
4,7 kΩ a VCC. El TS5A23157 selecciona alternativamente entre Vo y

Vinv = 2Vref 2 − Vo.

Respecto de Vref 2, esta conmutación equivale al cambio de signo requerido para la detección síncrona
(Texas Instruments, 2019, 2025).

1.4. Filtrado, referencia sana y ganancia

Cada canal utiliza un filtro activo de segundo orden con R = 82 kΩ y C = 100 nF:

fn =

1
2πRC

≈ 19,4 Hz,

K = 1 +

5.9
10

= 1,59,

Qf =

1
3 − K

≈ 0,709.

(4)

La respuesta es próxima a Butterworth; la banda cercana a 20 Hz conserva los cambios lentos del sensor
y rechaza la componente de conmutación cercana a 2f0. Además,

1,59

2

π

≈ 1,012,

por lo que el filtro compensa aproximadamente la pérdida de amplitud asociada a la demodulación
cuadrada.
Sobre tubo sano se ajustan I0 y Q0, dos trimmers de 10 kΩ seguidos de buffers, hasta igualar I0 = ILP F
y Q0 = QLP F una vez establecidos los filtros. La escala temporal 1/(2πfn) ≈ 8,2 ms caracteriza el filtro,
pero no constituye un tiempo de establecimiento garantizado ni una espera suficiente para calibrar. Las
etapas diferenciales finales, con relaciones de 100 kΩ/10 kΩ, entregan

VI,OU T = Vref 2 + 10(ILP F − I0),
VQ,OU T = Vref 2 + 10(QLP F − Q0).

(5)

Así, el estado sano queda próximo a 1,85 V y la perturbación aparece como un desplazamiento alrededor
de dicho punto.

1.5. Generación de referencias y excitación

Con Ra = 150 kΩ, Rb = 820 Ω, Rf = 330 kΩ y Ca = Cb = 1 nF, la frecuencia teórica del oscilador es

√︄ 1/Ra + 1/Rb
Rf CaCb
El valor coincide con los aproximadamente 9,6 kHz observados en simulación. Dos diodos 1N4148 estabilizan
la amplitud evitando el recorte sostenido.

≈ 9,70 kHz.

fosc ≈

1
2π

(6)

La componente Q se obtiene mediante un all-pass con R = 16 kΩ y C = 1 nF:

HAP (s) =

1 − sRC
1 + sRC

,

f90 =

1
2πRC

≈ 9,95 kHz.

(7)

2

A 9,6 kHz produce aproximadamente −88◦ (valor calculado, no medido). Un driver con realimentación de
530 Ω y resistencia de 10 kΩ, cuya ganancia es 1,053, desacopla la carga de las bobinas y el capacitor de
10 µF elimina la componente DC de Vexc. El TS924 se emplea por su operación a baja tensión y capacidad
de manejar la carga sensora (cerca de 50 Ω entre las dos ramas, del orden de 20 mA) (STMicroelectronics,
2014).

2. Resultados y análisis

Las simulaciones verificaron cada etapa antes de integrar la cadena completa. El modelo nominal de la
bobina emplea L0 = 200 µH y R0 = 5 Ω; las perturbaciones dR y dL actúan sobre la bobina activa y se
utilizan únicamente para comprobar la sensibilidad eléctrica del circuito, sin representar una profundidad
física de la discontinuidad.

2.1. Puente y acondicionamiento en PCB1

Figura 1: Excitación, puente diferencial y acondicionamiento de PCB1.

(a) Puente diferencial.

(b) Acondicionamiento en PCB1.

(c) Vexc, Vd y Vo.

En la Figura 1, Vd resulta mucho menor que Vexc porque, en condición sana, las dos ramas poseen
impedancias similares. Este comportamiento es buscado: el puente rechaza la mayor parte de la excitación
común y deja principalmente la diferencia asociada al sensor.
PCB1 amplifica el desbalance y genera Vo, cuya amplitud y fase cambian con la impedancia de la bobina.
El margen de esta etapa y las consecuencias del recorte se analizan en la sección 2.5.

3

2.2. Referencias y excitación coherentes

Figura 2: Generación de las referencias I/Q y de la excitación del puente.

(a) Oscilador, all-pass y driver.

(b) OSCI , OSCQ y Vexc.

La Figura 2 muestra que OSCI y OSCQ oscilan aproximadamente entre 0,95 V y 2,75 V, centradas en
Vref 2 ≈ 1,85 V, con frecuencia cercana a 9,6 kHz. El desplazamiento entre ambas es próximo a cuadratura,
permitiendo separar posteriormente la señal en dos proyecciones.
Después del driver y del acoplamiento se obtiene Vexc ≈ 1,94 V pico a pico centrada en cero. La generación
de OSCI , OSCQ y Vexc desde el mismo oscilador evita diferencias de frecuencia entre excitación y
demodulación y mantiene una referencia de fase común.

2.3. Demodulación y extracción de banda base

La prueba aislada utiliza una entrada de 0,2 V pico. Para un canal alineado, la ecuación (3) predice

Vref 2 +

2A
π

= 1,977 324 V.

4

Tabla 1: Promedios de los canales RAW en la prueba aislada.

Entrada

IRAW (V) QRAW (V) Error alineado
Alineada con I
1,976958
Alineada con Q 1,840607

1,859613
1,976964

0,366 mV
0,360 mV

El error es cercano al 0,3 % de la componente útil, indicando que la conmutación reproduce adecuadamente
la multiplicación síncrona. Cuando la señal se rota 90◦, la componente principal se desplaza de I hacia Q,
comprobando la separación de amplitud y fase.

El canal no alineado conserva un residuo cercano a 9,5 mV, alrededor del 7,5 % de la componente principal.
Esta proyección cruzada cuantifica la no idealidad conjunta de las referencias y de la conmutación; la
prueba aislada no permite atribuirla a un único bloque. El desfase calculado del all-pass corresponde al
generador completo, no a las fuentes ideales de esta prueba.

Nota de precisión. Los decimales de las tablas de simulación expresan resolución numérica del modelo, no
exactitud experimental ni incertidumbre instrumental.

Figura 3: Prueba aislada de multiplicación y filtrado con un esquemático común.

(a) Conmutación I/Q y filtros de banda base.

(b) Inversión y multiplicación.

(c) Señales RAW y LPF.

En la Figura 3, la conmutación transforma la entrada en una rectificación síncrona. Las señales IRAW
y QRAW contienen tanto el promedio útil como componentes rápidas generadas por la conmutación,
principalmente alrededor de 2f0.
Los filtros de 20 Hz atenúan esas componentes y conservan la banda base. Después de esta etapa, la fase
de la señal ya no se observa como un desplazamiento temporal de una onda de 10 kHz, sino como la
relación entre los niveles I y Q.

5

2.4. Calibración y respuesta a desplazamientos DC

Tabla 2: Calibración y ganancia final en la prueba de banda base.

Magnitud

Estado calibrado Desplazamiento controlado

ILP F − I0
QLP F − Q0
VI,OU T
VQ,OU T

−0,027 mV
0,123 mV
1,849 73 V
1,851 23 V

7,920 mV
−4,645 mV
1,929 20 V
1,803 55 V

Con I0 = 1,929 549 V y Q0 = 1,770 451 V, las salidas calibradas quedan próximas a Vref 2. La resta
retira el nivel base antes de aplicar la ganancia final; estos ajustes dependen del ensayo y no son valores
universales para los trimmers.

Los desplazamientos controlados de 7,92 mV en I y −4,645 mV en Q producen cambios aproximados de
79,2 mV y −46,5 mV, respectivamente, de acuerdo con G = 10.
Se registró una variación pico a pico de 40,4 mV en las salidas finales del ensayo. Sin especificar la
ventana temporal de medición, este valor no permite separar el transitorio de establecimiento del rizado
estacionario. Su interpretación y la selección definitiva de ganancia requieren comprobar la señal después
del establecimiento.

2.5. Lazo completo y rango dinámico

La simulación integrada compara dR = dL = 0 con dR = dL = 5 %. Este porcentaje se utiliza
únicamente como una perturbación eléctrica de prueba y no representa la geometría ni la profundidad de
la discontinuidad.

Tabla 3: Respuesta del lazo integrado ante la perturbación paramétrica.

Magnitud Condición sana

dR = dL = 5 %

ILP F
QLP F
VI,OU T
VQ,OU T

1,682 69 V
1,497 60 V
1,845 62 V
1,848 39 V

0,842 02 V
3,594 89 V
0,101 72 V
3,598 02 V

Figura 4: Condiciones sana y perturbada del modelo completo del Anexo A.

6

En condición sana, ILP F y QLP F no tienen que coincidir con 1,85 V, pues contienen la respuesta y offsets
de las etapas anteriores. Al ajustar I0 y Q0, las salidas finales quedan próximas a Vref 2.
La perturbación produce cambios diferentes en ambos canales; al alcanzarse saturación, estas lecturas no
permiten cuantificar linealmente las variaciones de amplitud y fase.

Sin embargo,

VI,OU T = 0,102 V,

VQ,OU T = 3,598 V,

quedan muy próximas a los rieles de alimentación. Por tanto, esta prueba demuestra sensibilidad del
sistema, pero también saturación. En ese punto la salida ya no puede considerarse proporcional a dR y
dL.
PCB1 posee además un límite independiente. Aproximadamente 2,5 mV pico a pico en su entrada producen
cerca de 2,55 V pico a pico en Vo; con 3,4 mV la excursión requerida sería de 3,46 V, casi todo el rango de
alimentación.

Para la etapa de banda base debe cumplirse

G ∆VBB,m´ax ≤ m´ın (Vref 2 − VOL, VOH − Vref 2) .

(8)

Con rieles ideales de 0 V y 3,7 V, G = 10 admite aproximadamente ±185 mV antes de saturación. Reducir
G protege la etapa final, pero no corrige un recorte que haya ocurrido previamente en PCB1.

2.6. Caracterización experimental de las puntas en LabVIEW

2.6.1. Montaje, adquisición y procesamiento

La configuración final emplea dos bobinas anulares que rodean el tubo. La activa inspecciona la región de
interés y la segunda permanece como referencia sobre cobre sano. Ambas se caracterizaron sobre cobre
sano a 10 kHz, con nivel de prueba de 1 V; sus parámetros R–L serie y factores de calidad se presentan
en la Tabla 4.

Tabla 4: Parámetros medidos de las bobinas anulares sobre cobre sano.

Bobina

Referencia
Móvil

L (µH) Rs (Ω)
8,59
196,66
8,09
195,66

Qc

1,438
1,519

Los valores son coherentes con Qc = 2πf L/Rs: se calculan 1,4385 y 1,5196, respectivamente. Este Qc
caracteriza las bobinas, no el factor Qf de los filtros. Las inductancias próximas a 196 µH respaldan
el nominal de 200 µH utilizado en simulación; las resistencias medidas son parámetros experimentales
distintos de R0 = 5 Ω.
El VI del Anexo C adquiere la excitación y la salida de PCB1 mediante DAQ Assistant. La excitación
adquirida es la referencia I y su transformada de Hilbert genera Q (National Instruments, 2004). Los
productos con la señal de PCB1 se filtran a 20 Hz; después se restan las referencias y se aplica G = 10.
Se promedian las muestras 8000 a 9999, en una ventana de duración 2000/fs que comienza en 8000/fs.
La exclusión del transitorio debe verificarse con la frecuencia de muestreo y la respuesta temporal del
procesamiento; esos datos no quedan documentados numéricamente en la captura. Los 10 kHz corresponden
a la excitación, no a fs. Tampoco queda identificado el modelo de la tarjeta de adquisición.

7

El ensayo a 10 kHz comparó tubo sano, región con discontinuidad y bobina al aire, manteniendo excitación,
ganancias, filtrado y ajustes. Los indicadores rotulados I0/Q0 en LabVIEW se denominan aquí SI , SQ:
son salidas procesadas, distintas de los trimmers analógicos I0, Q0. LabVIEW usa multiplicación numérica
de las referencias adquiridas; PCB2 implementa conmutación ±1. Ambas recuperan proyecciones I/Q,
pero no comparten automáticamente el mismo factor de escala absoluto.

2.6.2. Resultados referidos al tubo sano
Las lecturas (SI , SQ) fueron (−3,53; 1,26) en tubo sano, (−3,47; 1,37) sobre la discontinuidad y
(−5,45; −2,18) al aire. Para eliminar el nivel común de referencia y comparar las tres condiciones, se
calculó

∆SI = SI − SI,sano,

∆IBB = ∆SI /10,

∆SQ = SQ − SQ,sano,

∆QBB = ∆SQ/10.

(9)

Tabla 5: Respuesta experimental relativa al tubo sano a 10 kHz.

Condición

Tubo sano
Zona con discontinuidad
Bobina al aire

∆SI (V) ∆SQ (V) MS (V)
0,000
0,000
0,125
0,110
3,940
−3,440

0,000
0,060
−1,920

Nota. MS = √︁∆S2
diez; no corresponden a tensiones medidas directamente en las salidas físicas de PCB2.

Q. Los valores son coordenadas equivalentes del procesamiento en LabVIEW con ganancia

I + ∆S2

La discontinuidad produjo ∆IBB ≈ 6 mV y ∆QBB ≈ 11 mV, con magnitud conjunta de 12,5 mV antes
de la ganancia y de 125 mV después de ella, en la escala del procesamiento digital. En este registro, el
cambio de Q es 1,83 veces el de I, por lo que ambos canales aportan información. Estas coordenadas
no se comparan directamente con el margen analógico de PCB2: ello requiere calibrar la amplitud de
referencia y la escala de ambas implementaciones.

La condición al aire produce un contraste mucho mayor, de 3,940 V en la magnitud procesada, asociado
al cambio de acoplamiento bobina–conductor. La variación de la discontinuidad y la del aire son
aproximadamente colineales, pero de sentidos opuestos (61,4◦ y −119,2◦ en este plano I/Q). Esta
dirección depende de la referencia del ensayo; no identifica por sí sola un cambio puramente resistivo o
inductivo.

2.6.3. Variación relativa de la respuesta y de la impedancia

Como medida normalizada del contraste experimental se utiliza

pI/Q = 100

√︂(SI,def − SI,sano)2 + (SQ,def − SQ,sano)2
√︂(SI,aire − SI,sano)2 + (SQ,aire − SQ,sano)2
El 3,18 % expresa el contraste de la discontinuidad respecto del contraste sano–aire en la respuesta
procesada. La ganancia común y los offsets fijos se cancelan; no representa un cambio porcentual de
impedancia.
Con Z = Rs + j2πf L, las mediciones de la Tabla 4 permiten calcular a 10 kHz Zref = (8,59 + j12,36) Ω
y Zmov = (8,09 + j12,29) Ω. Con los valores sin redondear, ∆Zsano = (−0,50 − j0,063) Ω, de magnitud
0,504 Ω; el desbalance relativo es

≈ 3,18 %.

(10)

pZ,sano = 100 |Zmov − Zref |

|Zref |

≈ 3,35 %.

(11)

8

Predomina la diferencia resistiva: Rs cambia −5,82 % y L, −0,51 %. La disminución de magnitud de
impedancia es 2,21 % (de 15,05 Ω a 14,72 Ω), una definición distinta de |∆Z|/|Zref |. El desbalance inicial
justifica el ajuste de RBR y la resta de la referencia I/Q.
Ambas bobinas se midieron sobre cobre sano: el 3,35 % es su desbalance inicial, no el efecto de la
discontinuidad. No se dispone de R, L de la misma bobina sobre ambas regiones. El contraste procesado
del 3,18 % tampoco equivale al 5 % impuesto en simulación mediante Zpert = 1,05Znom: son magnitudes
y ensayos distintos.

3. Implementación del diseño en Altium

3.1. Correspondencia entre modelo y componentes

El esquemático del Anexo B traslada las funciones simuladas a componentes físicos. Se conserva el
INA155U para adquisición diferencial, TS924 en las etapas analógicas, LM2903B para los relojes y
TS5A23157 para la conmutación (Texas Instruments, 2000).
Los designadores cambian durante la integración, pero se mantienen las redes Vexc, Vo, OSCI /OSCQ,
CLKI /CLKQ, ILP F /QLP F y las salidas.
RBA permanece fija en 100 Ω; RBR es un trimmer de 500 Ω y las referencias sanas utilizan dos trimmers
de 10 kΩ.

3.2. Distribución física y ruteo

Figura 5: Vista 2D del ruteo integrado del sistema en Altium.

La distribución agrupa adquisición, generación y banda base, con puntos de prueba e interfaces accesibles.
Los criterios eléctricos priorizan desacoplamiento de 100 nF por encapsulado, retornos de baja impedancia
sin compartir trayectos sensibles con la excitación y separación de los relojes respecto de la adquisición.
El emparejamiento de los pares R–C y de las relaciones 100 kΩ/10 kΩ conserva la correspondencia I/Q:
los ajustes I0/Q0 corrigen offsets, no diferencias de ganancia o respuesta temporal.

9

3.3. Calibración y verificación de la tarjeta

La secuencia prevista de puesta en marcha verifica VCC, Vref 2, las referencias OSCI /OSCQ, los relojes y
Vexc bajo carga. Sobre cobre sano se ajusta RBR, se comprueba que Vo no tenga recorte y, después del
establecimiento de los filtros, se ajustan I0/Q0. El balance del sensor precede a la puesta a cero de banda
base.

La caracterización verifica la respuesta del sensor y su procesamiento en LabVIEW. LTspice verifica el
comportamiento del modelo analógico; su correspondencia con el montaje queda pendiente de validación
física. Altium documenta su implementación esquemática y su distribución en PCB; la captura del ruteo
no acredita por sí sola verificación eléctrica, cumplimiento de DRC ni aptitud definitiva para fabricación.

4. Conclusiones

1. La cadena PCB1–PCB2 convierte el desbalance de las bobinas en dos componentes de banda base.
Las simulaciones verifican el recorrido desde el puente hasta las salidas I/Q. La caracterización R–L
sobre cobre sano cuantificó un desbalance complejo inicial del 3,35 %, que justifica tanto el balance
del puente como la calibración de la línea base.

2. El oscilador, el all-pass y el driver generan aproximadamente 9,6 kHz, referencias cercanas a cuadratura
y una excitación de 1,94 V pico a pico. El canal alineado presenta un error cercano al 0,3 %, con una
proyección cruzada aproximada del 7,5 %.

3. El filtrado de 20 Hz, la referencia sana y la ganancia diez permiten representar la perturbación
mediante dos niveles continuos. Experimentalmente, la discontinuidad produjo cambios procesados de
60 mV en I y 110 mV en Q, con una separación vectorial de aproximadamente 125 mV, equivalente a
3,18 % del contraste sano–aire; ambos canales contienen información relevante.

4. El ensayo integrado evidencia respuesta a la perturbación y saturación, no proporcionalidad lineal. El
margen de PCB1 y la ganancia final requieren validación física sin trasladar directamente la escala
digital a la analógica. Los registros experimentales evidencian contraste entre condiciones, pero no
incluyen una evaluación estadística de repetibilidad ni permiten establecer un umbral de detección o
una relación con la profundidad de la falla.

10

Referencias
National Instruments. (2004). LabVIEW analysis concepts (370192C-01) [Manual].

https://docs-be.ni.com/bundle/370192c/raw/resource/enus/370192c.pdf

Orozco, L. (2014). Synchronous detectors facilitate precision low-level measurements. Analog Dialogue, 48 (11).

https://www.analog.com/en/resources/analog-dialogue/articles/
synchronous-detectors-facilitate-precision.html

STMicroelectronics. (2014). TS924, TS924A: Rail-to-rail output current quad operational amplifier (Rev. 11)

[Hoja de datos].
https://www.st.com/resource/en/datasheet/ts924.pdf

Texas Instruments. (2000). INA155: Single-supply, rail-to-rail output, CMOS instrumentation amplifier [Hoja de

datos].
https://www.ti.com/lit/ds/symlink/ina155.pdf

Texas Instruments. (2019). TS5A23157: Dual 10-ohm SPDT analog switch (Rev. F) [Hoja de datos].

https://www.ti.com/lit/ds/symlink/ts5a23157.pdf

Texas Instruments. (2025). LM393B, LM2903B, LM193, LM293, LM393 and LM2903 dual comparators (Rev.

AH) [Hoja de datos].
https://www.ti.com/lit/ds/symlink/lm2903.pdf

TWI Ltd. (s. f.). Eddy current testing.

https://www.twi-global.com/technical-knowledge/job-knowledge/eddy-current-testing-123

11

A. Esquemático completo en LTspice

Figura 6: Modelo completo de la cadena PCB1–PCB2.

(a) Puente, alimentación y generación de referencias y excitación.

(b) Adquisición diferencial y acondicionamiento en PCB1.

(c) Demodulación, filtrado, referencias sanas y salidas I/Q.

12

B. Esquemático completo en Altium

Figura 7: Implementación esquemática integrada del sistema.

13

C. Adquisición y procesamiento implementados en LabVIEW

Figura 8: Diagrama de adquisición, demodulación I/Q y estimación DC en LabVIEW.

El DAQ Assistant entrega dos canales: la referencia de excitación y la respuesta de PCB1. La primera se
utiliza directamente en I y, mediante Hilbert, en Q. Los productos pasan por filtros de 20 Hz, restas de
referencia y ganancia diez. Finalmente se promedian 2.000 muestras desde el índice 8.000. Las constantes
de resta visibles (−0,318 en I y 0,1 en Q) son ajustes del VI mostrado, no los niveles físicos universales de
los trimmers. La comparación experimental se expresa respecto del registro sano, según la ecuación (9).

14

D. Referencia de verificación por nodos

La secuencia siguiente resume las comprobaciones previstas para la implementación analógica. Los valores
de simulación son referencias de diseño y la calibración sana se realiza sobre el montaje físico.

Tabla 6: Nodos, magnitudes y función de verificación.

Nodo

Magnitud esperada

Función

VCC, Vref 2
OSCI , OSCQ

CLKI , CLKQ
Vexc

Vd, Vo
ILP F , QLP F

VI,OU T , VQ,OU T

Alimentación y tierra virtual
Oscilación y cuadratura

3,7 V y aproximadamente 1,85 V DC
Aproximadamente 9,6 kHz, con centro en
Vref 2
Dos niveles lógicos compatibles con el switch Comparación y controles
Aproximadamente 1,94 V pico a pico, sin ni-
vel DC
Diferencial sano pequeño y salida sin recorte Balance y margen de PCB1
Niveles de banda base después del estableci-
miento
Próximas a Vref 2 después del ajuste sano

Demodulación y filtrado

Driver bajo carga

Resta de referencia y ganancia

La calibración se conserva durante la inspección. Si una etapa anterior alcanza su límite, primero debe
corregirse su margen antes de reajustar la línea base; así, la puesta a cero no oculta un recorte de la señal
adquirida.

15
