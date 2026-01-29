<!-- Source: ZPL II Programming Guide Volume 1 -->
<!-- Section: Advanced 1D Barcodes (^BA-^BK, ^BL-^BP) -->
<!-- Generated: 2025-11-02 04:52:35 -->


Important · If additional information about the EAN-8 bar code is required, go to www.aimglobal.org .

This table identifies the parameters for this format:

| Parameters                               | Details                                                                                                                                                       |
|------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------|
| o = orientation                          | Accepted Values: N = normal R = rotated 90 degrees (clockwise) I = inverted 180 degrees B = read from bottom up, 270 degrees Default Value: current ^FW value |
| h = bar code height (in dots)            | Accepted Values: 1 to 32000 Default Value: value set by ^BY                                                                                                   |
| f = print interpretation line            | Accepted Values: Y (yes) or N (no) Default Value: Y                                                                                                           |
| g = print interpretation line above code | Accepted Values: Y (yes) or N (no) Default Value: N                                                                                                           |

<!-- image -->

Example · This is an example of an EAN-8 bar code:

<!-- image -->

<!-- image -->

## ^B9

## UPC-E Bar Code

Description The ^B9 command produces a variation of the UPC symbology used for number system 0. It is a shortened version of the UPC-A bar code, where zeros are suppressed, resulting in codes that require less printing space. The 6 dot/mm,

12 dot/mm, and 24 dot/mm printheads produce the UPC and EAN symbologies at 100 percent of their size. However, an 8 dot/mm printhead produces the UPC and EAN symbologies at a magnification factor of 77 percent.

Each character in a UPC-E bar code is composed of four elements: two bars and two spaces. The ^BY command must be used to specify the width of the narrow bar.

- ^B9 supports a fixed ratio.
- Field data ( ^FD) is limited to exactly 10 characters, requiring a five-digit manufacturer's code and five-digit product code.
- When using the zero-suppressed versions of UPC, you must enter the full 10-character sequence. ZPL II calculates and prints the shortened version.

Format ,h,f,g,e

Important · If additional information about the UPC-E bar code is required, go to www.aimglobal.org .

This table identifies the parameters for this format:

| Parameters                               | Details                                                                                                                                                       |
|------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------|
| o = orientation                          | Accepted Values: N = normal R = rotated 90 degrees (clockwise) I = inverted 180 degrees B = read from bottom up, 270 degrees Default Value: current ^FW value |
| h = bar code height (in dots)            | Accepted Values: 1 to 32000 Default Value: value set by ^BY                                                                                                   |
| f = print interpretation line            | Accepted Values: Y (yes) or N (no) Default Value: Y                                                                                                           |
| g = print interpretation line above code | Accepted Values: Y (yes) or N (no) Default Value: N                                                                                                           |
| e = print check digit                    | Accepted Values: Y (yes) or N (no) Default Value: Y                                                                                                           |

<!-- image -->

Example · This is an example of a UPC-E bar code:

<!-- image -->

## Rules for Proper Product Code Numbers

- If the last three digits in the manufacturer's number are 000, 100, or 200, valid product code numbers are 00000 to 00999.
- If the last three digits in the manufacturer's number are 300, 400, 500, 600, 700, 800, or 900, valid product code numbers are 00000 to 00099.
- If the last two digits in the manufacturer's number are 10, 20, 30, 40, 50, 60, 70, 80, or 90, valid product code numbers are 00000 to 00009.
- If the manufacturer's number does not end in zero (0), valid product code numbers are 00005 to 00009.

<!-- image -->

## ^BA

## Code 93 Bar Code

Description The ^BA command creates a variable length, continuous symbology. The Code 93 bar code is used in many of the same applications as Code 39. It uses the full 128-character ASCII set. ZPL II, however, does not support ASCII control codes or escape sequences. It uses the substitute characters shown below.

| Control Code   | ZPL II Substitute   |
|----------------|---------------------|
| Ctrl $         | &                   |
| Ctrl%          | '                   |
| Ctrl /         | (                   |
| Ctrl +         | )                   |

Each character in the Code 93 bar code is composed of six elements: three bars and three spaces. Although invoked differently, the human-readable interpretation line prints as though the control code has been used.

- ^BA supports a fixed print ratio.
- Field data ( ^FD ) is limited to the width (or length, if rotated) of the label.

Format ^BAo,h,f,g,e

Important · If additional information about the Code 93 bar code is required, go to www.aimglobal.org .

This table identifies the parameters for this format:

| Parameters                    | Details                                                                                                                                                       |
|-------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------|
| o = orientation               | Accepted Values: N = normal R = rotated 90 degrees (clockwise) I = inverted 180 degrees B = read from bottom up, 270 degrees Default Value: current ^FW value |
| h = bar code height (in dots) | Accepted Values: 1 to 32000 Default Value: value set by ^BY                                                                                                   |
| f = print interpretation line | Accepted Values: Y (yes) or N (no) Default Value: Y                                                                                                           |

<!-- image -->

| Parameters                               | Details                                             |
|------------------------------------------|-----------------------------------------------------|
| g = print interpretation line above code | Accepted Values: Y (yes) or N (no) Default Value: N |
| e = print check digit                    | Accepted Values: Y (yes) or N (no) Default Value: N |

Example · This is an example of a Code 93 bar code:

<!-- image -->

Comments All control codes are used in pairs.

Code 93 is also capable of encoding the full 128-character ASCII set. For more details, see Table 4 on page 41 .

## Full ASCII Mode for Code 93

Code 93 can generate the full 128-character ASCII set using paired characters as shown in Table 4 on page 41 .

Table 4 • Code 93 Full ASCII Mode

| ASCII   | Code   | 93   |
|---------|--------|------|
| NUL     | 'U     |      |
| SOH     | &A     |      |
| STX     | B &    |      |
| ETX     | C &    |      |
| EOT     | D &    |      |
| ENQ     | E &    |      |
| ACK     | F &    |      |
| BEL     | G &    |      |
| BS      | H &    |      |
| HT      | I &    |      |
| LF      | J &    |      |
| VT      | K &    |      |
| FF      | L &    |      |
| CR      | M &    |      |
| SO      | N &    |      |
| SI      | &O     |      |
| DLE     | P &    |      |
| DC1     | Q &    |      |
| DC2     | R &    |      |
| DC3     | S &    |      |
| DC4     | T &    |      |
| NAK     | U &    |      |
| SYN     | V &    |      |
| ETB     | W &    |      |
| CAN     | X &    |      |
| EM      | Y &    |      |
| SUB     | Z &    |      |
| ESC     | 'A     |      |
| FS      | 'B     |      |
| FS      | 'C     |      |
| RS      | 'D     |      |
| US      | 'E     |      |

| ASCII   | Code   | 93   |
|---------|--------|------|
| SP      | Space  |      |
| !       | (A     |      |
| '       | (B     |      |
| #       | C (    |      |
| $       | D (    |      |
| %       | E (    |      |
| &       | F (    |      |
| '       | G (    |      |
| (       | H (    |      |
| )       | I (    |      |
| *       | J (    |      |
| ++      | ++     |      |
| '       | (L     |      |
| -       | -      |      |
| .       | .      |      |
| /       | /      |      |
| 0       | O      |      |
| 1       | 1      |      |
| 2       | 2      |      |
| 3       | 3      |      |
| 4       | 4      |      |
| 5       | 5      |      |
| 6       | 6      |      |
| 7       | 7      |      |
| 8       | 8      |      |
| 9       | 9      |      |
| :       | (Z     |      |
| ;       | 'F     |      |
| <       | 'G     |      |
| =       | 'H     |      |
| >       | 'I     |      |
| ?       | 'J     |      |

<!-- image -->

Table 5 • Code 93 Full ASCII Mode

| ASCII   | Code 93   |
|---------|-----------|
| @       | 'V        |
| A       | A         |
| B       | B         |
| C       | C         |
| D       | D         |
| E       | E         |
| F       | F         |
| G       | G         |
| H       | H         |
| I       | I         |
| J       | J         |
| K       | K         |
| L       | L         |
| M       | M         |
| N       | N         |
| O       | O         |
| P       | P         |
| Q       | Q         |
| R       | R         |
| S       | S         |
| T       | T         |
| U       | U         |
| V       | V         |
| W       | W         |
| X       | X         |
| Y       | Y         |
| Z       | Z         |
| [       | 'K        |
| \       | 'L        |
| ]       | 'M        |
| ^       | 'N        |
| _       | 'O        |

<!-- image -->

<!-- image -->

## ^BB

## CODABLOCK Bar Code

Description The ^BB command produces a two-dimensional, multirow, stacked symbology. It is ideally suited for applications that require large amounts of information.

Depending on the mode selected, the code consists of one to 44 stacked rows. Each row begins and ends with a start and stop pattern.

- CODABLOCK A supports variable print ratios.
- CODABLOCK E and F support only fixed print ratios.

Format ^BBo,h,s,c,r,m

Important · If additional information about the CODABLOCK bar code is required, go to www.aimglobal.org .

This table identifies the parameters for this format:

| Parameters                                        | Details                                                                                                                                                                                                                                                        |
|---------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| o = orientation                                   | Accepted Values: N = normal R = rotated 90 degrees (clockwise) I = inverted 180 degrees B = read from bottom up, 270 degrees Default Value: N                                                                                                                  |
| h = bar code height for individual rows (in dots) | Accepted Values: 2 to 32000 Default Value: 8 This number, multiplied by the module, equals the height of the individual row in dots.                                                                                                                           |
| s = security level                                | Accepted Values: Y (yes) or N (no) Default Value: Y Security level determines whether symbol check-sums are generated and added to the symbol. Check sums are never generated for single-row symbols. This can be turned off only if parameter m is set to A . |
| c = number of characters per row (data columns)   | Accepted Values: 2 to 62 characters This is used to encode a CODABLOCK symbol. It gives the you control over the width of the symbol.                                                                                                                          |

<!-- image -->

