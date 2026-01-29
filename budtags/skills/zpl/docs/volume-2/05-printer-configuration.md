<!-- Source: ZPL II Programming Guide Volume 2 -->
<!-- Section: Chapter 5: Printer Configuration Using ZPL II -->
<!-- Generated: 2025-11-02 04:52:35 -->

## XML-Super Host Status

This section provides information about XML-Super Host Status.

## Contents

| Introduction to XML .    |   78 |
|--------------------------|------|
| XML Attributes . . . . . |   78 |
| Printer Definitions.     |   79 |
| Saved Settings. . .      |   80 |
| Format Settings . .      |   88 |
| Status Information       |   90 |

<!-- image -->

<!-- image -->

## Introduction to XML

XML (Extensible Markup Language), a scaled-down version of SGML (Standard Generalized Markup Language) geared toward processing and Web applications, is used to return Zebra printer information to the ZTools™ 4.0 program for Windows. You also may choose to use XML data for your own custom software applications.

Using ZPL II commands, an administrator or user can change the specific setting and format variables of the printer, such as ribbon tension, print mode, label length, or font. To see a full listing of all current setting and format information, enter the following ZPL II command:

^HZS

Any information that does not apply to the printer's platform will not be returned.

Transmission of XML data from the printer to your host application may be slow due to the amount of information being returned. Using the ZPL II commands ~HI and ~HS will be a faster alternative. XML data should only be used to gather data that is not available under the ~HI and ~HS commands.

## XML Attributes

The tables in this section contain a description of each attribute, an example of the XMLgenerated information sent back from the printer with example information, and the ZPL II command used to change or set the attribute (if applicable).

The following main categories of attributes are covered in this section:

- Printer Definitions on page 79
- Saved Settings on page 80
- Format Settings on page 88
- Status Information on page 90

Two additional categories of attributes exist for use with Zebra printers:

- object list
- Zebra object

## Printer Definitions

Table 18 • Printer Definitions

| Description                        | XML Output                                                                                                                          | ZPL      |
|------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------|----------|
| Model of printer                   | <MODEL>140XiIII</MODEL>                                                                                                             | ^CT, ~CT |
| Firmware version                   | <FIRMWARE-VERSION>V33.10.OP10</FIRMWARE- VERSION>                                                                                   |          |
| Plug-and-play information          | <PLUG-AND-PLAY-VALUE>MANUFACTURER:Zebra Technologies;COMMAND SET:ZPL;MODEL:ZTC 140XiII-600dpi;CLASS:PRINTER; </PLUG-AND-PLAY-VALUE> |          |
| Dots per millimeter                | <DOTS-PER-MM>24</DOTS-PER-MM>                                                                                                       |          |
| Dots per row                       | <DOTS-PER-DOTROW>1920</DOTS-PER-DOTROW>                                                                                             |          |
| Physical memory: type              | <TYPE ENUM='R, E, B'>R</TYPE>                                                                                                       |          |
| Physical memory: size              | <SIZE>3145728</SIZE>                                                                                                                |          |
| Physical memory: available for use | <AVAILABLE>2600940</AVAILABLE>                                                                                                      |          |
| Option: label cutter               | <CUTTER BOOL='Y,N'>N</CUTTER>                                                                                                       |          |
| Option: label rewind               | <REWIND BOOL='Y,N'>N</REWIND>                                                                                                       |          |
| Option: label peel                 | <PEEL BOOL='Y,N'>Y</PEEL>                                                                                                           |          |
| Option: label applicator           | <APPLICATOR BOOL='Y,N'>N</APPLICATOR>                                                                                               |          |
| Option: label verifier             | <VERIFIER BOOL='Y,N'>N</VERIFIER>                                                                                                   |          |

## Saved Settings

Table 19 • Saved Settings

| Description                                   | XML Output                                                                                                                                                                                                                    | ZPL      |
|-----------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------|
| Name of printer                               | <NAME>Zebra Printer</NAME>                                                                                                                                                                                                    | ^KN      |
| Description of printer                        | <DESCRIPTION>in Shipping Area</Description>                                                                                                                                                                                   | ^KN      |
| Set control instruction prefix (default is ~) | <TILDE-DEFINE MIN='0' MAX='255'> <CURRENT>126</CURRENT> <STORED>126</STORED> <DEFAULT>126</DEFAULT> </TILDE-DEFINE>                                                                                                           | ^CT, ~CT |
| Set format instruction prefix (default is ^)  | <CARET-DEFINE MIN='0' MAX='255'> <CURRENT>94</CURRENT> <STORED>94</STORED> <DEFAULT>94</DEFAULT> </CARET-DEFINE>                                                                                                              | ^CC, ~CC |
| Set delimiter character (default is ,)        | <DELIM-DEFINE MIN='0' MAX='255'> <CURRENT>44</CURRENT> <STORED>44</STORED> <DEFAULT>44</DEFAULT> </DELIM-DEFINE>                                                                                                              | ^CD, ~CD |
| Toggle half-density                           | <HALF-DENSITY BOOL='Y,N'> <CURRENT>N</CURRENT> <STORED>N</STORED> <DEFAULT>N</DEFAULT> </HALF-DENSITY>                                                                                                                        | ^JM      |
| Set ribbon tension                            | <RIBBON-TENSION ENUM='LOW, MEDIUM, HIGH'> <CURRENT>HIGH</CURRENT> <STORED>HIGH</STORED> <DEFAULT>HIGH</DEFAULT> </RIBBON-TENSION ENUM>                                                                                        | ^JW      |
| Set display language                          | <OPERATOR-LANGUAGE ENUM='ENGLISH, SPANISH, FRENCH, GERMAN, ITALIAN, NORWEGIAN, PORTUGUESE, SWEDISH, DANISH, SPANISH2, DUTCH, FINNISH, CUSTOM'> <CURRENT>ENGLISH</CURRENT> <STORED>ENGLISH</STORED> <DEFAULT>ENGLISH</DEFAULT> | ^KL      |

Table 19 • Saved Settings (Continued)

| Description                                    | XML Output                                                                                                                                   | ZPL   |
|------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------|-------|
| Set password                                   | <PASSWORD MIN='0' MAX='9999'> <CURRENT>1234</CURRENT> <STORED>1234</STORED> </PASSWORD>                                                      | ^KP   |
| Set label positioning relative to top edge     | <LABEL-TOP MIN='-120' MAX='120'> <CURRENT>0</CURRENT> <STORED>0</STORED> <DEFAULT>0</DEFAULT> </LABEL-TOP>                                   | ^LT   |
| Set maximum label length                       | <MAX-LABEL-LENGTH MIN='0' MAX='9999'> <CURRENT>23400</CURRENT> <STORED>0</STORED> <DEFAULT>39</DEFAULT> </MAX-LABEL-LENGTH>                  | ^ML   |
| Set printing darkness                          | <MEDIA-DARKNESS MIN='0' MAX='30'> <CURRENT>11</CURRENT> <STORED>11</STORED> <DEFAULT>10</DEFAULT> </MEDIA-DARKNESS>                          | ^SD   |
| Media feed: set action at power up             | <POWER-UP ENUM='FEED, CALIBRATION, LENGTH, NO MOTION'> <CURRENT>FEED</CURRENT> <STORED>FEED</STORED> <DEFAULT>FEED</DEFAULT>                 | ^MF   |
| Media feed: set action after closing printhead | <HEAD-CLOSE ENUM='FEED, CALIBRATION, LENGTH, NO MOTION'> <CURRENT>FEED</CURRENT> <STORED>FEED</STORED> <DEFAULT>FEED</DEFAULT> </HEAD-CLOSE> | ^MF   |
| Print mode: set post-print action              | <MODE ENUM='REWIND, TEAR OFF, PEEL OFF, CUTTER'> <CURRENT>TEAR OFF</CURRENT> <STORED>TEAR OFF</STORED> <DEFAULT>TEAR OFF</DEFAULT> </MODE>   | ^MM   |

Table 19 • Saved Settings (Continued)

| Description                                                           | XML Output                                                                                                                                                            | ZPL   |
|-----------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------|
| Print mode: set pre- peel option                                      | <PRE-PEEL BOOL='Y,N'> <CURRENT>N</CURRENT> <STORED>N</STORED> <DEFAULT>N</DEFAULT> </PRE-PEEL>                                                                        | ^MM   |
| Set media type (continuous or non-continuous roll)                    | <MEDIA-TRACKING ENUM='CONTINUOUS, NON-CONTINUOUS'> <CURRENT>CONTINUOUS</CURRENT> <STORED>CONTINUOUS</STORED> <DEFAULT>CONTINUOUS</DEFAULT> </MEDIA-TRACKING>          | ^MN   |
| Set measurement type                                                  | <MODE-UNITS ENUM='DOTS, INCHES, MILLIMETERS'> <CURRENT>DOTS</CURRENT> <STORED>DOTS</STORED> <DEFAULT>DOTS</DEFAULT> </MODE-UNITS>                                     | ^MU   |
| Assign a network ID number (must be done prior to networking printer) | <ZNET-ID MIN='0' MAX='999'> <CURRENT>0</CURRENT> <STORED>0</STORED> <DEFAULT>0</DEFAULT> </ZNET-ID>                                                                   | ^NI   |
| Select type of media                                                  | <MEDIA-TYPE ENUM='DIRECT-THERMAL, THERMAL- TRANS.'> <CURRENT>DIRECT-THERMAL</CURRENT> <STORED>DIRECT-THERMAL</STORED> <DEFAULT>THERMAL-TRANS.</DEFAULT> </MEDIA-TYPE> | ^MT   |
| Set print width                                                       | <PRINT-WIDTH MIN='2' MAX='2000'> <CURRENT>1920</CURRENT> <STORED>1920</STORED> <DEFAULT>0</DEFAULT> </PRINT-WIDTH>                                                    | ^PW   |

Table 19 • Saved Settings (Continued)

| Description                       | XML Output                                                                                                                                    | ZPL   |
|-----------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------|-------|
| Set printhead resistance          | <HEAD-RESISTANCE MIN='488' MAX='2415'> <CURRENT>500</CURRENT> <STORED>500</STORED> <DEFAULT>500</DEFAULT> </HEAD-RESISTANCE>                  | ^SR   |
| Calibration: label length in dots | <CALIBRATED-LABEL-LENGTH MIN='0' MAX='9999'> <CURRENT>1244</CURRENT> <STORED>1244</STORED> <DEFAULT>1244</DEFAULT> </CALIBRATED-LABEL-LENGTH> | ^SS   |
| Calibration: web                  | <WEB-THRESHOLD MIN='0' MAX='100'> <CURRENT>0</CURRENT> <STORED>0</STORED> <DEFAULT>0</DEFAULT> </WEB-THRESHOLD>                               | ^SS   |
| Calibration: media                | <MEDIA-THRESHOLD MIN='0' MAX='100'> <CURRENT>75</CURRENT> <STORED>75</STORED> <DEFAULT>0</DEFAULT>                                            | ^SS   |
| Calibration: ribbon               | </MEDIA-THRESHOLD> <RIBBON-THRESHOLD MIN='0' MAX='100'> <CURRENT>60</CURRENT> <STORED>60</STORED> <DEFAULT>60</DEFAULT>                       | ^SS   |
| Calibration: mark sensing         | <MARK-THRESHOLD MIN='0' MAX='100'> <CURRENT>0</CURRENT> <STORED>0</STORED> <DEFAULT>0</DEFAULT> </MARK-THRESHOLD>                             | ^SS   |
| Calibration: mark media sensing   | <MARK-MEDIA-THRESHOLD MIN='0' MAX='100'> <CURRENT>0</CURRENT> <STORED>0</STORED> <DEFAULT>0</DEFAULT> </MARK-MEDIA-THRESHOLD>                 | ^SS   |

<!-- image -->

Table 19 • Saved Settings (Continued)

| Description                                                 | XML Output                                                                                                                                                | ZPL   |
|-------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------|-------|
| Calibration: intensity of media LED                         | <MEDIA-LED-INTENSITY MIN='0' MAX='255'> <CURRENT>13</CURRENT> <STORED>13</STORED> <DEFAULT>13</DEFAULT> </MEDIA-LED-INTENSITY>                            | ^SS   |
| Calibration: intensity of ribbon LED                        | <RIBBON-LED-INTENSITY MIN='0' MAX='255'> <CURRENT>20</CURRENT> <STORED>20</STORED> <DEFAULT>20</DEFAULT> </RIBBON-LED-INTENSITY>                          | ^SS   |
| Calibration: intensity of mark LED sensing                  | <MARK-LED-INTENSITY MIN='0' MAX='255'> <CURRENT>0</CURRENT> <STORED>0</STORED> <DEFAULT>0</DEFAULT> </MARK-LED-INTENSITY>                                 | ^SS   |
| Set language preference to ZPL or ZPL II                    | <LABEL-DESCRIPTION-LANGUAGE ENUM='ZPL II, ZPL'> <CURRENT>ZPL II</CURRENT> <STORED>ZPL II</STORED> <DEFAULT>ZPL II</DEFAULT> </LABEL-DESCRIPTION-LANGUAGE> | ^SZ   |
| Adjust the rest position of media after printing            | <TEAR-OFF-POSITION MIN='-120' MAX='120'> <CURRENT>0</CURRENT> <STORED>0</STORED> <DEFAULT>0</DEFAULT> </TEAR-OFF-POSITION>                                | ~TA   |
| Printer sleep: (PA400/PT400 only)                           | <FORCE-OFF-MODE BOOL='Y,N'> <CURRENT>N</CURRENT> <STORED>N</STORED> <DEFAULT>N</DEFAULT> </FORCE-OFF-MODE>                                                | ^ZZ   |
| Printer sleep: set number of idle seconds prior to shutdown | <IDLE-TIME MIN='0' MAX='999999'> <CURRENT>0</CURRENT> <STORED>0</STORED> <DEFAULT>0</DEFAULT> </IDLE-TIME>                                                | ^ZZ   |

Table 19 • Saved Settings (Continued)

| Description                            | XML Output                                                                                                                                                                | ZPL   |
|----------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------|
| Set backfeed percent                   | <BACKFEED-PERCENT ENUM='OFF, BEFORE, 10%, 20%, 30%, 40%, 50%, 60%, 70%, 80%, DEFAULT, AFTER'> <CURRENT>NO YES</CURRENT> <STORED>NO YES</STORED> <DEFAULT>NO YES</DEFAULT> | ~JB   |
| Control on-line verifier device        | <VERIFIER-PORT ENUM='OFF, VER-RPRNT ERR, VER-THRUPUT'> <CURRENT>OFF</CURRENT> <STORED>OFF</STORED> <DEFAULT>OFF</DEFAULT> </VERIFIER-PORT>                                | ^JJ   |
| Control on-line applicator port        | <APPLICATOR-PORT ENUM='OFF, MODE 1, MODE 2, MODE 3, MODE 4'> <CURRENT>OFF</CURRENT> <STORED>OFF</STORED> <DEFAULT>OFF</DEFAULT> </APPLICATOR-PORT>                        | ^JJ   |
| Set communication: baud rate           | <BAUD ENUM='110, 300, 600, 1200, 2400, 4800, 9600, 14400, 19200, 28800, 38400, 57600'> <CURRENT>9600</CURRENT> <STORED>9600</STORED> <DEFAULT>9600</DEFAULT>              | ^SC   |
| Set communication: number of stop bits | <STOP-BITS ENUM='1 STOP BIT, 2 STOP BITS'> <CURRENT>1 STOP BIT</CURRENT> <STORED>1 STOP BIT</STORED> <DEFAULT>1 STOP BIT</DEFAULT> </STOP-BITS>                           | ^SC   |
| Set communication: parity options      | <PARITY ENUM='NONE, ODD, EVEN'> <CURRENT>NONE</CURRENT> <STORED>NONE</STORED> <DEFAULT>EVEN</DEFAULT> </PARITY>                                                           | ^SC   |

Table 19 • Saved Settings (Continued)

| Description                                     | XML Output                                                                                                                          | ZPL   |
|-------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------|-------|
| Set communication: handshake options            | <HANDSHAKE ENUM='XON/XOFF, DSR/DTR'> <CURRENT>XON/XOFF</CURRENT> <STORED>XON/XOFF</STORED> <DEFAULT>XON/XOFF</DEFAULT> </HANDSHAKE> | ^SC   |
| Set communication: protocol options             | <PROTOCOL ENUM='NONE, ZEBRA, ACK_NAK'> <CURRENT>NONE</CURRENT> <STORED>NONE</STORED> <DEFAULT>NONE</DEFAULT> </PROTOCOL>            | ^SC   |
| Mode protection: darkness mode                  | <DISABLE-DARKNESS BOOL='Y,N'> <CURRENT>N</CURRENT> <STORED>N</STORED> <DEFAULT>N</DEFAULT> </DISABLE-DARKNESS>                      | ^MP   |
| Mode protection: position mode                  | <DISABLE-POSITION BOOL='Y,N'> <CURRENT>N</CURRENT> <STORED>N</STORED> <DEFAULT>N</DEFAULT>                                          | ^MP   |
| Mode protection: calibration mode               | <DISABLE-CALIBRATION BOOL='Y,N'> <CURRENT>N</CURRENT> <STORED>N</STORED> <DEFAULT>N</DEFAULT> </DISABLE-CALIBRATION>                | ^MP   |
| Mode protection: save calibration settings mode | <DISABLE-SAVE-CONFIGURATION BOOL='Y,N'> <CURRENT>N</CURRENT> <STORED>N</STORED> <DEFAULT>N</DEFAULT> </DISABLE-SAVE-CONFIGURATION>  | ^MP   |
| Mode protection: pause key                      | <DISABLE-PAUSE-KEY BOOL='Y,N'> <CURRENT>N</CURRENT> <STORED>N</STORED> <DEFAULT>N</DEFAULT> </DISABLE-PAUSE-KEY>                    | ^MP   |

Table 19 • Saved Settings (Continued)

| Description                        | XML Output                                                                                                                             | ZPL   |
|------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------|-------|
| Mode protection: feed key          | <DISABLE-FEED-KEY BOOL='Y,N'> <CURRENT>N</CURRENT> <STORED>N</STORED> <DEFAULT>N</DEFAULT> </DISABLE-FEED-KEY>                         | ^MP   |
| Mode protection: cancel key        | <DISABLE-CANCEL-KEY BOOL='Y,N'> <CURRENT>N</CURRENT> <STORED>N</STORED> <DEFAULT>N</DEFAULT> </DISABLE-CANCEL-KEY>                     | ^MP   |
| Mode protection: menu changes mode | <DISABLE-MENU BOOL='Y,N'> <CURRENT>N</CURRENT> <STORED>N</STORED> <DEFAULT>N</DEFAULT> </DISABLE-MENU>                                 | ^MP   |
| Map drive B: card memory           | <DRIVE-B ENUM='R, E, B'> <CURRENT>B</CURRENT> <STORED>B</STORED> <DEFAULT>B</DEFAULT> </DRIVE-B>                                       | ^CM   |
| Map drive E: on- board flash       | <DRIVE-E ENUM='R, E, B'> <CURRENT>E</CURRENT> <STORED>E</STORED> <DEFAULT>E</DEFAULT> </DRIVE-E>                                       | ^CM   |
| Map drive R: on- board RAM         | <DRIVE-R ENUM='R, E, B'> <CURRENT>R</CURRENT> <STORED>R</STORED> <DEFAULT>R</DEFAULT>                                                  | ^CM   |
| Radio frequency ID settings        | <RFID-TYPE ENUM='NONE, AUTO DETECT, TAG-IT, ICODE'> <CURRENT>NONE</CURRENT> <STORED>NONE</STORED> <DEFAULT>NONE</DEFAULT> </RFID-TYPE> | ^RS   |

## Format Settings

Table 20 • Format Settings

| Description                                 | XML Output                                                     | ZPL II   |
|---------------------------------------------|----------------------------------------------------------------|----------|
| Code validation settings                    | <CODE-VALIDATION BOOL='Y,N'>N</CODE- VALIDATION>               | ^CV      |
| Reprint partially printed label             | <REPRINT-AFTER-ERROR BOOL='Y,N'>Y</REPRINT- AFTER-ERROR>       | ^JZ      |
| Set default measurement                     | <MODE-UNITS ENUM='DOTS, INCHES, MILLIMETERS'>DOTS</MODE-UNITS> | ^MU      |
| Defines label length                        | <LABEL-LENGTH MIN='0' MAX='9999'>1244</LABEL-LENGTH>           | ^LL      |
| Reverse field print color                   | <LABEL-REVERSE BOOL='Y,N'>N</LABEL-REVERSE>                    | ^LR      |
| Compatibility with smaller formats (Z- 130) | <LABEL-SHIFT MIN='-9999' MAX='9999'>0</LABEL-SHIFT>            | ^LS      |
| Set label home position                     | <LABEL-HOME> <X-AXIS MIN='0' MAX='32000'>0</X-AXIS>            |          |
| Adjust darkness relative to current setting | <RELATIVE-DARKNESS MIN='-30' MAX='30'>0</RELATIVE-DARKNESS>    | ^MD      |
| Set print speed                             | <PRINT-RATE MIN='1' MAX='4'>2</PRINT-RATE>                     | ^PR      |
| Set slew speed                              | <SLEW-RATE MIN='1' MAX='4'>6</SLEW-RATE>                       | ^PR      |
| Set backfeed speed                          | <BACKFEED-RATE MIN='1' MAX='4'>2</BACKFEED- RATE>              | ^PR      |
| Printhead test:                             | <MANUAL-RANGE BOOL='Y,N'>N</MANUAL-RANGE>                      | ^JT      |
| Printhead test:                             | <FIRST-ELEMENT MIN='0' MAX='9999'>0</FIRST- ELEMENT>           | ^JT      |
| Printhead test:                             | <LAST-ELEMENT MIN='0' MAX='9999'>9999</LAST- ELEMENT>          | ^JT      |
| Font: set default type                      | <FONT-LETTER MIN='0' MAX='255'>65</FONT- LETTER>               | ^CF      |
| Font: set default height                    | <HEIGHT MIN='1' MAX='9999'>9</HEIGHT>                          | ^CF      |
| Font: set default width                     | <WIDTH MIN='1' MAX='9999'>5</WIDTH>                            | ^CF      |
| Bar code: print ratio                       | <RATIO MIN='2.0' MAX='3.0'>3.0</RATIO>                         | ^BY      |
| Bar code: width in dots                     | <MODULE-WIDTH MIN='1' MAX='10'>2</MODULE- WIDTH>               | ^BY      |
| Bar code: height in dots                    | <HEIGHT MIN='1' MAX='9999'>10</HEIGHT>                         | ^BY      |

Table 20 • Format Settings (Continued)

| Description    | XML Output                                                                                             | ZPL II   |
|----------------|--------------------------------------------------------------------------------------------------------|----------|
| Head-test info | <FATAL BOOL='Y,N'> <CURRENT>N</CURRENT> <STORED>N</STORED> <DEFAULT>N</DEFAULT> </FATAL>               |          |
| Head-test info | <INTERVAL MIN='0' MAX='9999'> <CURRENT>0</CURRENT> <STORED>0</STORED> <DEFAULT>0</DEFAULT> </INTERVAL> |          |

<!-- image -->

## Status Information

Table 21 • Status Information

| Description            | XML Output                                                                                                                                            | ZPL   |
|------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------|-------|
| Set batch print        | <TOTAL-LABELS-IN-BATCH>1</TOTAL-LABELS-IN- BATCH>                                                                                                     |       |
| Batch print status     | <LABELS-REMAINING-IN-BATCH>0</LABELS- REMAINING-IN- BATCH>                                                                                            |       |
| Printhead temperature  | <PRINTHEAD-TEMP> <OVERTEMP-THRESHOLD>300</OVERTEMP- THRESHOLD> <UNDERTEMP-THRESHOLD>-1</UNDERTEMP- THRESHOLD> <CURRENT>24</CURRENT> </PRINTHEAD-TEMP> |       |
| Powersupply            | <OVERTEMP-THRESHOLD>70</OVERTEMP-THRESHOLD>                                                                                                           |       |
| Powersupply            | <CURRENT>27</CURRENT>                                                                                                                                 |       |
| Battery over-temp      | <OVERTEMP-THRESHOLD>50</OVERTEMP-THRESHOLD>                                                                                                           |       |
| Battery temp           | <CURRENT>0</CURRENT>                                                                                                                                  |       |
| Battery voltage        | <CURRENT-BATTERY-VOLTAGE>0</CURRENT-BATTERY- VOLTAGE>                                                                                                 |       |
| Number of formats      | <NUMBER-OF-FORMATS>1</NUMBER-OF-FORMATS> <PARTIAL-FORMAT-IN-PROGRESS BOOL='Y,N'>N</PARTIAL-FORMAT-IN-PROGRESS>                                        |       |
| Printer pause          | <PAUSE BOOL='Y,N'>N</PAUSE>                                                                                                                           |       |
| Out of paper           | <PAPER-OUT BOOL='Y,N'>N</PAPER-OUT>                                                                                                                   |       |
| Out of ribbon          | <RIBBON-OUT BOOL='Y,N'>N</RIBBON-OUT>                                                                                                                 |       |
| Head-element status    | <FAILED BOOL='Y,N'>N</FAILED>                                                                                                                         |       |
| Printer cover open     | <COVER-OPEN BOOL='Y,N'>N</COVER-OPEN>                                                                                                                 |       |
| Printhead open         | <HEAD-OPEN BOOL='Y,N'>N</HEAD-OPEN>                                                                                                                   |       |
| Powersupply over- temp | <POWERSUPPLY-OVERTEMP-ERROR BOOL='Y,N'>N</POWERSUPPLY-OVERTEMP-ERROR>                                                                                 |       |

Table 21 • Status Information (Continued)

| Description           | XML Output                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | ZPL   |
|-----------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------|
| Cut error             | <CUTTER-JAM-ERROR BOOL='Y,N'>N</CUTTER-JAM- ERROR> <RIBBON-TENSION-ERROR BOOL='Y,N'>N</RIBBON- TENSION-ERROR> <VERIFIER-ERROR BOOL='Y,N'>N</VERIFIER- ERROR> <CONFIG-LOST-ERROR BOOL='Y,N'>Y</CONFIG- LOST-ERROR> <RAM-ALLOCATION-ERROR BOOL='Y,N'>N</RAM- ALLOCATION-ERROR> <BITMAP-ALLOCATION-ERROR BOOL='Y,N'>N</BITMAP-ALLOCATION-ERROR> <STORED-FORMAT-ERROR BOOL='Y,N'>N</STORED- FORMAT-ERROR> <STORED-GRAPHIC-ERROR BOOL='Y,N'>N</STORED- GRAPHIC-ERROR> <STORED-BITMAP-ERROR BOOL='Y,N'>N</STORED- BITMAP-ERROR> <STORED-FONT-ERROR BOOL='Y,N'>N</STORED- FONT-ERROR> <CACHE-MEMORY-ERROR BOOL='Y,N'>N</CACHE- MEMORY-ERROR> |       |
| Replace battery       | <BATTERY-DEAD-ERROR BOOL='Y,N'>N</BATTERY- DEAD-ERROR>                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |       |
| Battery over-temp     | <BATTERY-OVERTEMP-ERROR BOOL='Y,N'>N</BATTERY-OVERTEMP-ERROR>                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |       |
| Low battery voltage   | <BATTERY-VOLTAGE-ERROR BOOL='Y,N'>N</BATTERY-VOLTAGE-ERROR>                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |       |
| Printhead under- temp | <HEAD-UNDERTEMP-WARNING BOOL='Y,N'>N</HEAD- UNDERTEMP-WARNING>                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |       |
| Printhead over- temp  | <HEAD-OVERTEMP-ERROR BOOL='Y,N'>N</HEAD- OVERTEMP-ERROR> <RIBBON-IN-WARNING BOOL='Y,N'>Y</RIBBON-IN- WARNING>                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |       |

Table 21 • Status Information (Continued)

| Description         | XML Output                                                                                                                                                                                                                                                                                                                                                  | ZPL   |
|---------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------|
| Low ribbon warning  | <RIBBON-LOW-WARNING BOOL='Y,N'>N</RIBBON- LOW-WARNING>                                                                                                                                                                                                                                                                                                      |       |
| Low battery warning | <BATTERY-LOW-WARNING BOOL='Y,N'>N</BATTERY- LOW-WARNING> <BUFFER-FULL-ERROR BOOL='Y,N'>N</BUFFER- FULL-ERROR> <PRINTER-ODOMETER /> <CLOCK><DATE /><TIME /></CLOCK> <OBJECT MEMORY-LOCATION='B' TYPE='ZPL' FORMAT='ZPL' SIZE='36' PROTECTED='N'>GRF_TEST</OBJECT> <OBJECT MEMORY-LOCATION='B' TYPE='ZPL' FORMAT='ZPL' SIZE='60' PROTECTED='N'>ZEBRA</OBJECT> |       |

<!-- image -->

<!-- image -->

7

