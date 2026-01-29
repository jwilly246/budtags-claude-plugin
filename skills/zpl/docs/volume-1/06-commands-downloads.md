<!-- Source: ZPL II Programming Guide Volume 1 -->
<!-- Section: Download Commands (~D*) -->
<!-- Generated: 2025-11-02 04:52:35 -->

| e = check digit selection     | Accepted Values: A = no check digits B = 1 Mod 10 C = 2 Mod 10 D = 1 Mod 11 and 1 Mod 10 Default Value: B                                                     |
| h = bar code height (in dots) | Accepted Values: 1 to 32000 Default Value: value set by ^BY                                                                                                   |
| f = print interpretation line | Accepted Values: Y (yes) or N (no) Default Value: Y                                                                                                           |

<!-- image -->

| Parameters   | Parameters                                         | Details                                             |
|--------------|----------------------------------------------------|-----------------------------------------------------|
| g            | = print interpretation line above code             | Accepted Values: Y (yes) or N (no) Default Value: N |
| e2           | = inserts check digit into the interpretation line | Accepted Values: Y (yes) or N (no) Default Value: N |

- Example · This is an example of a MSI bar code:

<!-- image -->

<!-- image -->

<!-- image -->

^BO

## Aztec Bar Code Parameters

Description The ^BO command creates a two-dimensional matrix symbology made up of square modules arranged around a bulls-eye pattern at the center.

<!-- image -->

Note · The Aztec bar code works with firmware v60.13.0.11A and higher.

Format ^BOa,b,c,d,e,f,g

This table identifies the parameters for this format:

| Parameters                                         | Details                                                                                                                                                                                                                                 |
|----------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| a = orientation                                    | Accepted Values: N = normal R = rotated I = inverted 180 degrees B = read from bottom up, 270 degrees Default Value: current ^FW value                                                                                                  |
| b = magnification factor                           | Accepted Values: 1 to 10 Default Value: 1 on 150 dpi printers 2 on 200 dpi printers 3 on 300 dpi printers 6 on 600 dpi printers                                                                                                         |
| c = extended channel interpretation code indicator | Accepted Values: Y = if data contains ECICs N = if data does not contain ECICs. Default Value: N                                                                                                                                        |
| d = error control and symbol size/type indicator   | Accepted Values: 0 = default error correction level 01 to 99 = error correction percentage (minimum) 101 to 104 = 1 to 4-layer compact symbol 201 to 232 = 1 to 32-layer full-range symbol 300 = a simple Aztec 'Rune' Default Value: 0 |
| e = menu symbol indicator                          | Accepted Values: Y = if this symbol is to be a menu (bar code reader initialization) symbol N = if it is not a menu symbol Default Value: N                                                                                             |

<!-- image -->

| Parameters                                  | Details                                                                      |
|---------------------------------------------|------------------------------------------------------------------------------|
| f = number of symbols for structured append | Accepted Values: 1 through 26 Default Value: 1                               |
| g = optional ID field for structured append | The ID field is a text string with 24-character maximum Default Value: no ID |

## Example · This is an example of the ^B0 command:

## ZPL II CODE

```
^XA ^B0R,7,N,0,N,1,0 ^FD 7. This is testing label 7^FS ^XZ
```

<!-- image -->

<!-- image -->

<!-- image -->

^BP

## Plessey Bar Code

Description The ^BP command is a pulse-width modulated, continuous, non-self- checking symbology.

Each character in the Plessey bar code is composed of eight elements: four bars and four adjacent spaces.

- ^BP supports a print ratio of 2.0:1 to 3.0:1.
- Field data ( ^FD ) is limited to the width (or length, if rotated) of the label.

Format ^BPo,e,h,f,g

Important · If additional information about the Plessey bar code is required, go to www.aimglobal.org .

This table identifies the parameters for this format:

| Parameters                               | Details                                                                                                                                                       |
|------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------|
| o = orientation                          | Accepted Values: N = normal R = rotated 90 degrees (clockwise) I = inverted 180 degrees B = read from bottom up, 270 degrees Default Value: current ^FW value |
| e = print check digit                    | Accepted Values: Y (yes) or N (no) Default Value: N                                                                                                           |
| h = bar code height (in dots)            | Accepted Values: Y (yes) or N (no) Default Value: N                                                                                                           |
| f = print interpretation line            | Accepted Values: Y (yes) or N (no) Default Value: Y                                                                                                           |
| g = print interpretation line above code | Accepted Values: Y (yes) or N (no) Default Value: N                                                                                                           |

<!-- image -->

Example · This is an example of a Plessey bar code:

<!-- image -->

<!-- image -->

## QR Code Bar Code

Description The ^BQ command produces a matrix symbology consisting of an array of nominally square modules arranged in an overall square pattern. A unique pattern at three of the symbol's four corners assists in determining bar code size, position, and inclination.

A wide range of symbol sizes is possible, along with four levels of error correction. Userspecified module dimensions provide a wide variety of symbol production techniques.

QR Code Model 1 is the original specification, while QR Code Model 2 is an enhanced form of the symbology. Model 2 provides additional features and can be automatically differentiated from Model 1.

Model 2 is the recommended model and should normally be used.

This bar code is printed using field data specified in a subsequent ^FD string.

Encodable character sets include numeric data, alphanumeric data, 8-bit byte data, and Kanji characters.

Format ^BQa,b,c,d,e

Important · If additional information about the QR Code bar code is required, go to www.aimglobal.org .

This table identifies the parameters for this format:

| Parameters               | Details                                                                                                                         |
|--------------------------|---------------------------------------------------------------------------------------------------------------------------------|
| a = field position       | Fixed Value: normal ( ^FW has no effect on rotation)                                                                            |
| b = model                | Accepted Values: 1 (original) and 2 (enhanced - recommended) Default Value: 2                                                   |
| c = magnification factor | Accepted Values: 1 to 10 Default Value: 1 on 150 dpi printers 2 on 200 dpi printers 3 on 300 dpi printers 6 on 600 dpi printers |

| Parameters   | Details                                                                                                                                                               |
|--------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| d = H,Q,M,L  | Accepted Values: H = ultra-high reliability level Q = high reliability level M = standard level L = high density level Default Value: Q = if empty M = invalid values |
| e = N,A,B.K  | Accepted Values: 1 - 7 Default Value: 7                                                                                                                               |

## Example · This is an example of a QR Code bar code:

<!-- image -->

<!-- image -->

On the pages that follow are specific commands for formatting the ^BQ command with the ^FD statements that contain the information to be coded.

## Considerations for ^FD When Using the QR Code:

## QR Switches (formatted into the ^FD field data)

## mixed mode &lt;D&gt;

D = allows mixing of different types of character modes in one code.

code No. &lt;01 16&gt;

Value = subtracted from the Nth number of the divided code (must be two digits).

## No. of divisions &lt;02 16&gt;

Number of divisions (must be two digits).

## parity data &lt;1 byte&gt;

Parity data value is obtained by calculating at the input data (the original input data before divided byte-by-byte through the EX-OR operation).

## error correction level &lt;H, Q, M, L&gt;

```
H = ultra-high reliability level Q = high reliability level M = standard level (default) L = high density level
```

## character Mode &lt;N, A, B, K&gt;

alphanumeric

```
N = numeric A =
```

Bxxxx = 8-bit byte mode. This handles the 8-bit Latin/Kana character set in accordance with JIS X 0201 (character values 0x00 to 0xFF).

xxxx = number of data characters is represented by two bytes of BCD code.

K = Kanji - handles only Kanji characters in accordance with the Shift JIS system based on JIS X 0208. This means that all parameters after the character mode K should be 16-bit characters. If there are any 8-bit characters (such as ASCII code), an error occurs.

## data character string &lt;Data&gt;

Follows character mode or it is the last switch in the ^FD statement.

## data input &lt;A, M&gt;

A = Automatic Input (default). Data character string JIS8 unit, Shift JIS. When the input mode is Automatic Input, the binary codes of 0x80 to 0x9F and 0xE0 to 0xFF cannot be set.

M = Manual Input

Two types of data input mode exist: Automatic (A) and Manual (M). If A is specified, the character mode does not need to be specified. If M is specified, the character mode must be specified.

## ^FD Field Data (Normal Mode)

```
Automatic Data Input (A) with Switches ^FD <error correction level>A, <data character string> ^FS
```

<!-- image -->

Example •

- QR Code, normal mode with automatic data input.

GENERATED LABEL

口

<!-- image -->

口

- 1 Q = error correction level
- 2 A, = automatic setting
- 3 data string character

## Manual Data Input (M) with Switches

&lt;character mode&gt;&lt;data character string&gt;

```
^FD <error correction level>M, ^FS
```

- Example · QR Code, normal mode with manual data input:
- 1 H = error correction level (ultra-high reliability level
- 2 M, = input mode (manual input)
- 3 N = character mode (numeric data)
- 4 data character string

<!-- image -->

<!-- image -->

Example · QR Code, normal mode with standard reliability and manual data input:

<!-- image -->

<!-- image -->

- 1 M = error correction level (standard-high reliability level
- 2 M, = manual input
- 3 A = alphanumeric data
- 4 AC-42 = data character string

## ^FD Field Data (Mixed Mode - requires more switches)

```
Automatic Data Input (A) with Switches ^FD <D><code No.> <No. of divisions> <parity data>, <error correction level> A, <data character string>, <data character string>, <  :  >, <data character string n**> ^FS Manual Data Input (M) with Switches ^FD <code No.> <No. of divisions> <parity data>, <error correction level> M, <character mode 1> <data character string 1>, <character mode 2> <data character string 2>, < :  > <  :  >, <character mode n> <data character string n**> ^FS
```

n** up to 200 in mixed mode

<!-- image -->

| <mixed mode identifier>   | D      | (mixed)                             |
|---------------------------|--------|-------------------------------------|
| <code No.>                | M      | (code number)                       |
| <No. of divisions>        | D      | (divisions)                         |
