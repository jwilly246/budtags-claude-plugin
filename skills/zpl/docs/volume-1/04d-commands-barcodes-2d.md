<!-- Source: ZPL II Programming Guide Volume 1 -->
<!-- Section: 2D Barcodes (^BQ, ^BX, ^BO) -->
<!-- Generated: 2025-11-02 04:52:35 -->

| Parameters                   | Details                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
|------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| r = number of rows to encode | Accepted Values: for CODABLOCK A: 1 to 22 for CODABLOCK E and F: 2 to 4 • If values for c and r are not specified, a single row is produced. • If a value for r is not specified, and c exceeds the maximum range, a single row equal to the field data length is produced. • If a value for c is not specified, the number of characters per row is derived by dividing the field data by the value of r . • If both parameters are specified, the amount of field data must be less than the product of the specified parameters. If the field data exceeds the value of the product, either no symbol or an error code is printed (if ^CV is active). • If the data field contains primarily numeric data, fewer than the specified rows might be printed. If the field data contains several shift and code-switch characters, more |
| m = mode                     | Accepted Values: A , E , F CODABLOCK A uses the Code 39 character set. CODABLOCK F uses the Code 128 character set. CODABLOCK E uses the Code 128 character set and automatically adds FNC1. Default Value: F                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |

Example · This is an example of a CODABLOCK bar code:

<!-- image -->

## Special Considerations for the ^BY Command When Using ^BB

The parameters for the ^BYw,r,h command, when used with a ^BB

w = module width (in dots) Accepted Values: 2 to 10 (CODABLOCK A only) Default Value: 2 r = ratio Fixed Value: 3 (ratio has no effect on CODABLOCK E or F) h = height of bars (in dots) Accepted Values: 1 to 32,32000 Default Value: 10

CODABLOCK uses this as the overall symbol height only when the row height is not specified in the ^BB h parameter.

```
code, are as follows:
```

<!-- image -->

## Special Considerations for ^FD Character Set When Using ^BB

The character set sent to the printer depends on the mode selected in parameter m.

CODABLOCK A: CODABLOCK A uses the same character set as Code 39. If any other character is used in the ^FD statement, either no bar code is printed or an error message is printed (if ^CV is active).

CODABLOCK E: The Automatic Mode includes the full ASCII set except for those characters with special meaning to the printer. Function codes or the Code 128 Subset A &lt; nul &gt; character can be inserted using of the ^FH command.

| <fnc1> = 80 hex   | <fnc3> = 82 hex   |
|-------------------|-------------------|
| <fnc2> = 81 hex   | <fnc4> = 83 hex   |
| <nul> = 84 hex    |                   |

For any other character above 84 hex, either no bar code is printed or an error message is printed (if ^CV is active).

CODABLOCK F: CODABLOCK F uses the full ASCII set, except for those characters with special meaning to the printer. Function codes or the Code 128 Subset A &lt; nul &gt; character can be inserted using of the ^FH command.

| <fnc1> = 80 hex   | <fnc3> = 82 hex   |
|-------------------|-------------------|
| <fnc2> = 81 hex   | <fnc4> = 83 hex   |
| <nul> = 84 hex    |                   |

<!-- image -->

## ^BC

## Code 128 Bar Code (Subsets A, B, and C)

Description The ^BC command creates the Code 128 bar code, a high-density, variable length, continuous, alphanumeric symbology. It was designed for complexly encoded product identification.

Code 128 has three subsets of characters. There are 106 encoded printing characters in each set, and each character can have up to three different meanings, depending on the character subset being used. Each Code 128 character consists of six elements: three bars and three spaces.

- ^BC supports a fixed print ratio.
- Field data ( ^FD ) is limited to the width (or length, if rotated) of the label.

Format ^BCo,h,f,g,e,m

Important · If additional information about the Code 128 bar code is required, go to www.aimglobal.org .

This table identifies the parameters for this format:

| Parameters                               | Details                                                                                                                                                         |
|------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------|
| o = orientation                          | Accepted Values: N = normal R = rotated 90 degrees (clockwise) I = inverted 180 degrees B = read from bottom up, 270 degrees Default Value: current ^FW value   |
| h = bar code height (in dots)            | Accepted Values: 1 to 32000 Default Value: value set by ^BY                                                                                                     |
| f = print interpretation line            | Accepted Values: Y (yes) or N (no) Default Value: Y The interpretation line can be printed in any font by placing the font command before the bar code command. |
| g = print interpretation line above code | Accepted Values: Y (yes) or N (no) Default Value: N                                                                                                             |

<!-- image -->

| Parameters          | Details                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
|---------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| e = UCC check digit | Accepted Values: Y (turns on) or N (turns off) Mod 103 check digit is always there. It cannot be turned on or off. Mod 10 and 103 appear together with e turned on. Default Value: N                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| m = mode            | Accepted Values: N = no selected mode U = UCC Case Mode • More than 19 digits in ^FD or ^SN are eliminated. • Fewer than 19 digits in ^FD or ^SN add zeros to the right to bring the count to 19. This produces an invalid interpretation line. A = Automatic Mode. This analyzes the data sent and automatically determines the best packing method. The full ASCII character set can be used in the ^FD statement -the printer determines when to shift subsets. A string of four or more numeric digits causes an automatic shift to Subset C. D = New Mode (x.11.x and newer firmware) This allows dealing with UCC/EAN with and without chained application identifiers. The code starts in the appropriate subset followed by FNC1 to indicate a UCC/EAN 128 bar code. The printer automatically strips out parentheses and spaces for encoding, but prints them in the human-readable section. The printer automatically determines if a check digit is required, calculate it, and print it. Automatically sizes the human readable. Default Value: N |

Example · This is an example of a Code 128 bar code:

<!-- image -->

## Code 128 Subsets

The Code 128 character subsets are referred to as Subset A, Subset B, and Subset C. A subset can be selected in these ways:

- A special Invocation Code can be included in the field data ( ^FD ) string associated with that bar code.
- The desired Start Code can be placed at the beginning of the field data. If no Start Code is entered, Subset B are used.

To change subsets within a bar code, place the Invocation Code at the appropriate points within the field data ( ^FD ) string. The new subset stays in effect until changed with the Invocation Code. For example, in Subset C, &gt;7 in the field data changes the Subset to A.

Table 6 shows the Code 128 Invocation Codes and Start Characters for the three subsets.

Table 6 • Code 128 Invocation Characters

| Invocation Code   | Decimal Value    | SubsetA Character   | Subset B Character                  | Subset C Character                  |
|-------------------|------------------|---------------------|-------------------------------------|-------------------------------------|
| ><                | 62               |                     |                                     |                                     |
| >0                | 30               | >                   | >                                   |                                     |
| >=                | 94               |                     | ~                                   |                                     |
| >1                | 95               | USQ                 | DEL                                 |                                     |
| >2                | 96               | FNC 3               | FNC 3                               |                                     |
| >3                | 97               | FNC 2               | FNC 2                               |                                     |
| >4                | 98               | SHIFT               | SHIFT                               |                                     |
| >5                | 99               | CODE C              | CODE C                              |                                     |
| >6                | 100              | CODE B              | FNC 4                               | CODE B                              |
| >7                | 101              | FNC 4               | CODEA                               | CODEA                               |
| >8                | 102              | FNC 1               | FNC 1                               | FNC 1                               |
| Start Characters  | Start Characters |                     |                                     |                                     |
| >9                | 103              | Start CodeA         | (Numeric Pairs give Alpha/Numerics) | (Numeric Pairs give Alpha/Numerics) |
| >:                | 104              | Start Code B        | (Normal Alpha/Numeric)              | (Normal Alpha/Numeric)              |
| >;                | 105              | Start Code C        | (All numeric (00 - 99)              | (All numeric (00 - 99)              |

Table 7 shows the character sets for Code 128:

<!-- image -->

Table 7 • Code 128 character sets

| Value 0   | CodeA SP   | Code B SP   | Code C 00   | Value 53   | CodeA U      | Code B U       | Code C 53   |
|-----------|------------|-------------|-------------|------------|--------------|----------------|-------------|
| 1         | !          | !           | 01          | 54         | V            | V              | 54          |
| 2         | ''         | ''          | 02          | 55         | W            | W              | 55          |
| 3         | #          | #           | 03          | 56         | X            | X              | 56          |
| 4         | $          | $           | 04          | 57         | Y            | Y              | 57          |
| 5         | %          | %           | 05          | 58         | Z            | Z              | 58          |
| 6         | &          | &           | 06          | 59         | [            | [              | 59          |
| 7         | '          | '           | 07          | 60         | \            | \              | 60          |
| 8         | (          | (           | 08          | 61         | ]            | ]              | 61          |
| 9         | )          | )           | 09          | 62         | ^            | ^              | 62          |
| 10        | *          | *           | 10          | 63         | _            | _              | 63          |
| 11        | ++         | ++          | 11          | 64         | NUL          | .              | 64          |
| 12        | ,          | ,           | 12          | 65         | SOH          | a              | 65          |
| 13        | -          | -           | 13          | 66         | STX          | b              | 66          |
| 14        | .          | .           | 14          | 67         | ETX          | c              | 67          |
| 15        | /          | /           | 15          | 68         | EOT          | d              | 68          |
| 16        | 0          | 0           | 16          | 69         | ENQ          | e              | 69          |
| 17        | 1          | 1           |             |            | ACK          | f              | 70          |
| 18        | 2          | 2           | 17          | 70         | BEL          | g              | 71          |
|           |            |             | 18          | 71 72      | BS           | h              |             |
| 19        | 3          | 3           | 19          |            |              |                | 72          |
| 20 21     | 4 5        | 4           | 20          | 73         | HT           | i j            | 73          |
| 22        | 6          | 5 6         | 21 22       | 74 75      | LF VT        | k              | 74 75       |
| 23        | 7          | 7           | 23          | 76         | FF           | l              | 76          |
|           |            |             |             |            | CR           | m              | 77          |
| 24        | 8          | 8           | 24          | 77         | SO           | n              | 78          |
| 25        | 9          | 9           | 25          | 78 79      | SI           | o              | 79          |
| 26        | : ;        | : ;         | 26 27       | 80         | DLE          | p              | 80          |
| 28        |            |             |             |            | DC1          | q              | 81          |
| 27        | <          | <           | 28          | 81         | DC2          |                |             |
| 29        | =          | =           | 29          | 82         | DC3          | r              | 82          |
| 30        | > ?        | >           | 30          | 83         |              | s              | 83          |
| 31        | @          | ?           | 31          | 84         | DC4 NAK      | t u            | 84          |
| 32        | A          | @           | 32          | 85         | SYN          | v              | 85 86       |
| 33        |            | A           | 33          | 86         |              |                |             |
| 34        | B          | B           | 34          | 87         | ETB          | w              | 87          |
| 35        | C          | C           | 35          | 88         | CAN EM       | x              | 88          |
| 36        | D          | D           | 36          | 89         |              | y              | 89          |
| 37        | E          | E           | 37          | 90         | SUB          | z              | 90          |
| 38        | F          | F           | 38          | 91         | ESC          | {              | 91          |
| 39        | G          | G           | 39          | 92         | FS           | |              | 92          |
| 40        | H          | H           | 40 41       | 93 94      | GS RS        | } ~            | 93 94       |
| 41        | I          | I           |             |            |              |                |             |
| 42        | J          | J           | 42          | 95         | US           | DEL            | 95          |
| 43        | K          | K           | 43          | 96         | FNC3         | FNC3           | 96          |
| 44 45     | L          | L           | 44 45       | 97         | FNC2         | FNC2           | 97          |
| 46        | M N        | M N         | 46          | 98         | SHIFT Code C | SHIFT Code C   | 98          |
| 47        |            |             |             | 99         |              |                | 99          |
|           | O          | O           | 47          | 100        | Code B       | FNC4           | Code B      |
| 48        | P          | P           | 48          | 101        | FNC4         | CodeA          | CodeA       |
| 49        | Q          | Q           | 49          |            |              |                |             |
| 50        | R          | R           | 50          | 102        | FNC1         | FNC1           | FNC1        |
|           |            |             |             | 103        |              | START (Code A) |             |
| 51        | S          | S           | 51          | 104        | START        | START (Code B) | C)          |

<!-- image -->

Example · Figures A and B are examples of identical bar codes, and Figure C is an example of switching from Subset C to B to A, as follows:

<!-- image -->

C0DE128

<!-- image -->

Because Code 128 Subset B is the most commonly used subset, ZPL II defaults to Subset B if no start character is specified in the data string.

382436C0TE128TEST

<!-- image -->

^XA ^FO50,50 ^BY3^B C N,100,Y,N,N ^FD&gt;;382436&gt;6 C ODE128&gt;752375152^FS

^XZ

Figure C: Switching from Subset C to B to A

## How ^BC Works Within a ZPL II Script

- ^XA - the first command starts the label format.
- ^FO100,75 - the second command sets the field origin at 100 dots across the x-axis and 75 dots down the y-axis from the upper-left corner.
- ^BCN,100,Y,N,N - the third command calls for a Code 128 bar code to be printed with no rotation (N) and a height of 100 dots. An interpretation line is printed (Y) below the bar code (N). No UCC check digit is used (N).
- ^FDCODE128^FS (Figure A) ^FD&gt;:CODE128^FS (Figure B) - the field data command specifies the content of the bar code.
- ^XZ - the last command ends the field data and indicates the end of the label.

<!-- image -->

The interpretation line prints below the code with the UCC check digit turned off.

The ^FD command for Figure A does not specify any subset, so Subset B is used. In Figure B, the ^FD command specifically calls Subset B with the &gt;: Start Code. Although ZPL II defaults to Code B, it is good practice to include the Invocation Codes in the command.

Code 128 - Subset B is programmed directly as ASCII text, except for values greater than 94 decimal and a few special characters that must be programmed using the invocation codes. Those characters are:

^ &gt; ~

## Example · Code 128 - Subsets A and C

Code 128, Subsets A and C are programmed in pairs of digits, 00 to 99, in the field data string. For details, see Table 6 on page 49 .

In Subset A, each pair of digits results in a single character being encoded in the bar code; in Subset C, characters are printed as entered. Figure E below is an example of Subset A (&gt;9 is the Start Code for Subset A).

Nonintegers programmed as the first character of a digit pair (D2) are ignored. However, nonintegers programmed as the second character of a digit pair (2D) invalidate the entire digit pair, and the pair is ignored. An extra unpaired digit in the field data string just before a code shift is also ignored.

Figure C and Figure D below are examples of Subset C. Notice that the bar codes are identical. In the program code for Figure D, the D is ignored and the 2 is paired with the 4.

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

## The UCC/EAN-128 Symbology

The symbology specified for the representation of Application Identifier data is UCC/EAN128, a variant of Code 128, exclusively reserved to EAN International and the Uniform Code Council (UCC).

Note · It is not intended to be used for data to be scanned at the point of sales in retail outlets.

UCC/EAN-128 offers several advantages. It is one of the most complete, alphanumeric, onedimensional symbologies available today. The use of three different character sets (A, B and C), facilitates the encoding of the full 128 ASCII character set. Code 128 is one of the most compact linear bar code symbologies. Character set C enables numeric data to be represented in a double density mode. In this mode, two digits are represented by only one symbol character saving valuable space. The code is concatenated. That means that multiple AIs and their fields may be combined into a single bar code. The code is also very reliable. Code 128 symbols use two independent self-checking features which improves printing and scanning reliability.

UCC/EAN-128 bar codes always contain a special non-data character known as function 1 (FNC 1), which follows the start character of the bar code. It enables scanners and processing software to auto-discriminate between UCC/EAN-128 and other bar code symbologies, and subsequently only process relevant data.

The UCC/EAN-128 bar code is made up of a leading quiet zone, a Code 128 start character A, B, or C, a FNC 1 character, Data (Application Identifier plus data field), a symbol check character, a stop character, and a trailing quiet zone.

UCC/EAN, UCC/128 are a couple of ways you'll hear someone refer to the code. This just indicates that the code is structured as dictated by the application identifiers that are used.

SSCC (Serial Shipping Container Code) formatted following the data structure layout for Application Identifier 00. See Table 8, UCC Application Identifier Table on page 57. It could be 00 which is the SSCC code. The customer needs to let us know what application identifiers are used for their bar code so we can help them.

There are several ways of writing the code to print the code to Application Identifier '00' structure.

<!-- image -->

