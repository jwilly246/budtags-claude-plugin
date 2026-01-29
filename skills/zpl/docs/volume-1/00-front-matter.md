<!-- Source: ZPL II Programming Guide Volume 1 -->
<!-- Section: Front Matter, TOC, Copyright -->
<!-- Generated: 2025-11-02 04:52:35 -->

<!-- image -->

## ZPL II ®

## Programming Guide

Volume One

<!-- image -->

© 2005 ZIH Corp.

The copyrights in this manual and the label print engine described therein are owned by Zebra Technologies Corporation. Unauthorized reproduction of this manual or the software in the label print engine may result in imprisonment of up to one year and fines of up to $10,000 (17 U.S.C.506). Copyright violators may be subject to civil liability.

This product may contain ZPL ® , ZPL II ® , and ZebraLink™ programs; Element Energy Equalizer ® Circuit; E3 ® ; and AGFA fonts. Software © ZIH Corp. All rights reserved worldwide. ZebraLink and all product names and numbers are trademarks, and Zebra, the Zebra logo, ZPL, ZPL II, Element Energy Equalizer Circuit, and E3 Circuit are registered trademarks of ZIH Corp. All rights reserved worldwide. CG Triumvirate is a trademark of AGFA Monotype Corporation. All rights reserved worldwide. CG Triumvirate™ font © AGFA Monotype Corporation. Intellifont ®  portion © AGFA Monotype Corporation. All rights reserved worldwide. UFST is a registered trademark of AGFA Monotype Corporation. All rights reserved worldwide. All other brand names, product names, or trademarks belong to their respective holders.

## Part # 45541L-002 Rev. A

## Contents

| Contents                         | . . . . . . . . . . . . . . . . . . .   | . . . i   |
|----------------------------------|-----------------------------------------|-----------|
| Proprietary Statement .          | . . . . . . . .                         | . xiii    |
| Preface . .                      | . . . . . . . . . . . . . . . . . . .   | . xv      |
| Who Should Use This Document .   | Who Should Use This Document .          | . xvi     |
| How This Document Is Organized . | How This Document Is Organized .        | . xvi     |
| Contacts .                       | . . . . . . . . . . . . . . . . . . .   | . xvi     |
| Support .                        | . . . . . . . . . . . . . . . . .       | . xvii    |
| Document Conventions. .          | . . . . . . .                           | . xvii    |
| Related Documents .              | . . . . . . . . . .                     | xviii     |
| 1 • Introduction .               | . . . . . . . . . . . . .               | . . 1     |
| 2 • ZPL Commands . .             | . . . . . . . . .                       | . . 3     |
| Basic ZPL Exercises. .           | . . . . . . . . .                       | . . 5     |
| Before you begin.                | . . . . . . . . . .                     | . . 5     |
| ^A                               | Scalable/Bitmapped Font . .             | . 12      |
| ^A@                              | Use Font Name to Call Font              | . 15      |
| ^B1                              | Code 11 Bar Code . . . . . .            | . 17      |
| ^B2                              | Interleaved 2 of 5 Bar Code             | . 19      |
| ^B3                              | Code 39 Bar Code . . . . . . .          | . 21      |
| ^B4                              | Code 49 Bar Code . . . . . . .          | . 25      |
| ^B5                              | Planet Code bar code . . . .            | . 29      |
| ^B7                              | PDF417 Bar Code . . . . . . .           | . 30      |
| ^B8                              | EAN-8 Bar Code . . . . . . . .          | . 35      |
| ^B9                              | UPC-E Bar Code . . . . . . . .          | . 37      |
| ^BA                              | Code 93 Bar Code . . . . . . .          | . 39      |
| ^BB                              | CODABLOCK Bar Code . .                  | . 43      |

<!-- image -->

| ^BC   | Code 128 Bar Code (Subsets A, B, and C) .                       | . 47    |
|-------|-----------------------------------------------------------------|---------|
| ^BD   | UPS MaxiCode Bar Code . . . . . . . . . . . . . .               | . 60    |
| ^BE   | EAN-13 Bar Code . . . . . . . . . . . . . . . . . . . .         | . 63    |
| ^BF   | Micro-PDF417 Bar Code . . . . . . . . . . . . . . .             | . 65    |
| ^BI   | Industrial 2 of 5 Bar Codes . . . . . . . . . . . . .           | . 68    |
| ^BJ   | Standard 2 of 5 Bar Code . . . . . . . . . . . . . . .          | . 70    |
| ^BK   | ANSI Codabar Bar Code . . . . . . . . . . . . . . .             | . 72    |
| ^BL   | LOGMARS Bar Code . . . . . . . . . . . . . . . . . .            | . 74    |
| ^BM   | MSI Bar Code . . . . . . . . . . . . . . . . . . . . . . .      | . 76    |
| ^BO   | Aztec Bar Code Parameters . . . . . . . . . . . .               | . 78    |
| ^BP   | Plessey Bar Code . . . . . . . . . . . . . . . . . . . .        | . 80    |
| ^BQ   | QR Code Bar Code . . . . . . . . . . . . . . . . . . .          | . 82    |
| ^BR   | RSS (Reduced Space Symbology) Bar Code                          | . 88    |
| ^BS   | UPC/EAN Extensions . . . . . . . . . . . . . . . . .            | . 90    |
| ^BT   | TLC39 bar code . . . . . . . . . . . . . . . . . . . . . .      | . 93    |
| ^BU   | UPC-A Bar Code . . . . . . . . . . . . . . . . . . . . .        | . 95    |
| ^BX   | Data Matrix Bar Code . . . . . . . . . . . . . . . . .          | . 97    |
| ^BY   | Bar Code Field Default . . . . . . . . . . . . . . . .          | 101     |
| ^BZ   | POSTNET Bar Code . . . . . . . . . . . . . . . . . .            | 103     |
| ^CC   | ~CC Change Carets . . . . . . . . . . . . . . . .               | 105     |
| ^CD   | ~CD Change Delimiter . . . . . . . . . . . . . .                | 106     |
| ^CF   | Change Alphanumeric Default Font . . . . .                      | 107     |
| ^CI   | Change International Font . . . . . . . . . . . . . .           | 109     |
| ^CM   | Change Memory Letter Designation . . . .                        | .112    |
| ^CO   | Cache On . . . . . . . . . . . . . . . . . . . . . . . . . .    | .113    |
| ^CT   | ~CT Change Tilde . . . . . . . . . . . . . . . . . .            | .115    |
| ^CV   | Code Validation . . . . . . . . . . . . . . . . . . . . . .     | .116    |
| ^CW   | Font Identifier . . . . . . . . . . . . . . . . . . . . . . .   | .118    |
| ~DB   | Download Bitmap Font . . . . . . . . . . . . . . . .            | 120     |
| ~DE   | Download Encoding . . . . . . . . . . . . . . . . .             | 122     |
| ^DF   | Download Format . . . . . . . . . . . . . . . . . . .           | 123     |
| ~DG   | Download Graphics . . . . . . . . . . . . . . . . . .           | 124     |
| ~DN   | Abort Download Graphic . . . . . . . . . . . . . .              | 126     |
| ~DS   | Download Scalable Font . . . . . . . . . . . . . .              | 127     |
| ~DT   | Download TrueType Font . . . . . . . . . . . . .                | 128     |
| ~DU   | Download Unbounded TrueType Font . . .                          | 129     |
| ~DY   | Download Graphics . . . . . . . . . . . . . . . . . .           | 130     |
| ~EG   | Erase Download Graphics . . . . . . . . . . . .                 | 131 132 |
| ^FB   | Field Block . . . . . . . . . . . . . . . . . . . . . . . . . . |         |
| ^FC   | Field Clock (for Real-Time Clock) . . . . . . . .               | 134     |

| ^FD   | Field Data . . . . . . . . . . . . . . . . . . . .   | 135     |
|-------|------------------------------------------------------|---------|
| ^FH   | Field Hexadecimal Indicator . . . . . .              | 136     |
| ^FM   | Multiple Field Origin Locations . . . .              | 137     |
| ^FN   | Field Number . . . . . . . . . . . . . . . . . .     | 139     |
| ^FO   | Field Origin . . . . . . . . . . . . . . . . . . .   | 140     |
| ^FP   | Field Parameter . . . . . . . . . . . . . . .        | 141     |
| ^FR   | Field Reverse Print . . . . . . . . . . . .          | 142     |
| ^FS   | Field Separator . . . . . . . . . . . . . . . .      | 143     |
| ^FT   | Field Typeset . . . . . . . . . . . . . . . . .      | 144     |
| ^FV   | Field Variable . . . . . . . . . . . . . . . .       | 148     |
| ^FW   | Field Orientation . . . . . . . . . . . . . . .      | 149     |
| ^FX   | Comment . . . . . . . . . . . . . . . . . . . . .    | 150     |
| ^GB   | Graphic Box . . . . . . . . . . . . . . . . .        | 151     |
| ^GC   | Graphic Circle . . . . . . . . . . . . . . . .       | 153     |
| ^GD   | Graphic Diagonal Line . . . . . . . . . .            | 154     |
| ^GE   | Graphic Ellipse . . . . . . . . . . . . . . .        | 155     |
| ^GF   | Graphic Field . . . . . . . . . . . . . . . . .      | 156     |
| ^GS   | Graphic Symbol . . . . . . . . . . . . . . .         | 158     |
| ~HB   | Battery Status . . . . . . . . . . . . . . . . .     | 160     |
| ~HD   | Head Temperature Information . . . .                 | 161     |
| ^HF   | Graphic Symbol . . . . . . . . . . . . . . . .       | 162     |
| ^HG   | Host Graphic . . . . . . . . . . . . . . . . .       | 163     |
| ^HH   | Configuration Label Return . . . . . . .             | 164     |
| ~HI   | Host Identification . . . . . . . . . . . . .        | 165     |
| ~HM   | Host RAM Status . . . . . . . . . . . . . .          | 166     |
| ~HS   | Host Status Return . . . . . . . . . . . . .         | 167     |
| ~HU   | Return ZebraNet Alert Configuration                  | 170     |
| ^HV   | Host Verification . . . . . . . . . . . . . . . .    | 171     |
| ^HW   | Host Directory List . . . . . . . . . . . . .        | 172     |
| ^HY   | Upload Graphics . . . . . . . . . . . . . . .        | 174     |
| ^HZ   | Display Description Information . . .                | 175     |
| ^ID   | Object Delete . . . . . . . . . . . . . . . . .      | 177     |
| ^IL   | Image Load . . . . . . . . . . . . . . . . . .       | 179     |
| ^IM   | Image Move . . . . . . . . . . . . . . . . . .       | 181     |
| ^IS   | Image Save . . . . . . . . . . . . . . . . . .       | 182     |
| ~JA   | Cancel All . . . . . . . . . . . . . . . . . . . .   | 184     |
| ^JB   | Initialize Flash Memory . . . . . . . . .            | 185     |
| ~JB   | Reset Optional Memory . . . . . . . . . . .          | 186 187 |
| ~JC   | Set Media Sensor Calibration . .                     |         |
| ~JD   | Enable Communications Diagnostics                    | 188     |

| ~JE   | Disable Diagnostics . . . . . . . . . . . . . . . . . . . . . . . .         |     189 |
|-------|-----------------------------------------------------------------------------|---------|
| ~JF   | Set Battery Condition . . . . . . . . . . . . . . . . . . . . . . .         | 190     |
| ~JG   | Graphing Sensor Calibration . . . . . . . . . . . . . . . . . .             | 191     |
| ^JJ   | Set Auxiliary Port . . . . . . . . . . . . . . . . . . . . . . . . . .      | 192     |
| ~JL   | Set Label Length . . . . . . . . . . . . . . . . . . . . . . . . . .        | 194     |
| ^JM   | Set Dots per Millimeter . . . . . . . . . . . . . . . . . . . . .           | 195     |
| ~JN   | Head Test Fatal . . . . . . . . . . . . . . . . . . . . . . . . . . .       | 196     |
| ~JO   | Head Test Non fatal . . . . . . . . . . . . . . . . . . . . . . . .         | 197     |
| ~JP   | Pause and Cancel Format . . . . . . . . . . . . . . . . . .                 | 198     |
| ~JR   | Power On Reset . . . . . . . . . . . . . . . . . . . . . . . . . . .        | 199     |
| ^JS   | Sensor Select . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .   | 200     |
| ~JS   | Change Backfeed Sequence . . . . . . . . . . . . . . . . .                  | 201     |
| ^JT   | Head Test Interval . . . . . . . . . . . . . . . . . . . . . . . . .        | 203     |
| ^JU   | Configuration Update . . . . . . . . . . . . . . . . . . . . . .            | 204     |
| ^JW   | Set Ribbon Tension . . . . . . . . . . . . . . . . . . . . . . . . .        | 205     |
| ~JX   | Cancel Current Partially Input Format . . . . . . . . . . .                 | 206     |
| ^JZ   | Reprint After Error . . . . . . . . . . . . . . . . . . . . . . . . . .     | 207     |
| ~KB   | Kill Battery (Battery Discharge Mode) . . . . . . . . . .                   | 208     |
| ^KD   | Select Date and Time Format (for Real Time Clock)                           | 209     |
| ^KL   | Define Language . . . . . . . . . . . . . . . . . . . . . . . . . .         | 210     |
| ^KN   | Define Printer Name . . . . . . . . . . . . . . . . . . . . . . . .         |   0.211 |
| ^KP   | Define Password . . . . . . . . . . . . . . . . . . . . . . . . . .         | 212     |
| ^LH   | Label Home . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .    | 213     |
| ^LL   | Label Length . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .    | 214     |
| ^LR   | Label Reverse Print . . . . . . . . . . . . . . . . . . . . . . . . .       | 215     |
| ^LS   | Label Shift . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . | 216     |
| ^LT   | Label Top . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . | 217     |
| ^MC   | Map Clear . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .   | 218     |
| ^MD   | Media Darkness . . . . . . . . . . . . . . . . . . . . . . . . . . .        | 219     |
| ^MF   | Media Feed . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .    | 220     |
| ^ML   | Maximum Label Length . . . . . . . . . . . . . . . . . . . . .              | 221     |
| ^MM   | Print Mode . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .  | 222     |
| ^MN   | Media Tracking . . . . . . . . . . . . . . . . . . . . . . . . . . . .      | 223     |
| ^MP   | Mode Protection . . . . . . . . . . . . . . . . . . . . . . . . . . .       | 224     |
| ^MT   | Media Type . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .    | 225     |
| ^MU   | Set Units of Measurement . . . . . . . . . . . . . . . . . . .              | 226     |
| ^MW   | Modify Head Cold Warning . . . . . . . . . . . . . . . . . . .              | 228     |
| ~NC   | Network Connect . . . . . . . . . . . . . . . . . . . . . . . . . .         | 229     |
| ^NI   | Network ID Number . . . . . . . . . . . . . . . . . . . . . . . .           | 230     |
| ~NR   | Set All Network Printers Transparent . . . . . . . . . . .                  | 231     |

| ^NS   | Change Networking Settings . . . . . . . . . . . . . .                |   232 |
|-------|-----------------------------------------------------------------------|-------|
| ~NT   | Set Currently Connected Printer Transparent .                         |   233 |
| ^PF   | Slew Given Number of Dot Rows . . . . . . . . . . .                   |   234 |
| ^PH   | ~PH Slew to Home Position . . . . . . . . . . . . . .                 |   235 |
| ^PM   | Printing Mirror Image of Label . . . . . . . . . . . . .              |   236 |
| ^PO   | Print Orientation . . . . . . . . . . . . . . . . . . . . . . . .     |   237 |
| ^PP   | ~PP Programmable Pause . . . . . . . . . . . . . .                    |   238 |
| ^PQ   | Print Quantity . . . . . . . . . . . . . . . . . . . . . . . . . .    |   239 |
| ^PR   | Print Rate . . . . . . . . . . . . . . . . . . . . . . . . . . . . .  |   240 |
| ~PR   | Applicator Reprint . . . . . . . . . . . . . . . . . . . . . . .      |   243 |
| ~PS   | Print Start . . . . . . . . . . . . . . . . . . . . . . . . . . . . . |   244 |
| ^PW   | Print Width . . . . . . . . . . . . . . . . . . . . . . . . . . . .   |   245 |
| ~RO   | Reset Advanced Counter . . . . . . . . . . . . . . . . .              |   246 |
| ^SC   | Set Serial Communications . . . . . . . . . . . . . . .               |   247 |
| ~SD   | Set Darkness . . . . . . . . . . . . . . . . . . . . . . . . . .      |   248 |
| ^SE   | Select Encoding . . . . . . . . . . . . . . . . . . . . . . .         |   249 |
| ^SF   | Serialization Field (with a Standard ^FD String)                      |   250 |
| ^SL   | Set Mode and Language (for Real-Time Clock)                           |   252 |
| ^SN   | Serialization Data . . . . . . . . . . . . . . . . . . . . . . .      |   253 |
| ^SO   | Set Offset (for Real-Time Clock) . . . . . . . . . . . .              |   255 |
| ^SP   | Start Print . . . . . . . . . . . . . . . . . . . . . . . . . . . . . |   256 |
| ^SQ   | Halt ZebraNet Alert . . . . . . . . . . . . . . . . . . . . . .       |   258 |
| ^SR   | Set Printhead Resistance . . . . . . . . . . . . . . . . .            |   259 |
| ^SS   | Set Media Sensors . . . . . . . . . . . . . . . . . . . . . .         |   260 |
| ^ST   | Set Date and Time (for Real-Time Clock) . . . .                       |   262 |
| ^SX   | Set ZebraNet Alert . . . . . . . . . . . . . . . . . . . . . . .      |   263 |
| ^SZ   | Set ZPL . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . |   265 |
| ~TA   | Tear-off Adjust Position . . . . . . . . . . . . . . . . . . .        |   266 |
| ^TO   | Transfer Object . . . . . . . . . . . . . . . . . . . . . . . . .     |   267 |
| ~WC   | Print Configuration Label . . . . . . . . . . . . . . . . . .         |   269 |
| ^WD   | Print Directory Label . . . . . . . . . . . . . . . . . . . . .       |   270 |
| ^XA   | Start Format . . . . . . . . . . . . . . . . . . . . . . . . . . .    |   272 |
| ^XB   | Suppress Backfeed . . . . . . . . . . . . . . . . . . . . . .         |   273 |
| ^XF   | Recall Format . . . . . . . . . . . . . . . . . . . . . . . . . .     |   274 |
| ^XG   | Recall Graphic . . . . . . . . . . . . . . . . . . . . . . . . . .    |   275 |
| ^XZ   | End Format . . . . . . . . . . . . . . . . . . . . . . . . . . .      |   276 |
| ^ZZ   | Printer Sleep . . . . . . . . . . . . . . . . . . . . . . . . . .     |   277 |

v

| A • RFID Commands . . . . . .                                                                 | . . . . . . . . . . . . . . . . . . . . . .                                                   | . 279   |
|-----------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------|---------|
| RFID                                                                                          | Command Overview . . . . . . . . . . . . . . . . . . . . . . . . . .                          | . . 280 |
| ^HR                                                                                           | Calibrate RFID Transponder Position . . . . . . . . . . . .                                   | . . 281 |
| ^RB                                                                                           | Define EPC Data Structure . . . . . . . . . . . . . . . . . . . .                             | . . 284 |
| ^RF                                                                                           | Read or Write RFID Format . . . . . . . . . . . . . . . . . . . .                             | . . 286 |
| ^RM                                                                                           | Enable RFID Motion . . . . . . . . . . . . . . . . . . . . . . . . . .                        | . . 288 |
| ^RN                                                                                           | Detect Multiple RFID Tags in Encoding Field . . . . . . .                                     | . . 289 |
| ~RO                                                                                           | Reset Advanced Counters . . . . . . . . . . . . . . . . . . . . .                             | . . 290 |
| ^RR                                                                                           | Specify RFID Retries for a Block . . . . . . . . . . . . . . . .                              | . . 292 |
| ^RS                                                                                           | RFID Setup . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .                    | . . 293 |
| ^RT                                                                                           | Read RFID Tag . . . . . . . . . . . . . . . . . . . . . . . . . . . . .                       | . . 297 |
| ^RW                                                                                           | Set RFID Read and Write Power Levels . . . . . . . . . .                                      | . . 299 |
| ^RZ                                                                                           | Set RFID Tag Password . . . . . . . . . . . . . . . . . . . . . . .                           | . . 300 |
| ^WT                                                                                           | Write Tag . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .                 | . . 301 |
| ^WV                                                                                           | Verify RFID Write Operation . . . . . . . . . . . . . . . . . . . .                           | . . 303 |
| B • Wireless Print Server Commands . . . . . . . . .                                          | B • Wireless Print Server Commands . . . . . . . . .                                          | . . 305 |
| ^KP                                                                                           | Define Printer Password . . . . . . . . . . . . . . . . . . . . . .                           | . . 306 |
| ^NB                                                                                           | Search for Wired Print Server during Network Boot . .                                         | . . 307 |
| ^NN                                                                                           | Set SNMP . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .                    | . . 308 |
| ^NP                                                                                           | Set Primary/Secondary Device . . . . . . . . . . . . . . . . .                                | . . 309 |
| ^NS                                                                                           | Change Wired Networking Settings . . . . . . . . . . . . . .                                  | . . 310 |
| ^NT                                                                                           | Set SMTP . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .                  | . . 312 |
| ^NW                                                                                           | Set Web Authentication Timeout Value . . . . . . . . . . .                                    | . . 313 |
| ^WA                                                                                           | Set Antenna Parameters . . . . . . . . . . . . . . . . . . . . . .                            | . . 314 |
| ^WE                                                                                           | Set Wireless Encryption Values . . . . . . . . . . . . . . . . .                              | . . 315 |
| ^WI                                                                                           | Change Wireless Network Settings . . . . . . . . . . . . . .                                  | . . 317 |
| ^WL                                                                                           | Set LEAP Parameters . . . . . . . . . . . . . . . . . . . . . . . .                           | . . 318 |
| ~WL                                                                                           | Print Network Configuration Label . . . . . . . . . . . . . . .                               | . . 319 |
| ^WP                                                                                           | Set Wireless Password . . . . . . . . . . . . . . . . . . . . . . .                           | . . 320 |
| ^WR                                                                                           | Set Transmit Rate . . . . . . . . . . . . . . . . . . . . . . . . . . .                       | . . 321 |
| ~WR                                                                                           | Reset Wireless Card . . . . . . . . . . . . . . . . . . . . . . . . .                         | . . 322 |
| ^WS                                                                                           | Set Wireless Card Values . . . . . . . . . . . . . . . . . . . . .                            | . . 323 |
| Index . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . | Index . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . | . 325   |

## Functional Table of Contents

<!-- image -->

| Abort Download Graphic . . . . . . . . . . . . .             | 126   |
|--------------------------------------------------------------|-------|
| ANSI Codabar Bar Code . . . . . . . . . . . . .              | . 72  |
| Applicator Reprint . . . . . . . . . . . . . . . . . .       | 243   |
| Aztec Bar Code Parameters. . . . . . . . . . .               | . 78  |
| Bar Code Field Default . . . . . . . . . . . . . .           | 101   |
| Battery Status . . . . . . . . . . . . . . . . . . . . .     | 160   |
| Cache On . . . . . . . . . . . . . . . . . . . . . . . . .   | 113   |
| Calibrate RFID Transponder Position. . . .                   | 281   |
| Cancel All . . . . . . . . . . . . . . . . . . . . . . . . . | 184   |
| Cancel Current Partially Input Format . . .                  | 206   |
| Change Alphanumeric Default Font . . . .                     | 107   |
| Change Backfeed Sequence . . . . . . . . .                   | 201   |
| Change Carets . . . . . . . . . . . . . . . . . . . .        | 105   |
| Change Delimiter . . . . . . . . . . . . . . . . . .         | 106   |
| Change International Font . . . . . . . . . . . .            | 109   |
| Change Memory Letter Designation . . .                       | 112   |
| Change Networking Settings . . . . . . . . .                 | 232   |
| Change Tilde . . . . . . . . . . . . . . . . . . . . .       | 115   |
| Change Wired Networking Settings . . . . .                   | 310   |
| Change Wireless Network Settings . . . . .                   | 317   |
| CODABLOCK Bar Code. . . . . . . . . . . . . .                | . 43  |
| Code 11 Bar Code . . . . . . . . . . . . . . . . .           | . 17  |
| Code 128 Bar Code (Subsets A, B, and C)                      | . 47  |
| Code 39 Bar Code . . . . . . . . . . . . . . . . . .         | . 21  |
| Code 49 Bar Code . . . . . . . . . . . . . . . . . .         | . 25  |
| Code 93 Bar Code . . . . . . . . . . . . . . . . . .         | . 39  |
| Code Validation . . . . . . . . . . . . . . . . . . . .      | 116   |
| Comment . . . . . . . . . . . . . . . . . . . . . . . . .    | 150   |
| Configuration Label Return. . . . . . . . . . . .            | 164   |

| Configuration Update . . . . . . . . . . . . . . . . .          | 204   |
|-----------------------------------------------------------------|-------|
| Data Matrix Bar Code . . . . . . . . . . . . . . . . .          | . 97  |
| Define EPC Data Structure. . . . . . . . . . . . . .            | 284   |
| Define Language . . . . . . . . . . . . . . . . . . . .         | 210   |
| Define Password . . . . . . . . . . . . . . . . . . . . .       | 212   |
| Define Printer Name . . . . . . . . . . . . . . . . . .         | 211   |
| Define Printer Password. . . . . . . . . . . . . . . .          | 306   |
| Detect Multiple RFID Tags in Encoding Field                     | 289   |
| Disable Diagnostics . . . . . . . . . . . . . . . . . .         | 189   |
| Display Description Information . . . . . . . . .               | 175   |
| Download Bitmap Font . . . . . . . . . . . . . . . .            | 120   |
| Download Encoding . . . . . . . . . . . . . . . . . .           | 122   |
| Download Format . . . . . . . . . . . . . . . . . . .           | 123   |
| Download Graphics . . . . . . . . . . . . . . . . . .           | 124   |
| Download Graphics . . . . . . . . . . . . . . . . . .           | 130   |
| Download Scalable Font . . . . . . . . . . . . . .              | 127   |
| Download TrueType Font . . . . . . . . . . . . .                | 128   |
| Download Unbounded TrueType Font . . . .                        | 129   |
| EAN-13 Bar Code . . . . . . . . . . . . . . . . . . . .         | . 63  |
| EAN-8 Bar Code. . . . . . . . . . . . . . . . . . . . . .       | . 35  |
| Enable Communications Diagnostics . . . . .                     | 188   |
| Enable RFID Motion . . . . . . . . . . . . . . . . . . .        | 288   |
| End Format . . . . . . . . . . . . . . . . . . . . . . . . .    | 276   |
| Erase Download Graphics . . . . . . . . . . . . .               | 131   |
| Field Block . . . . . . . . . . . . . . . . . . . . . . . . . . | 132   |
| Field Clock (for Real-Time Clock) . . . . . . . .               | 134   |
| Field Data . . . . . . . . . . . . . . . . . . . . . . . . . .  | 135   |
| Field Hexadecimal Indicator . . . . . . . . . . . .             | 136   |
| Field Number . . . . . . . . . . . . . . . . . . . . . . . .    | 139   |
| Field Orientation . . . . . . . . . . . . . . . . . . . . .     | 149   |
| Field Origin . . . . . . . . . . . . . . . . . . . . . . . . .  | 140   |
| Field Parameter . . . . . . . . . . . . . . . . . . . . .       | 141   |
| Field Reverse Print . . . . . . . . . . . . . . . . . .         | 142   |
| Field Separator . . . . . . . . . . . . . . . . . . . . . .     | 143   |
| Field Typeset . . . . . . . . . . . . . . . . . . . . . . .     | 144   |
| Field Variable . . . . . . . . . . . . . . . . . . . . . . .    | 148   |
| Font Identifier . . . . . . . . . . . . . . . . . . . . . . . . | 118   |
| Graphic Box . . . . . . . . . . . . . . . . . . . . . . . .     | 151   |
| Graphic Circle . . . . . . . . . . . . . . . . . . . . . . .    | 153   |
| Graphic Diagonal Line . . . . . . . . . . . . . . . .           | 154   |
| Graphic Ellipse . . . . . . . . . . . . . . . . . . . . . .     | 155   |
| Graphic Field . . . . . . . . . . . . . . . . . . . . . . .     | 156   |
| Graphic Symbol . . . . . . . . . . . . . . . . . . . . .        | 158   |
| Graphic Symbol . . . . . . . . . . . . . . . . . . . . . .      | 162   |

| Graphing Sensor Calibration . . . . . . .             | 191   |
|-------------------------------------------------------|-------|
| Halt ZebraNet Alert . . . . . . . . . . . . . . .     | 258   |
| Head Temperature Information. . . . . .               | 161   |
| Head Test Fatal . . . . . . . . . . . . . . . .       | 196   |
| Head Test Interval . . . . . . . . . . . . . .        | 203   |
| Head Test Non fatal . . . . . . . . . . . . .         | 197   |
| Host Directory List . . . . . . . . . . . . . .       | 172   |
| Host Graphic . . . . . . . . . . . . . . . . . .      | 163   |
| Host Identification . . . . . . . . . . . . . .       | 165   |
| Host RAM Status . . . . . . . . . . . . . . .         | 166   |
| Host Status Return . . . . . . . . . . . . . .        | 167   |
| Host Verification . . . . . . . . . . . . . . . . .   | 171   |
| Image Load . . . . . . . . . . . . . . . . . . . .    | 179   |
| Image Move . . . . . . . . . . . . . . . . . . .      | 181   |
| Image Save . . . . . . . . . . . . . . . . . . . .    | 182   |
| Industrial 2 of 5 Bar Codes . . . . . . . .           | . 68  |
| Initialize Flash Memory . . . . . . . . . . .         | 185   |
| Interleaved 2 of 5 Bar Code . . . . . . .             | . 19  |
| Kill Battery (Battery Discharge Mode)                 | 208   |
| Label Home . . . . . . . . . . . . . . . . . . . .    | 213   |
| Label Length . . . . . . . . . . . . . . . . . . .    | 214   |
| Label Reverse Print . . . . . . . . . . . . . .       | 215   |
| Label Shift . . . . . . . . . . . . . . . . . . . . . | 216   |
| Label Top . . . . . . . . . . . . . . . . . . . . . . | 217   |
| LOGMARS Bar Code . . . . . . . . . . . . .            | . 74  |
| Map Clear . . . . . . . . . . . . . . . . . . . . .   | 218   |
| Maximum Label Length . . . . . . . . . .              | 221   |
| Media Darkness . . . . . . . . . . . . . . . .        | 219   |
| Media Feed . . . . . . . . . . . . . . . . . . . .    | 220   |
| Media Tracking . . . . . . . . . . . . . . . . .      | 223   |
| Media Type . . . . . . . . . . . . . . . . . . . .    | 225   |
| Micro-PDF417 Bar Code . . . . . . . . . .             | . 65  |
| Mode Protection . . . . . . . . . . . . . . . . .     | 224   |
| Modify Head Cold Warning. . . . . . . . .             | 228   |
| MSI Bar Code . . . . . . . . . . . . . . . . . .      | . 76  |
| Multiple Field Origin Locations . . . . . .           | 137   |
| Network Connect . . . . . . . . . . . . . . .         | 229   |
| Network ID Number . . . . . . . . . . . . .           | 230   |
| Object Delete . . . . . . . . . . . . . . . . . .     | 177   |
| Pause and Cancel Format . . . . . . .                 | 198   |
| PDF417 Bar Code . . . . . . . . . . . . . . .         | . 30  |
| Planet Code bar code. . . . . . . . . . . . .         | . 29  |
| POSTNET Bar Code . . . . . . . . . . . . .            | 103   |

| Power On Reset . . . . . . . . . . . . . . . . . . . . . . . . . . . .         | 199   |
|--------------------------------------------------------------------------------|-------|
| Print Configuration Label . . . . . . . . . . . . . . . . . . . . . .          | 269   |
| Print Directory Label . . . . . . . . . . . . . . . . . . . . . . . . .        | 270   |
| Print Mode . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .   | 222   |
| Print Network Configuration Label . . . . . . . . . . . . . . .                | 319   |
| Print Orientation . . . . . . . . . . . . . . . . . . . . . . . . . . . . .    | 237   |
| Print Quantity . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .     | 239   |
| Print Rate . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . | 240   |
| Print Start . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .  | 244   |
| Print Width . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .    | 245   |
| Printer Sleep . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .    | 277   |
| Printing Mirror Image of Label . . . . . . . . . . . . . . . . .               | 236   |
| Programmable Pause . . . . . . . . . . . . . . . . . . . . . . . .             | 238   |
| QR Code Bar Code. . . . . . . . . . . . . . . . . . . . . . . . . . .          | . 82  |
| Read or Write RFID Format . . . . . . . . . . . . . . . . . . . .              | 286   |
| Read RFID Tag. . . . . . . . . . . . . . . . . . . . . . . . . . . . . .       | 297   |
| Recall Format . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .      | 274   |
| Recall Graphic . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .     | 275   |
| Reprint After Error . . . . . . . . . . . . . . . . . . . . . . . . . . .      | 207   |
| Reset Advanced Counter . . . . . . . . . . . . . . . . . . . . . .             | 246   |
| Reset Advanced Counters . . . . . . . . . . . . . . . . . . . . .              | 290   |
| Reset Optional Memory . . . . . . . . . . . . . . . . . . . . . .              | 186   |
| Reset Wireless Card. . . . . . . . . . . . . . . . . . . . . . . . . .         | 322   |
| Return ZebraNet Alert Configuration . . . . . . . . . . . . .                  | 170   |
| RFID Setup. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .    | 293   |
| RSS (Reduced Space Symbology) Bar Code . . . . . .                             | . 88  |
| Scalable/Bitmapped Font . . . . . . . . . . . . . . . . . . . . . .            | . 12  |
| Search for Wired Print Server during Network Boot . .                          | 307   |
| Select Date and Time Format (for Real Time Clock)                              | 209   |
| Select Encoding . . . . . . . . . . . . . . . . . . . . . . . . . . . .        | 249   |
| Sensor Select . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .    | 200   |
| Serialization Data . . . . . . . . . . . . . . . . . . . . . . . . . . . .     | 253   |
| Serialization Field (with a Standard ^FD String) . . . .                       | 250   |
| Set All Network Printers Transparent . . . . . . . . . . . .                   | 231   |
| Set Antenna Parameters . . . . . . . . . . . . . . . . . . . . . .             | 314   |
| Set Auxiliary Port . . . . . . . . . . . . . . . . . . . . . . . . . . .       | 192   |
| Set Battery Condition . . . . . . . . . . . . . . . . . . . . . . . .          | 190   |
| Set Currently Connected Printer Transparent . . . . .                          | 233   |
| Set Darkness . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .       | 248   |
| Set Date and Time (for Real-Time Clock) . . . . . . . . .                      | 262   |
| Set Dots per Millimeter . . . . . . . . . . . . . . . . . . . . . .            | 195   |
| Set Label Length . . . . . . . . . . . . . . . . . . . . . . . . . . . .       | 194   |
| Set LEAP Parameters. . . . . . . . . . . . . . . . . . . . . . . . .           | 318   |
| Set Media Sensor Calibration . . . . . . . . . . . . . . . . .                 | 187   |

| Set Media Sensors . . . . . . . . . . . . . . . . . . . .           | 260   |
|---------------------------------------------------------------------|-------|
| Set Mode and Language (for Real-Time Clock)                         | 252   |
| Set Offset (for Real-Time Clock) . . . . . . . . . .                | 255   |
| Set Primary/Secondary Device. . . . . . . . . . . .                 | 309   |
| Set Printhead Resistance . . . . . . . . . . . . . . .              | 259   |
| Set RFID Read and Write Power Levels . . . .                        | 299   |
| Set RFID Tag Password. . . . . . . . . . . . . . . . .              | 300   |
| Set Ribbon Tension . . . . . . . . . . . . . . . . . . . .          | 205   |
| Set Serial Communications . . . . . . . . . . . . .                 | 247   |
| Set SMTP . . . . . . . . . . . . . . . . . . . . . . . . . . . .    | 312   |
| Set SNMP. . . . . . . . . . . . . . . . . . . . . . . . . . . .     | 308   |
| Set Transmit Rate. . . . . . . . . . . . . . . . . . . . . .        | 321   |
| Set Units of Measurement . . . . . . . . . . . . . .                | 226   |
| Set Web Authentication Timeout Value . . . . .                      | 313   |
| Set Wireless Card Values. . . . . . . . . . . . . . . .             | 323   |
| Set Wireless Encryption Values . . . . . . . . . . .                | 315   |
| Set Wireless Password. . . . . . . . . . . . . . . . . .            | 320   |
| Set ZebraNet Alert . . . . . . . . . . . . . . . . . . . . .        | 263   |
| Set ZPL . . . . . . . . . . . . . . . . . . . . . . . . . . . . .   | 265   |
| Slew Given Number of Dot Rows . . . . . . . . .                     | 234   |
| Slew to Home Position . . . . . . . . . . . . . . . . .             | 235   |
| Specify RFID Retries for a Block . . . . . . . . . .                | 292   |
| Standard 2 of 5 Bar Code. . . . . . . . . . . . . . . .             | . 70  |
| Start Format . . . . . . . . . . . . . . . . . . . . . . . . . .    | 272   |
| Start Print . . . . . . . . . . . . . . . . . . . . . . . . . . . . | 256   |
| Suppress Backfeed . . . . . . . . . . . . . . . . . . . .           | 273   |
| Tear-off Adjust Position . . . . . . . . . . . . . . . . .          | 266   |
| TLC39 bar code . . . . . . . . . . . . . . . . . . . . . . .        | . 93  |
| Transfer Object . . . . . . . . . . . . . . . . . . . . . . .       | 267   |
| UPC/EAN Extensions . . . . . . . . . . . . . . . . . .              | . 90  |
| UPC-A Bar Code . . . . . . . . . . . . . . . . . . . . . .          | . 95  |
| UPC-E Bar Code . . . . . . . . . . . . . . . . . . . . . .          | . 37  |
| Upload Graphics . . . . . . . . . . . . . . . . . . . . . .         | 174   |
| UPS MaxiCode Bar Code . . . . . . . . . . . . . . .                 | . 60  |
| Use Font Name to Call Font . . . . . . . . . . . . .                | . 15  |
| Verify RFID Write Operation . . . . . . . . . . . . . .             | 303   |
| Write Tag . . . . . . . . . . . . . . . . . . . . . . . . . . . .   | 301   |

<!-- image -->

Notes · \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

## Proprietary Statement

<!-- image -->

This manual contains proprietary information of Zebra Technologies Corporation and its subsidiaries ('Zebra Technologies'). It is intended solely for the information and use of parties operating and maintaining the equipment described herein. Such proprietary information may not be used, reproduced, or disclosed to any other parties for any other purpose without the expressed written permission of Zebra Technologies.

## Product Improvements

Continuous improvement of products is a policy of Zebra Technologies. All specifications and designs are subject to change without notice.

## FCC Compliance Statement

This device complies with Part 15 rules. Operation is subject to the following two conditions:

1. This device may not cause harmful interference, and
2. This device must accept any interference received, including interference that may cause undesired operation.

This equipment has been tested and found to comply with the limits for Class B Digital Devices, pursuant to Part 15 of the FCC Rules. These limits are designed to provide reasonable protection against harmful interference when the equipment is operated in a residential environment. This equipment generates, uses, and can radiate radio frequency energy and, if not installed and used in accordance with the product manuals, may cause harmful interference to radio communications. However, there is no guarantee that interference will not occur in a particular installation. If this equipment does cause harmful interference to radio or television reception, the user is encouraged to do one or more of the following measures:

- Reorient or relocate the receiving antenna.
- Increase the separation between the equipment and receiver.
- Connect the equipment into an outlet on a circuit different from that to which the receiver is connected.
- Consult the dealer or an experienced radio/TV technician for help.

The user is cautioned that any changes or modifications not expressly approved by Zebra Technologies could void the user's authority to operate the equipment. To ensure compliance, this printer must be used with Shielded Communication Cables.

## Canadian DOC Compliance Statement

This Class B digital apparatus complies with Canadian ICES-003.

Cet appareil numérique de la classe B est conforme à la norme NMB-003 du Canada.

## Liability Disclaimer

Zebra Technologies takes steps to ensure that its published Engineering specifications and manuals are correct; however, errors do occur. Zebra Technologies reserves the right to correct any such errors and disclaims liability resulting therefrom.

## Limitation of Liability

In no event shall Zebra Technologies or anyone else involved in the creation, production, or delivery of the accompanying product (including hardware and software) be liable for any damages whatsoever (including, without limitation, consequential damages including loss of business profits, business interruption, or loss of business information) arising out of the use of, the results of use of, or inability to use such product, even if Zebra Technologies has been advised of the possibility of such damages. Some jurisdictions do not allow the exclusion or limitation of incidental or consequential damages, so the above limitation or exclusion may not apply to you.

## Preface

<!-- image -->

This section provides you with contact information, document structure and organization, and additional reference documents.

## Contents

| Who Should Use This Document.                   | . xvi   |
|-------------------------------------------------|---------|
| How This Document Is Organized                  | . xvi   |
| Contacts. . . . . . . . . . . . . . . . . . . . | . xvi   |
| Support . . . . . . . . . . . . . . . . . .     | . xvii  |
| Document Conventions . . . . . . . .            | . xvii  |
| Related Documents . . . . . . . . . . .         | xviii   |

<!-- image -->

## Who Should Use This Document

This document is intended for programmers who are familiar working with programming languages.

## How This Document Is Organized

This guide is set up as follows:

| Section                        | Description                                                                                                    |
|--------------------------------|----------------------------------------------------------------------------------------------------------------|
| Introduction                   | Provides a high-level overview about this guide and Zebra Programming Language (ZPL).                          |
| ZPL Commands                   | Provides an alphabetical, detailed description of each ZPL command.                                            |
| RFID Commands                  | Provides an alphabetical, detailed description of each ZPL RFID command, and some examples of how to use them. |
| Wireless Print Server Commands | Provides new and modified ZPL commands for the Wireless Print Server.                                          |

You can contact Zebra Technologies at any of the following:

Visit us at:

http://www.zebra.com

## Our Mailing Addresses:

Zebra Technologies Corporation

333 Corporate Woods Parkway

Vernon Hills, Illinois 60061.3109 U.S.A

Telephone: +1 847.634.6700

Fax: +1 847.913.8766

## Zebra Technologies Europe Limited

Zebra House The Valley Centre, Gordon Road High Wycombe Buckinghamshire HP13 6EQ, UK Telephone: +44 (0)1494 472872 Fax: +44 (0)1494 450103

## Contacts

## Support

You can contact Zebra support at:

Web Address:

www.zebra.com/SS/service\_support.htm

US Phone Number +1 847.913.2259

UK/International Phone Number +44 (0) 1494 768289

## Document Conventions

The following conventions are used throughout this document to convey certain information:

Alternate Color (online only) Cross-references contain links to other sections in this guide. If you are viewing this guide online, click the blue text to jump to its location.

Command Line Examples All command line examples appear in Courier New font. For example, type the following to get to the Post-Install scripts in the bin directory:

Ztools

Files and Directories All file names and directories appear in Courier New font. For example, the Zebra&lt;version number&gt;.tar file and the /root directory.

Important, Note, and Example

Important · Advises you of information that is essential to complete a task.

Electrostatic Discharge Caution · Warns you of the potential for electrostatic discharge.

Electric Shock Caution · Warns you of a potential electric shock situation.

Caution · Warns you of a situation where excessive heat could cause a burn.

Caution · Advises you that failure to take or avoid a specific action could result in physical harm to you.

Caution · Advises you that failure to take or avoid a specific action could result in physical harm to the hardware.

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

Caution · Advises you need to wear protective eyeware.

Note · Indicates neutral or positive information that emphasizes or supplements important points of the main text.

Example · Provides an example, often a scenario, to better clarify a section of text.

Tools · Tells you what tools you need to complete a given task.

Illustration Callouts Callouts are used when an illustration contains information that needs to be labeled and described. A table that contains the labels and descriptions follows the graphic. Figure 1 provides an example.

Figure 1 • Sample Figure with Callouts

<!-- image -->

## Related Documents

The following documents might be helpful references:

- ZPL II® Programming Guide Volume One (part number 45541L-002)
- ZPL II® Programming Guide Volume Two (part number 45542L-001).

<!-- image -->

<!-- image -->

1

