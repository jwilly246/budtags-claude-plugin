<!-- Source: ZPL II Programming Guide Volume 1 -->
<!-- Section: UPC/EAN Barcodes (^B5-^B9, ^BE, ^BU) -->
<!-- Generated: 2025-11-02 04:52:35 -->

<!-- image -->

| Parameters                    | Details                                                                                                                                                                                                                                                                                                         |
|-------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| f = print interpretation line | Accepted Values: N = no line printed A = print interpretation line above code B = print interpretation line below code Default Value: N When the field data exceeds two rows, expect the interpretation line to extend beyond the right edge of the bar code symbol.                                            |
| m = starting mode             | Accepted Values: 0 = Regular Alphanumeric Mode 1 = Multiple Read Alphanumeric 2 = Regular Numeric Mode 3 = Group Alphanumeric Mode 4 = Regular Alphanumeric Shift 1 5 = Regular Alphanumeric Shift 2 A = Automatic Mode. The printer determines the starting mode by analyzing the field data. Default Value: A |

Example •

## This is an example of a Code 49 bar code:

<!-- image -->

<!-- image -->

| Field Data Set                                                           | Unshifted Character Set                                                  | Shift 1 Character Set                                                    | Shift 2 Character Set                                                    |
|--------------------------------------------------------------------------|--------------------------------------------------------------------------|--------------------------------------------------------------------------|--------------------------------------------------------------------------|
| 0                                                                        | 0                                                                        | '                                                                        |                                                                          |
| 1                                                                        | 1                                                                        | ESC                                                                      | ;                                                                        |
| 2                                                                        | 2                                                                        | FS                                                                       | <                                                                        |
| 3                                                                        | 3                                                                        | GS                                                                       | =                                                                        |
| 4                                                                        | 4                                                                        | RS                                                                       | >                                                                        |
| 5                                                                        | 5                                                                        | US                                                                       | ?                                                                        |
| 6                                                                        | 6                                                                        | !                                                                        | @                                                                        |
| 7                                                                        | 7                                                                        | '                                                                        | [                                                                        |
| 8                                                                        | 8                                                                        | #                                                                        | \                                                                        |
| 9                                                                        | 9                                                                        | &                                                                        | ]                                                                        |
| A                                                                        | A                                                                        | SOH                                                                      | a                                                                        |
| B                                                                        | B                                                                        | STX                                                                      | b                                                                        |
| C                                                                        | C                                                                        | ETX                                                                      | c                                                                        |
| D                                                                        | D                                                                        | EOT                                                                      | d                                                                        |
| E                                                                        | E                                                                        | ENQ                                                                      | e                                                                        |
| F                                                                        | F                                                                        | ACK                                                                      | f                                                                        |
| G                                                                        | G                                                                        | BEL                                                                      | g                                                                        |
| H                                                                        | H                                                                        | BS                                                                       | h                                                                        |
| I                                                                        | I                                                                        | HT                                                                       | I                                                                        |
| J                                                                        | J                                                                        | LF                                                                       | j                                                                        |
| K                                                                        | K                                                                        | VT                                                                       | k                                                                        |
| L                                                                        | L                                                                        | FF                                                                       | l                                                                        |
| M                                                                        | M                                                                        | CR                                                                       | m                                                                        |
| N                                                                        | N                                                                        | SO                                                                       | n                                                                        |
| O                                                                        | O                                                                        | SI                                                                       | o                                                                        |
| P                                                                        | P                                                                        | DLE                                                                      | p                                                                        |
| Q                                                                        | Q                                                                        | DC1                                                                      | q                                                                        |
| R                                                                        | R                                                                        | DC2                                                                      | r                                                                        |
| S                                                                        | S                                                                        | DC3                                                                      | s                                                                        |
| T                                                                        | T                                                                        | DC4                                                                      | t                                                                        |
| U                                                                        | U                                                                        | NAK                                                                      | u v                                                                      |
| V W                                                                      | V W                                                                      | SYN ETB                                                                  | w                                                                        |
| X                                                                        | X                                                                        | CAN                                                                      | x                                                                        |
| Y                                                                        | Y                                                                        | EM                                                                       | y                                                                        |
| Z                                                                        | Z                                                                        | SUB                                                                      | z                                                                        |
|                                                                          | -                                                                        | (                                                                        | _                                                                        |
| -                                                                        |                                                                          |                                                                          |                                                                          |
| . SPACE                                                                  | . SPACE                                                                  | )                                                                        | '                                                                        |
|                                                                          |                                                                          | Null                                                                     | DEL                                                                      |
| $                                                                        | $                                                                        | *                                                                        | {                                                                        |
| /                                                                        | /                                                                        | ,                                                                        | |                                                                        |
| ++                                                                       | ++                                                                       | :                                                                        | }                                                                        |
| %                                                                        | %                                                                        | reserved                                                                 | ~                                                                        |
| < (Shift 1)                                                              |                                                                          |                                                                          |                                                                          |
| > (Shift 2)                                                              |                                                                          |                                                                          |                                                                          |
| : (N.A.)                                                                 |                                                                          |                                                                          |                                                                          |
| ; (N.A.)                                                                 |                                                                          |                                                                          |                                                                          |
| ? (N.A.) = (Numeric Shift) Code 49 Shift 1 and 2 Character Substitutions | ? (N.A.) = (Numeric Shift) Code 49 Shift 1 and 2 Character Substitutions | ? (N.A.) = (Numeric Shift) Code 49 Shift 1 and 2 Character Substitutions | ? (N.A.) = (Numeric Shift) Code 49 Shift 1 and 2 Character Substitutions |

Table 3 • Code 49

<!-- image -->

<!-- image -->

## Code 49 Field Data Character Set

The ^FD data sent to the printer when using starting modes 0 to 5 is based on the Code 49 Internal Character Set. This is shown in the first column of the Code 49 table on the previous page. These characters are Code 49 control characters:

<!-- formula-not-decoded -->

Valid field data must be supplied when using modes 0 to 5. Shifted characters are sent as a two-character sequence of a shift character followed by a character in the unshifted character set.

Example · To encode a lowercase a , send a &gt; (Shift 2) followed by an uppercase A . If interpretation line printing is selected, a lowercase a prints in the interpretation line. This reflects what the output from the scanner reads. Code 49 uses uppercase alphanumeric characters only.

If an invalid sequence is detected, the Code 49 formatter stops interpreting field data and prints a symbol with the data up to the invalid sequence. These are examples of invalid sequences:

- Terminating numeric mode with any characters other than 0 to 9 or a Numeric Space.
- Starting in Mode 4 (Regular Alphanumeric Shift 1) and the first field data character is not in the Shift 1 set.
- Starting in Mode 5 (Regular Alphanumeric Shift 2) and the first field data character is not in the Shift 2 set.
- Sending Shift 1 followed by a character not in the Shift 1 set.
- Sending Shift 2 followed by a character not in the Shift 2 set.
- Sending two Shift 1 or Shift 2 control characters.

## Advantages of Using the Code 49 Automatic Mode

Using the default (Automatic Mode) completely eliminates the need for selecting the starting mode or manually performing character shifts. The Automatic Mode analyzes the incoming ASCII string, determines the proper mode, performs all character shifts, and compacts the data for maximum efficiency.

Numeric Mode is selected or shifted only when five or more continuous digits are found. Numeric packaging provides no space advantage for numeric strings consisting of fewer than eight characters.

## ^B5

## Planet Code bar code

Description The ^B5 command is supported in all printers as a resident bar code.

Format ^B5o,h,f,g

This table identifies the parameters for this format:

| Parameters                                                              | Details                                                                                                                                |
|-------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------|
| o = orientation code                                                    | Accepted Values: N = normal R = rotated I = inverted 180 degrees B = read from bottom up, 270 degrees Default Value: current ^FW value |
| h = bar code height (in dots)                                           | Accepted Values: 1 to 9999 Default Value: value set by ^BY                                                                             |
| f = interpretation line                                                 | Accepted Values: N = no default Y = yes                                                                                                |
| g = determines if the interpretation line is printed above the bar code | Accepted Values: N = no default Y = yes                                                                                                |

## Example · This is an example of a Planet Code bar code:

## ZPL II CODE

^XA

^FO150,100^BY3

^B5N,100,Y,0

^FD12345678901$FS

^XZ

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

## ^B7

## PDF417 Bar Code

Description The ^B7 command produces the PDF417 bar code, a two-dimensional, multirow, continuous, stacked symbology. PDF417 is capable of encoding over 1,000 characters per bar code. It is ideally suited for applications requiring large amounts of information at the time the bar code is read.

The bar code consists of three to 90 stacked rows. Each row consists of start and stop patterns and symbol characters called code-words . A code-word consists of four bars and four spaces. A three code-word minimum is required per row.

The PDF417 bar code is also capable of using the structured append option ( ^FM ), which allows you to extend the field data limitations by printing multiple bar codes. For more information on using structured append, see ^FM on page 137.

- PDF417 has a fixed print ratio.
- Field data ( ^FD) is limited to 3K of character data.

Format ^B7o,h,s,c,r,t

This table identifies the parameters for this format:

| Parameters                                         | Details                                                                                                                                                                                                                                                                                                                                                                              |
|----------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| o = orientation                                    | Accepted Values: N = normal R = rotated 90 degrees (clockwise) I = inverted 180 degrees B = read from bottom up, 270 degrees Default Value: current ^FW value                                                                                                                                                                                                                        |
| h = bar code height for individual rows (in dots)  | Accepted Values: 1 to height of label Default Value: value set by ^BY This number multiplied by the module equals the height of the individual rows in dots. 1 is not a recommended value.                                                                                                                                                                                           |
| s = security level                                 | Accepted Values: 1 to 8 (error detection and correction) Default Value: 0 (error detection only) This determines the number of error detection and correction code-words to be generated for the symbol. The default level provides only error detection without correction. Increasing the security level adds increasing levels of error correction and increases the symbol size. |
| c = number of data columns to encode               | Accepted Values: 1 to 30 Default Value: 1:2 (row-to-column aspect ratio) You can specify the number of code-word columns giving control over the width of the symbol.                                                                                                                                                                                                                |
| r = number of rows to encode                       | Accepted Values: 3 to 90 Default Value: 1:2 (row-to-column aspect ratio) You can specify the number of symbol rows giving control over the height of the symbol. For example, with no row or column values entered, 72 code-words would be encoded into a symbol of six columns and 12 rows. Depending on code- words, the aspect ratio is not always exact.                         |
| t = truncate right row indicators and stop pattern | Accepted Values: Y (perform truncation) and N (no truncation) Default Value: N                                                                                                                                                                                                                                                                                                       |

<!-- image -->

<!-- image -->

Example · This is an example of a PDF417 bar code:

<!-- image -->

Example · This is an example of a PDF417 without and with truncation selected:

PDF417 without Truncation being selected

<!-- image -->

PDF417 with Truncation being selected

<!-- image -->

Example · This example shows the ^B7 command used with field hex ( ^FH ) characters:

<!-- image -->

## ZPL II CODE

```
^XA ^FO50,50^BY3,3.0^B7N,8,5,7,21,N ^FH_^FD[)>_1E06_1DP12345678_1DQ160 _1D1JUN123456789A2B4C6D8E_1D20LA6-987 _1D21L54321 ZES_1D15KG1155 _1DBSC151208_1D7Q10GT_1E_04^FS
```

- ^XZ

## Comments Noted in this bulleted list:

- If both columns and rows are specified, their product must be less than 928.
- No symbol is printed if the product of columns and rows is greater than 928.
- No symbol is printed if total code-words are greater than the product of columns and rows.
- Serialization is not allowed with this bar code.
- The truncation feature can be used in situations where label damage is not likely. The right row indicators and stop pattern is reduced to a single module bar width. The difference between a nontruncated and a truncated bar code is shown in This is an example of a PDF417 without and with truncation selected: on page 32.

## Special Considerations for ^BY When Using PDF417

When used with ^B7 , the parameters for the ^BY command are:

w = module width (in dots)

Accepted Values: 2 to 10

Default Value: 2

r  = ratio

Fixed Value: 3 (ratio has no effect on PDF417)

h = height of bars (in dots)

Accepted Values: 1 to 32000

Default Value: 10

PDF417 uses this only when row height is not specified in the ^B7 h parameter.

<!-- image -->

<!-- image -->

## Special Considerations for ^FD When Using PDF417

The character set sent to the printer with the ^FD command includes the full ASCII set, except for those characters with special meaning to the printer.

## Page Number 850 table

<!-- image -->

- CR and LF are also valid characters for all ^FD statements. This scheme is used:

\&amp; = carriage return/line feed

\\ = backslash (\)

- ^CI13 must be selected to print a backslash (\).

## ^B8

## EAN-8 Bar Code

Description The ^B8 command is the shortened version of the EAN-13 bar code. EAN is an acronym for European Article Numbering. Each character in the EAN-8 bar code is composed of four elements: two bars and two spaces.

- ^B8 supports a fixed ratio.
- Field data ( ^FD ) is limited to exactly seven characters. ZPL II automatically pads or truncates on the left with zeros to achieve the required number of characters.
- When using JAN-8 (Japanese Article Numbering), a specialized application of EAN-8, the first two non-zero digits sent to the printer are always 49.

Format ^B8o,h,f,g
