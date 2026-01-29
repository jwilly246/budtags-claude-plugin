<!-- Source: ZPL II Programming Guide Volume 1 -->
<!-- Section: Configuration Commands (^C*, ~C*) -->
<!-- Generated: 2025-11-02 04:52:35 -->


<!-- image -->

<!-- image -->

Comments The EAN-13 bar code uses the Mod 10 check-digit scheme for error checking. For more information on Mod 10, see ZPL II Programming Guide Volume Two .

<!-- image -->

## ^BF

## Micro-PDF417 Bar Code

Description The ^BF command creates a two-dimensional, multi-row, continuous, stacked symbology identical to PDF417, except it replaces the 17-module-wide start and stop patterns and left/right row indicators with a unique set of 10-module-wide row address patterns. These reduce overall symbol width and allow linear scanning at row heights as low as 2X.

Micro-PDF417 is designed for applications with a need for improved area efficiency but without the requirement for PDF417's maximum data capacity. It can be printed only in specific combinations of rows and columns up to a maximum of four data columns by 44 rows.

Field data ( ^FD ) and field hexadecimal ( ^FH ) are limited to:

- 250 7-bit characters
- 150 8-bit characters
- 366 4-bit numeric characters

Format ^BFo,h,m

This table identifies the parameters for this format:

| Parameters                    | Details                                                                                                                                                       |
|-------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------|
| o = orientation               | Accepted Values: N = normal R = rotated 90 degrees (clockwise) I = inverted 180 degrees B = read from bottom up, 270 degrees Default Value: current ^FW value |
| h = bar code height (in dots) | Accepted Values: 1 to 9999 Default Value: value set by ^BY or 10 (if no ^BY value exists).                                                                    |
| m = mode                      | Accepted Values: 0 to 33 (see Micro-PDF417 Mode on page 67) Default Value: 0 (see Micro-PDF417 Mode on page 67)                                               |

<!-- image -->

<!-- image -->

Example · This is an example of a Micro-PDF417 bar code:

<!-- image -->

## To encode data into a Micro-PDF417 Bar Code, complete these steps:

1. Determine the type of data to be encoded (for example, ASCII characters, numbers, 8-bit data, or a combination).
2. Determine the maximum amount of data to be encoded within the bar code (for example, number of ASCII characters, quantity of numbers, or quantity of 8-bit data characters).
3. Determine the percentage of check digits that are used within the bar code. The higher the percentage of check digits that are used, the more resistant the bar code is to damage however, the size of the bar code increases.
4. Use the chart Micro-PDF417 Mode on page 67 with the information gathered from the questions above to select the mode of the bar code.

|   Mode (M) |   Number of Data Columns |   Number of Data Rows |   %of Cws for EC |   Max Alpha Characters |   Max Digits |
|------------|--------------------------|-----------------------|------------------|------------------------|--------------|
|          0 |                        1 |                    11 |               64 |                      6 |            8 |
|          1 |                        1 |                    14 |               50 |                     12 |           17 |
|          2 |                        1 |                    17 |               41 |                     18 |           26 |
|          3 |                        1 |                    20 |               40 |                     22 |           32 |
|          4 |                        1 |                    24 |               33 |                     30 |           44 |
|          5 |                        1 |                    28 |               29 |                     38 |           55 |
|          6 |                        2 |                     8 |               50 |                     14 |           20 |
|          7 |                        2 |                    11 |               41 |                     24 |           35 |
|          8 |                        2 |                    14 |               32 |                     36 |           52 |
|          9 |                        2 |                    17 |               29 |                     46 |           67 |
|         10 |                        2 |                    20 |               28 |                     56 |           82 |
|         11 |                        2 |                    23 |               28 |                     64 |           93 |
|         12 |                        2 |                    26 |               29 |                     72 |          105 |
|         13 |                        3 |                     6 |               67 |                     10 |           14 |
|         14 |                        3 |                     8 |               58 |                     18 |           26 |
|         15 |                        3 |                    10 |               53 |                     26 |           38 |
|         16 |                        3 |                    12 |               50 |                     34 |           49 |
|         17 |                        3 |                    15 |               47 |                     46 |           67 |
|         18 |                        3 |                    20 |               43 |                     66 |           96 |
|         19 |                        3 |                    26 |               41 |                     90 |          132 |
|         20 |                        3 |                    32 |               40 |                    114 |          167 |
|         21 |                        3 |                    38 |               39 |                    138 |          202 |
|         22 |                        3 |                    44 |               38 |                    162 |          237 |
|         23 |                        4 |                     6 |               50 |                     22 |           32 |
|         24 |                        4 |                     8 |               44 |                     34 |           49 |
|         25 |                        4 |                    10 |               40 |                     46 |           67 |
|         26 |                        4 |                    12 |               38 |                     58 |           85 |
|         27 |                        4 |                    15 |               35 |                     76 |          111 |
|         28 |                        4 |                    20 |               33 |                    106 |          155 |
|         29 |                        4 |                    26 |               31 |                    142 |          208 |
|         30 |                        4 |                    32 |               30 |                    178 |          261 |
|         31 |                        4 |                    38 |               29 |                    214 |          313 |
|         32 |                        4 |                    44 |               28 |                    250 |          366 |
|         33 |                        4 |                     4 |               50 |                     14 |           20 |

Table 9 • Micro-PDF417 Mode

<!-- image -->

<!-- image -->

<!-- image -->

## ^BI

## Industrial 2 of 5 Bar Codes

Description The ^BI command is a discrete, self-checking, continuous numeric symbology. The Industrial 2 of 5 bar code has been in use the longest of the 2 of 5 family of bar codes. Of that family, the Standard 2 of 5 ( ^BJ ) and Interleaved 2 of 5 ( ^B2 ) bar codes are also available in ZPL II.

With Industrial 2 of 5, all of the information is contained in the bars. Two bar widths are employed in this code, the wide bar measuring three times the width of the narrow bar.

- ^BI supports a print ratio of 2.0:1 to 3.0:1.
- Field data ( ^FD ) is limited to the width (or length, if rotated) of the label.

Format ^BIo,h,f,g

Important · If additional information about the Industrial 2 of 5 bar code, go to www.aimglobal.org .

This table identifies the parameters for this format:

| Parameters                               | Details                                                                                                                                                       |
|------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------|
| o = orientation                          | Accepted Values: N = normal R = rotated 90 degrees (clockwise) I = inverted 180 degrees B = read from bottom up, 270 degrees Default Value: current ^FW value |
| h = bar code height (in dots)            | Accepted Values: 1 to 32000 Default Value: value set by ^BY                                                                                                   |
| f = print interpretation line            | Accepted Values: Y (yes) or N (no) Default Value: Y                                                                                                           |
| g = print interpretation line above code | Accepted Values: Y (yes) or N (no) Default Value: N                                                                                                           |

<!-- image -->

Example · This is an example of an Industrial 2 of 5 bar code:

<!-- image -->

<!-- image -->

<!-- image -->

^BJ

## Standard 2 of 5 Bar Code

Description The ^BJ command is a discrete, self-checking, continuous numeric symbology.

With Standard 2 of 5, all of the information is contained in the bars. Two bar widths are employed in this code, the wide bar measuring three times the width of the narrow bar.

- ^BJ supports a print ratio of 2.0:1 to 3.0:1.
- Field data ( ^FD ) is limited to the width (or length, if rotated) of the label.

Format ^BJo,h,f,g

Important · If additional information about the Standard 2 of 5 bar code is required, go to www.aimglobal.org .

This table identifies the parameters for this format:

| Parameters                               | Details                                                                                                                                                       |
|------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------|
| o = orientation                          | Accepted Values: N = normal R = rotated 90 degrees (clockwise) I = inverted 180 degrees B = read from bottom up, 270 degrees Default Value: current ^FW value |
| h = bar code height (in dots)            | Accepted Values: 1 to 32000 Default Value: value set by ^BY                                                                                                   |
| f = print interpretation line            | Accepted Values: Y (yes) or N (no) Default Value: Y                                                                                                           |
| g = print interpretation line above code | Accepted Values: Y (yes) or N (no) Default Value: N                                                                                                           |

<!-- image -->

Example · This is an example of a Standard 2 of 5 bar code:

<!-- image -->

<!-- image -->

<!-- image -->

^BK

## ANSI Codabar Bar Code

Description The ANSI Codabar bar code is used in a variety of information processing applications such as libraries, the medical industry, and overnight package delivery companies. This bar code is also known as USD-4 code, NW-7, and 2 of 7 code. It was originally developed for retail price labeling.

Each character in this code is composed of seven elements: four bars and three spaces. Codabar bar codes use two character sets, numeric and control (start and stop) characters.

- ^BK supports a print ratio of 2.0:1 to 3.0:1.
- Field data ( ^FD ) is limited to the width (or length, if rotated) of the label.

Format ^BKo,e,h,f,g,k,l

Important · If additional information about the ANSI Codabar bar code is required, go to www.aimglobal.org .

This table identifies the parameters for this format:

| Parameters                               | Details                                                                                                                                                       |
|------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------|
| o = orientation                          | Accepted Values: N = normal R = rotated 90 degrees (clockwise) I = inverted 180 degrees B = read from bottom up, 270 degrees Default Value: current ^FW value |
| e = check digit                          | Fixed Value: N                                                                                                                                                |
| h = bar code height (in dots)            | Accepted Values: 1 to 32000 Default Value: value set by ^BY                                                                                                   |
| f = print interpretation line            | Accepted Values: Y (yes) or N (no) Default Value: Y                                                                                                           |
| g = print interpretation line above code | Accepted Values: Y (yes) or N (no) Default Value: N                                                                                                           |
| k = designates a start character         | Accepted Values: A,B , C , D Default Value: A                                                                                                                 |
| l = designates stop character            | Accepted Values: A,B , C , D Default Value: A                                                                                                                 |

<!-- image -->

Example · This is an example of an ANSI Codabar bar code:

<!-- image -->

<!-- image -->

<!-- image -->

## ^BL

## LOGMARS Bar Code

Description The ^BL command is a special application of Code 39 used by the Department of Defense. LOGMARS is an acronym for Logistics Applications of Automated Marking and Reading Symbols.

- ^BL supports a print ratio of 2.0:1 to 3.0:1.
- Field data ( ^FD ) is limited to the width (or length, if rotated) of the label. Lowercase letters in the ^FD string are converted to the supported uppercase LOGMARS characters.

Format ^BLo,h,g

Important · If additional information about the LOGMARS bar code is required, go to www.aimglobal.org .

This table identifies the parameters for this format:

| Parameters                               | Details                                                                                                                                                       |
|------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------|
| o = orientation                          | Accepted Values: N = normal R = rotated 90 degrees (clockwise) I = inverted 180 degrees B = read from bottom up, 270 degrees Default Value: current ^FW value |
| h = bar code height (in dots)            | Accepted Values: 1 to 32000 Default Value: value set by ^BY                                                                                                   |
| g = print interpretation line above code | Accepted Values: Y (yes) or N (no) Default Value: N                                                                                                           |

<!-- image -->

Example · This is an example of a LOGMARS bar code:

<!-- image -->

<!-- image -->

Comments The LOGMARS bar code produces a mandatory check digit using Mod 43 calculations. For further information on the Mod 43 check digit, see ZPL II Programming Guide Volume Two .

<!-- image -->

<!-- image -->

^BM

## MSI Bar Code

Description The ^BM command is a pulse-width modulated, continuous, non-self- checking symbology. It is a variant of the Plessey bar code ( ^BP ).

Each character in the MSI bar code is composed of eight elements: four bars and four adjacent spaces.

- ^BM supports a print ratio of 2.0:1 to 3.0:1.
- For the bar code to be valid, field data ( ^FD ) is limited to 1 to 14 digits when parameter e is B , C , or D . ^FD is limited to 1 to 13 digits when parameter e is A , plus a quiet zone.

Format ^BMo,e,h,f,g,e2

Important · If additional information about the MSI bar code is required, go to www.aimglobal.org .

This table identifies the parameters for this format:

| Parameters                    | Details                                                                                                                                                       |
|-------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------|
| o = orientation               | Accepted Values: N = normal R = rotated 90 degrees (clockwise) I = inverted 180 degrees B = read from bottom up, 270 degrees Default Value: current ^FW value |
