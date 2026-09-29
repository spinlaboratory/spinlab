#DESC	1.2 * DESCRIPTOR INFORMATION ***********************
*
*	Dataset Type and Format:
*
DSRC	EXP
BSEQ	BIG
IKKF	REAL
XTYP	IDX
YTYP	IGD
ZTYP	NODATA
*
*	Item Formats:
*
IRFMT	D
YFMT	D
*
*	Data Ranges and Resolutions:
*
XPTS	1000
XMIN	0.000000
XWID	160.000000
YPTS	10
YMIN	1499.786328
YWID	0.427344
*
*	Documentational Text:
*
TITL	'003_WP_Noise_30dB'
IRNAM	'1st Harm Absorption'
XNAM	'Time'
YNAM	'Field'
IRUNI	''
XUNI	's'
YUNI	'G'
*
************************************************************
*
#SPL	1.2 * STANDARD PARAMETER LAYER
*
OPER    xuser
DATE    02/25/26
TIME    17:44:02
CMNT    
SAMP    
SFOR    
STAG    C
EXPT    CW
OXS1    IADC
AXS1    ETIM
AXS2    B0VL
AXS3    
A1CT    0.149995
A2RS    10
A2CT    0.15
A2SW    1e-05
MWFQ    9.834281e+09
MWPW    0.2
AVGS    1
SPTP    0.16
RCAG    30
RCHM    1
B0MA    0.0006
B0MF    100000
RCPH    0.0
RCOF    0.0
A1RS    1000
A1SW    160
RCTC    1.31072
*
************************************************************
*
#DSL	1.0 * DEVICE SPECIFIC LAYER
*

.DVC     acqStart, 1.0


.DVC     fieldCtrl, 1.0

AllegroMode        True
CenterField        1499.95 G
Delay              0.0 s
FieldFlyback       On
FieldWait          Wait LED off
GFactor            2.000000
MeasuringHall      False
NbPoints           10
RampCenter         1500.00 G
RampData            G
RampWidth          0.1 G
SetToSampleG       False
StaticField        1499.950 G
StaticFieldMon     1499.950 G
SweepDirection     Up
WidthTM            200.0 G

.DVC     freqCounter, 1.0

FrequencyMon       9.834281 GHz
QMonitBridge       On

.DVC     mwBridge, 1.0

AcqFineTuning      Never
AcqScanFTuning     Off
AcqSliceFTuning    Off
BridgeCalib        84.0
Power              200.0 mW
PowerAtten         0.0 dB
QValue             8900

.DVC     recorder, 1.0

BaselineCorr       On
NbScansAcc         1
NbScansDone        1
NbScansToDo        1
ReplaceMode        On
SmoothMode         Manual
SmoothPoints       0

.DVC     signalChannel, 1.0

AFCTrap            True
AllegroMode        True
AllowShortCt       False
Calibrated         True
ConvFact           9.271e-09
ConvTime           160.00 ms
DualDetect         OFF
EliDelay           1.0 us
ExtLockIn          False
ExtTrigger         False
Gain               30 dB
Harmonic           1
HighPass           True
Integrator         False
IsCalibExp         False
ModAmp             6.000 G
ModFreq            100.00 kHz
ModInput           Internal
ModPhase           0.0
ModResol           10.000
Offset             0.0 %
PolyCof            {2;3,9;0} 0,0.99652,0,0,0.00737177,0,0,-0.00559614,0,0,-2.88221e-05,0,0,1.00404e-05,0,0,3.43695e-08,0,0,-5.0404e-09,0,0,-1.4783e-11,0,0,-1.29132e-12,0
ResCenter          62.5 mm
ResLength          40 mm
Resolution         1000
Resonator          1
SctNorm            True
SctRevision        Allegro
SpuExtension       False
SweepTime          160.00 s
TimeConst          1310.72 ms
TimeExp            True
TuneCaps           42

*
************************************************************
