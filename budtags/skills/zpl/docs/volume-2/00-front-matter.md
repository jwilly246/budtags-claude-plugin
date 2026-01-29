<!-- Source: ZPL II Programming Guide Volume 2 -->
<!-- Section: Front Matter, TOC, Document Conventions -->
<!-- Generated: 2025-11-02 04:52:35 -->

<!-- image -->

## ZPL II ®

## Programming Guide Volume 2

<!-- image -->

© 2005 ZIH Corp.

The copyrights in this manual and the label print engine described therein are owned by Zebra Technologies Corporation. Unauthorized reproduction of this manual or the software in the label print engine may result in imprisonment of up to one year and fines of up to $10,000 (17 U.S.C.506). Copyright violators may be subject to civil liability.

This product may contain ZPL ® , ZPL II ® , and ZebraLink™ programs; Element Energy Equalizer ® Circuit; E3 ® ; and AGFA fonts. Software © ZIH Corp. All rights reserved worldwide.

ZebraLink and all product names and numbers are trademarks, and Zebra, the Zebra logo, ZPL, ZPL II, Element Energy Equalizer Circuit, and E3 Circuit are registered trademarks of ZIH Corp. All rights reserved worldwide.

CG Triumvirate is a trademark of AGFA Monotype Corporation. All rights reserved worldwide. CG Triumvirate™ font © AGFA Monotype Corporation. Intellifont ® portion © AGFA Monotype Corporation. All rights reserved worldwide. UFST is a registered trademark of AGFA Monotype Corporation. All rights reserved worldwide.

All other brand names, product names, or trademarks belong to their respective holders.

## Part Number: 45542L-002 Rev. A

## Contents

| About This Document . . . . . . . . . . . . . . . . . . . . . . . . . . . .                | . 1   |
|--------------------------------------------------------------------------------------------|-------|
| Who Should Use This Document . . . . . . . . . . . . . . . . . . . . . .                   | . 2   |
| How This Document Is Organized . . . . . . . . . . . . . . . . . . . . .                   | . 2   |
| Contacts . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . | . 3   |
| Support . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .      | . 3   |
| Document Conventions. . . . . . . . . . . . . . . . . . . . . . . . . . . . . .            | . 4   |
| 1 • ZPL II Basics . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .          | . 5   |
| How ZPL II Differs from ZPL. . . . . . . . . . . . . . . . . . . . . . . . . .             | . 6   |
| ZPL II Overview . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .      | . 7   |
| Format and Control Commands . . . . . . . . . . . . . . . . . . . . . . .                  | . 8   |
| Format Commands. . . . . . . . . . . . . . . . . . . . . . . . . . . . . .                 | . 8   |
| Control Commands. . . . . . . . . . . . . . . . . . . . . . . . . . . . . .                | . 9   |
| Command Parameters and Default Values. . . . . . . . . . . . . . .                         | 10    |
| Example of a Basic Label . . . . . . . . . . . . . . . . . . . . . . . . . . . .           | .11   |
| Shortcuts for Writing ZPL II Scripts. . . . . . . . . . . . . . . . . . . . .              | 13    |
| Writing Code on One Line and Using Parameter Defaults                                      | 13    |
| Eliminating Unnecessary Field Separators. . . . . . . . . . . .                            | 14    |
| Font Shortcuts . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .           | 15    |
| Using Device and Object Names . . . . . . . . . . . . . . . . . . . . . .                  | 16    |
| Device Names . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .             | 16    |
| Object Names and Extensions . . . . . . . . . . . . . . . . . . . . .                      | 16    |
| Name Parameter . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .               | 17    |
| 2 • Programming Exercises . . . . . . . . . . . . . . . . . . . . . . .                    | 19    |
| Introduction to Exercises. . . . . . . . . . . . . . . . . . . . . . . . . . . . .         | 20    |
| Computer and Software Requirements. . . . . . . . . . . . . . .                            | 20    |
| Performing the Exercises . . . . . . . . . . . . . . . . . . . . . . . . .                 | 20    |

<!-- image -->

| Exercise 1: Saving Label Formats as Graphic Images. . . . . . . . . . . . . . . . . . . . . . . .                                                                                                           |   21 |
|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------|
| Exercise 2: Downloading and Printing Graphic Images . . . . . . . . . . . . . . . . . . . . . . .                                                                                                           |   23 |
| Exercise 3: Setting Print Rate, Printing Quantities of Labels in an Inverted Orientation, and Suppressing Backfeed. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . |   26 |
| Exercise 4: Slew Command, Form Feed, and Printing Entire Formats in Reverse . .                                                                                                                             |   29 |
| Exercise 5: Using Serialized Fields. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .                                                                                            |   33 |
| Exercise 6: Stored Formats. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .                                                                                         |   35 |
| Advanced Techniques . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .                                                                                                       |   39 |
| Special Effects for Print Fields . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .                                                                                        |   41 |
| Serialized Data . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .                                                                                 |   41 |
| Variable Data . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .                                                                                 |   41 |
| Stored Formats . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .                                                                                  |   42 |
| Initialize/Erase Stored Formats. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .                                                                                                |   42 |
| Download Format Command . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .                                                                                                     |   42 |
| Field Number Command. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .                                                                                                 |   42 |
| Field Allocate . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .                                                                                      |   43 |
| Recall Stored Format Command . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .                                                                                                      |   43 |
| Control Commands. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .                                                                                       |   44 |
| Test and Setup Commands . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .                                                                                                   |   44 |
| Calibration and Media Feed Commands . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .                                                                                                           |   45 |
| Cancel/Clear Commands . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .                                                                                                 |   45 |
| Printer Control Commands. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .                                                                                                 |   45 |
| Set Dots/Millimeter . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .                                                                                         |   47 |
| Host Status Commands . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .                                                                                                |   47 |
| Changing Delimiters and Command Prefixes. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .                                                                                                       |   49 |
| Communication Diagnostics Commands . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .                                                                                                      |   49 |
| Networking . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .                                                                                |   50 |
| Assigning Network IDs/Chaining Multiple Printers . . . . . . . . . . . . . . . . . . . . . . . .                                                                                                            |   50 |
| Connecting Printers into the Network . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .                                                                                                    |   50 |
| Graphic Commands . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .                                                                                        |   51 |
| Boxes and Lines . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .                                                                                         |   51 |
| Working with Hex Graphic Images . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .                                                                                                     |   51 |
| Alternative Data Compression Scheme for ~DG and ~DB Commands . . . . . . . .                                                                                                                                |   52 |
| Recalling a Hexadecimal Graphic Image . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .                                                                                                         |   53 |
| Image Move . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .                                                                                        |   53 |
| Reducing Download Time of Graphic Images . . . . . . . . . . . . . . . . . . . . . . . . . . .                                                                                                              |   53 |
| Transferring Object Between Storage Devices. . . . . . . . . . . . . . . . . . . . . . . . . . .                                                                                                            |   54 |
| Deleting Graphics from Memory. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .                                                                                                    |   55 |
| Defining and Using the AUTOEXEC.ZPL Function . . . . . . . . . . . . . . . . . . . . . . .                                                                                                                  |   55 |
| Memory, Flash Cards, and Font Cards. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .                                                                                                  |   56 |

| 4 • Fonts and Bar Codes . . . . . . . . . . .          | . 59   |
|--------------------------------------------------------|--------|
| Standard Printer Fonts . . . . . . . . . . . . .       | . 60   |
| Proportional and Fixed Spacing . . . . . .             | . 61   |
| Scalable Versus Bitmapped Fonts . . . .                | . 62   |
| Scalable Fonts . . . . . . . . . . . . . . . .         | . 62   |
| Bitmapped Fonts. . . . . . . . . . . . . . .           | . 62   |
| Font Matrices . . . . . . . . . . . . . . . . . . . .  | . 64   |
| 6 dot/mm printhead. . . . . . . . . . . . .            | . 64   |
| 8 dot/mm (203 dpi) printhead . . . . .                 | . 64   |
| 12 dot/mm (300 dpi) printhead . . . .                  | . 65   |
| 24 dot/mm (600 dpi) printhead . . . .                  | . 65   |
| Bar Codes. . . . . . . . . . . . . . . . . . . . . . . | . 66   |
| Basic Format for Bar Codes . . . . . .                 | . 67   |
| Bar Code Field Instructions . . . . . .                | . 67   |
| Bar Code Command Groups . . . . .                      | . 69   |
| 5 • Printer Configuration Using ZPL II                 | . 71   |
| Printer Configuration Commands . . . . .               | . 72   |
| Print Mode . . . . . . . . . . . . . . . . . . .       | . 73   |
| Media Tracking . . . . . . . . . . . . . . . .         | . 73   |
| Media Type . . . . . . . . . . . . . . . . . . .       | . 73   |
| Media Darkness . . . . . . . . . . . . . . .           | . 74   |
| Label Top Position . . . . . . . . . . . . .           | . 74   |
| Set Media Sensors . . . . . . . . . . . . .            | . 74   |
| Mode Protection . . . . . . . . . . . . . . .          | . 75   |
| Reprint After Error. . . . . . . . . . . . . .         | . 75   |
| Configuration Update . . . . . . . . . . .             | . 75   |
| Set ZPL. . . . . . . . . . . . . . . . . . . . . .     | . 75   |
| Setting Up Customized Label Formats .                  | . 76   |
| 6 • XML-Super Host Status . . . . . . .                | . 77   |
| Introduction to XML. . . . . . . . . . . . . . . .     | . 78   |
| XML Attributes . . . . . . . . . . . . . . . . . . .   | . 78   |
| Printer Definitions . . . . . . . . . . . . . .        | . 79   |
| Saved Settings . . . . . . . . . . . . . . . .         | . 80   |
| Format Settings . . . . . . . . . . . . . . .          | . 88   |
| Status Information. . . . . . . . . . . . . .          | . 90   |
| 7 • Real Time Clock . . . . . . . . . . . . . . .      | . 93   |
| 8 • Mod 10 and Mod 43 Check Digits .                   | . 95   |
| Mod 43 Check Digit. . . . . . . . . . . . . . . .      | .      |
|                                                        | 97     |

| 9 • Error Detection Protocol . . . . . . . . . . . . . . . . . . . .               | . 99   |
|------------------------------------------------------------------------------------|--------|
| Introduction . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . | . 100  |
| What is a Protocol?. . . . . . . . . . . . . . . . . . . . . . . . . .             | . 100  |
| How Protocols Work . . . . . . . . . . . . . . . . . . . . . . . . .               | . 100  |
| Request Packet Formats from the Host Computer. . . . .                             | . 101  |
| Header Block Fields . . . . . . . . . . . . . . . . . . . . . . . . .              | . 101  |
| Data Block Fields . . . . . . . . . . . . . . . . . . . . . . . . . . .            | . 102  |
| Response From the Zebra Printer . . . . . . . . . . . . . . . . .                  | . 103  |
| Zebra Packet Response . . . . . . . . . . . . . . . . . . . . . .                  | . 103  |
| Header Block Fields . . . . . . . . . . . . . . . . . . . . . . . . .              | . 103  |
| Data Block Fields . . . . . . . . . . . . . . . . . . . . . . . . . . .            | . 104  |
| Disguising Control Code Characters . . . . . . . . . . . .                         | . 105  |
| Error Detection Protocol Application. . . . . . . . . . . . .                      | . 106  |
| Error Conditions and System Faults . . . . . . . . . . . . .                       | . 106  |
| How the Zebra Printer Processes a Request Packet                                   | . 107  |
| How the Zebra Printer Responds to Host Status . . .                                | . 108  |
| 10 • ZB64 Encoding and Compression . . . . . . . . . . .                           | 109    |
| Introduction to B64 and Z64 . . . . . . . . . . . . . . . . . . . . . .            | . .110 |
| B64 and Z64 Encoding . . . . . . . . . . . . . . . . . . . . . . . . . .           | . .112 |
| A • Code Page 850 Chart . . . . . . . . . . . . . . . . . . . . . .                | 115    |
| B • ASCII Code Chart . . . . . . . . . . . . . . . . . . . . . . . . .             | 119    |
| C • AIM Contact Information . . . . . . . . . . . . . . . . . . .                  | 121    |
| Proprietary Statement . . . . . . . . . . . . . . . . . . . . . . . . .            | 123    |

## About This Document

<!-- image -->

This section provides you with contact information, document structure and organization, and typographical conventions used in this document.

## Contents

| Who Should Use This Document.                   |   2 |
|-------------------------------------------------|-----|
| How This Document Is Organized                  |   2 |
| Contacts. . . . . . . . . . . . . . . . . . . . |   3 |
| Support . . . . . . . . . . . . . . . . . .     |   3 |
| Document Conventions . . . . . . . .            |   4 |

<!-- image -->

## Who Should Use This Document

This Programming Guide is intended for use by any person who needs to perform routine maintenance, upgrade, or troubleshoot problems with the printer.

## How This Document Is Organized

The Programming Guide is set up as follows:

| Section                                       | Description                                                                                                                                                                                            |
|-----------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| About This Document on page 1                 | This section provides you with contact information, document structure and organization, and typographical conventions used in this document.                                                          |
| ZPL II Basics on page 5                       | This section provides basic information about Zebra Programming Language II (ZPL II).                                                                                                                  |
| Programming Exercises on page 19              | This section provides exercises that show you how to use ZPL II.                                                                                                                                       |
| Advanced Techniques on page 39                | This section presents information and commands for using advanced techniques, such as special effects, serialized data fields, control commands, program delimiters, communications, and memory cards. |
| Fonts and Bar Codes on page 59                | This section provides information about different fonts (type faces) and bar codes that can be used with the printer.                                                                                  |
| Printer Configuration Using ZPL II on page 71 | This section discusses how to use the ZPL II printer configuration commands.                                                                                                                           |
| XML-Super Host Status on page 77              | This section provides information about XML-Super Host Status.                                                                                                                                         |
| Real Time Clock on page 93                    | This section discusses the ZPL II commands related to the Real- Time Clock (RTC).                                                                                                                      |
| Mod 10 and Mod 43 Check Digits on page 95     | This section provides information about Mod 10 and Mod 43 check digits.                                                                                                                                |
| Error Detection Protocol on page 99           | This section explains the Zebra protocol that has been supplanted in TCP/IP based applications because of the error detection compatibility inherent in the TCP/IP protocol.                           |
| ZB64 Encoding and Compression on page 109     | This section describes the Base 64 MIME (ZB64) encoding and compression. This is the same type of MIME encoding that is used in e-mail.                                                                |
| Code Page 850 Chart on page 115               | This section shows the Code Page 850 character set used by Zebra printers.                                                                                                                             |
| ASCII Code Chart on page 119                  | This section shows the American Standard Code for Information Interchange (ASCII) code used by Zebra printers.                                                                                         |
| AIM Contact Information on page 121           | This section provides contact information for AIM (Association for Automatic Identification and Mobility).                                                                                             |

## Contacts

## Support

<!-- image -->

You can contact Zebra Technologies Corporation at the following:

Visit us at:

www.zebra.com

## Our Mailing Addresses:

Zebra Technologies Corporation

333 Corporate Woods Parkway

Vernon Hills, Illinois 60061.3109 U.S.A

Telephone: +1 847.634.6700

Fax: +1 847.913.8766

## Zebra Technologies Europe Limited

Zebra House

The Valley Centre, Gordon Road High Wycombe

Buckinghamshire HP13 6EQ, UK

Telephone: +44 (0)1494 472872

Fax: +44 (0)1494 450103

You can contact Zebra support at:

Web Address:

www.zebra.com/SS/service\_support.htm

US Phone Number +1 847.913.2259

UK/International Phone Number +44 (0) 1494 768289

Note • The web address is case-sensitive.

<!-- image -->

## Document Conventions

The following conventions are used throughout this document to convey certain information.

Alternate Color (online only) Cross-references contain hot links to other sections in this guide. If you are viewing this guide online in .pdf format, you can click the cross-reference (blue text) to jump directly to its location.

LCD Display Examples Text from a printer's Liquid Crystal Display (LCD) appears in Bubbledot ICG font.

Command Line Examples Command line examples appear in Courier New font. For example, type ZTools to get to the Post-Install scripts in the bin directory.

Files and Directories File names and directories appear in Courier New font. For example, the Zebra&lt;version number&gt;.tar file and the /root directory.

## Icons Used

Caution · Warns you of the potential for electrostatic discharge.

Caution · Warns you of a potential electric shock situation.

Caution · Warns you of a situation where excessive heat could cause a burn.

Caution · Advises you that failure to take or avoid a specific action could result in physical harm to you.

Caution · (No icon) Advises you that failure to take or avoid a specific action could result in physical harm to the hardware.

Important · Advises you of information that is essential to complete a task.

Note · Indicates neutral or positive information that emphasizes or supplements important points of the main text.

Example · Provides an example, often a scenario, to better clarify a section of text.

Tools · Tells you what tools you need to complete a given task.

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

1

