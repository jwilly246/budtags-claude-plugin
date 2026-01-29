<!-- Source: ZPL II Programming Guide Volume 1 -->
<!-- Section: Basic 1D Barcodes (^B1-^B4) -->
<!-- Generated: 2025-11-02 04:52:35 -->

## ^B1

## Code 11 Bar Code

Description The ^B1 command produces the Code 11 bar code, also known as USD-8 code. In a Code 11 bar code, each character is composed of three bars and two spaces, and the character set includes 10 digits and the hyphen (-).

- ^B1 supports print ratios of 2.0:1 to 3.0:1.
- Field data ( ^FD ) is limited to the width (or length, if rotated) of the label.

Format ^B1o,e,h,f,g

Important · If additional information about the Code 11 bar code is required, go to www.aimglobal.org .

This table identifies the parameters for this format:

| Parameters                               | Details                                                                                                                                                       |
|------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------|
| o = orientation                          | Accepted Values: N = normal R = rotated 90 degrees (clockwise) I = inverted 180 degrees B = read from bottom up, 270 degrees Default Value: current ^FW value |
| e = check digit                          | Accepted Values: Y (yes) = 1 digit N (no) = 2 digits Default Value: N                                                                                         |
| h = bar code height (in dots)            | Accepted Values: 1 to 32000 Default Value: value set by ^BY                                                                                                   |
| f = print interpretation line            | Accepted Values: Y (yes) or N (no) Default Value: Y                                                                                                           |
| g = print interpretation line above code | Accepted Values: Y (yes) or N (no) Default Value: N                                                                                                           |

<!-- image -->

Example · This is an example of the Code 11 bar code:

<!-- image -->

<!-- image -->

<!-- image -->

## ^B2

## Interleaved 2 of 5 Bar Code

Description The ^B2 command produces the Interleaved 2 of 5 bar code, a high-density, self-checking, continuous, numeric symbology.

Each data character for the Interleaved 2 of 5 bar code is composed of five elements: five bars or five spaces. Of the five elements, two are wide and three are narrow. The bar code is formed by interleaving characters formed with all spaces into characters formed with all bars.

- ^B2 supports print ratios of 2.0:1 to 3.0:1.
- Field data ( ^FD ) is limited to the width (or length, if rotated) of the label.

Format ^B2o,h,f,g,e

Important · If additional information about the Code 11 bar code is required, go to www.aimglobal.org .

This table identifies the parameters for this format:

| Parameters                                 | Details                                                                                                                                                       |
|--------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------|
| o = orientation                            | Accepted Values: N = normal R = rotated 90 degrees (clockwise) I = inverted 180 degrees B = read from bottom up, 270 degrees Default Value: current ^FW value |
| h = bar code height (in dots)              | Accepted Values: 1 to 32000 Default Value: value set by ^BY                                                                                                   |
| f = print interpretation line              | Accepted Values: Y (yes) or N (no) Default Value: Y                                                                                                           |
| g = print interpretation line above code   | Accepted Values: Y (yes) or N (no) Default Value: N                                                                                                           |
| e = calculate and print Mod 10 check digit | Accepted Values: Y (yes) or N (no) Default Value: N                                                                                                           |

<!-- image -->

Example · This is an example of an Interleaved 2 of 5 bar code:

<!-- image -->

Comments The total number of digits in an Interleaved 2 of 5 bar code must be even. The printer automatically adds a leading 0 (zero) if an odd number of digits is received.

The Interleaved 2 of 5 bar code uses the Mod 10 check-digit scheme for error checking. For more information on Mod 10 check digits, see ZPL II Programming Guide Volume Two .

## ^B3

## Code 39 Bar Code

Description The Code 39 bar code is the standard for many industries, including the U.S. Department of Defense. It is one of three symbologies identified in the American National Standards Institute (ANSI) standard MH10.8M-1983. Code 39 is also known as USD-3 Code and 3 of 9 Code.

Each character in a Code 39 bar code is composed of nine elements: five bars, four spaces, and an inter-character gap. Three of the nine elements are wide; the six remaining elements are narrow.

- ^B3 supports print ratios of 2.0:1 to 3.0:1.
- Field data ( ^FD ) is limited to the width (or length, if rotated) of the label.
- Code 39 automatically generates the start and stop character (*).
- Asterisk (*) for start and stop character prints in the interpretation line, if the interpretation line is turned on.
- Code 39 is capable of encoding the full 128-character ASCII set.

Format ^B3o,e,h,f,g

Important · If additional information about the Code 39 bar code is required, go to www.aimglobal.org .

This table identifies the parameters for this format:

| Parameters                               | Details                                                                                                                                                       |
|------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------|
| o = orientation                          | Accepted Values: N = normal R = rotated 90 degrees (clockwise) I = inverted 180 degrees B = read from bottom up, 270 degrees Default Value: current ^FW value |
| e = Mod-43 check digit                   | Accepted Values: Y (yes) or N (no) Default Value: N                                                                                                           |
| h = bar code height (in dots)            | Accepted Values: 1 to 32000 Default Value: value set by ^BY                                                                                                   |
| f = print interpretation line            | Accepted Values: Y (yes) or N (no) Default Value: Y                                                                                                           |
| g = print interpretation line above code | Accepted Values: Y (yes) or N (no) Default Value: N                                                                                                           |

<!-- image -->

<!-- image -->

Example · This is an example of a Code 39 bar code:

<!-- image -->

<!-- image -->

<!-- image -->

Comments Extended ASCII is a function of the scanner, not of the bar code. Your scanner must have extended ASCII enabled for this feature to work. To enable extended ASCII in the Code 39, you must first encode +$ in your ^FD statement. To disable extended ASCII, you must encode -$ in your ^FD statement.

Example · This example encodes a carriage return with line feed into a Code 39 bar code:

<!-- image -->

<!-- image -->

## Full ASCII Mode for Code 39

Code 39 can generate the full 128-character ASCII set using paired characters as shown in these tables:

Table 1 • Code 39 Full ASCII Mode

| ASCII   | Code 39   | ASCII   | Code 39   |
|---------|-----------|---------|-----------|
| SOH     | $A        | SP      | Space     |
| STX     | $B        | !       | /A        |
| ETX     | $C        | '       | /B        |
| EOT     | $D        | #       | /C        |
| ENQ     | $E        | $       | /D        |
| ACK     | $F        | %       | /E        |
| BEL     | $G        | &       | /F        |
| BS      | $H        | '       | /G        |
| HT      | $I        | (       | /H        |
| LF      | $J        | )       | /I        |
| VT      | $K        | *       | /J        |
| FF      | $L        | ++      | /K        |
| CR      | $M        | '       | /L        |
| SO      | $N        | -       | -         |
| SI      | $O        | .       | .         |
| DLE     | $P        | /       | /O        |
| DC1     | $Q        | 0       | O         |
| DC2     | $R        | 1       | 1         |
| DC3     | $S        | 2       | 2         |
| DC4     | $T        | 3       | 3         |
| NAK     | $U        | 4       | 4         |
| SYN     | $V        | 5       | 5         |
| ETB     | $W        | 6       | 6         |
| CAN     | $X        | 7       | 7         |
| EM      | $Y        | 8       | 8         |
| SUB     | $Z        | 9       | 9         |
| ESC     | %A        | :       | /Z        |
| FS      | %B        | ;       | %F        |
| FS      | %C        | <       | %G        |
| RS      | %D        | =       | %H        |
| US      | %E        | >       | %I        |
|         |           | ?       | %J        |

| ASCII   | Code   | 39   |
|---------|--------|------|
| @       | %V     |      |
| A       | A      |      |
| B       | B      |      |
| C       | C      |      |
| D       | D      |      |
| E       | E      |      |
| F       | F      |      |
| G       | G      |      |
| H       | H      |      |
| I       | I      |      |
| J       | J      |      |
| K       | K      |      |
| L       | L      |      |
| M       | M      |      |
| N       | N      |      |
| O       | O      |      |
| P       | P      |      |
| Q       | Q      |      |
| R       | R      |      |
| S       | S      |      |
| T       | T      |      |
| U       | U      |      |
| V       | V      |      |
| W       | W      |      |
| X       | X      |      |
| Y       | Y      |      |
| Z       | Z      |      |
| [       | %K     |      |
| \       | %L     |      |
| ]       | %M     |      |
| ^       | %N     |      |
| _       | %O     |      |

| ASCII   | Code 39   |
|---------|-----------|
| '       | %W        |
| a       | +A        |
| b       | +B        |
| c       | +C        |
| d       | +D        |
| e       | +E        |
| f       | +F        |
| g       | +G        |
| h       | +H        |
| I       | +I        |
| j       | +J        |
| k       | +K        |
| l       | +L        |
| m       | +M        |
| n       | +N        |
| o       | +O        |
| p       | +P        |
| q       | +Q        |
| r       | +R        |
| s       | +S        |
| t       | +T        |
| u       | +U        |
| v       | +V        |
| w       | +W        |
| x       | +X        |
| y       | +Y        |
| z       | +Z        |
| {       | %P        |
| |       | %Q        |
| }       | %R        |
| ~       | %S        |
| DEL     | %T, %X    |

Table 2 • Code 39 Full ASCII Mode

<!-- image -->

## ^B4

## Code 49 Bar Code

Description The ^B4 command creates a multi-row, continuous, variable-length symbology capable of encoding the full 128-character ASCII set. It is ideally suited for applications requiring large amounts of data in a small space.

The code consists of two to eight rows. A row consists of a leading quiet zone, four symbol characters encoding eight code characters, a stop pattern, and a trailing quiet zone. A separator bar with a height of one module separates each row. Each symbol character encodes two characters from a set of Code 49 characters.

- ^B4 has a fixed print ratio.
- Rows can be scanned in any order.

Format ^B4o,h,f,m

Important · For additional information about the Code 11 bar code is required, see go to www.aimglobal.org .

This table identifies the parameters for this format:

| Parameters                               | Details                                                                                                                                                                                    |
|------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| o = orientation                          | Accepted Values: N = normal R = rotated 90 degrees (clockwise) I = inverted 180 degrees B = read from bottom up, 270 degrees Default Value: current ^FW value                              |
| h = height multiplier of individual rows | Accepted Values: 1 to height of label Default Value: value set by ^BY This number multiplied by the module equals the height of the individual rows in dots. 1 is not a recommended value. |

