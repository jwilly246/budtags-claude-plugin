<!-- Source: ZPL II Programming Guide Volume 2 -->
<!-- Section: Chapter 3: Advanced Techniques - Control Commands -->
<!-- Generated: 2025-11-02 04:52:35 -->

## Fonts and Bar Codes

<!-- image -->

This section provides information about different fonts (type faces) and bar codes that can be used with the printer.

## Contents

| Standard Printer Fonts . . . . . . . . .      |   60 |
|-----------------------------------------------|------|
| Proportional and Fixed Spacing . .            |   61 |
| Scalable Versus Bitmapped Fonts               |   62 |
| Scalable Fonts . . . . . . . . . . . . .      |   62 |
| Bitmapped Fonts . . . . . . . . . . .         |   62 |
| Font Matrices . . . . . . . . . . . . . . . . |   64 |
| 6 dot/mm printhead . . . . . . . . .          |   64 |
| 8 dot/mm (203 dpi) printhead. .               |   64 |
| 12 dot/mm (300 dpi) printhead.                |   65 |
| 24 dot/mm (600 dpi) printhead.                |   65 |
| Bar Codes . . . . . . . . . . . . . . . . . . |   66 |
| Basic Format for Bar Codes. . .               |   67 |
| Bar Code Field Instructions . . .             |   67 |
| Bar Code Command Groups . .                   |   69 |

<!-- image -->

## Standard Printer Fonts

Most Zebra printers come standard with 15 bitmapped fonts and one scalable font (Figure 9). Additional downloadable bitmapped and scalable fonts are also available. Character size and density (how dark it appears) depend on the density of the printhead and the media used.

```
A B C D A B C D A B C D A B C D A B C D A B C D 1 2 3 4 5 1 2 3 4 5 1 2 3 4 5 1 2 3 4 5 1 2 3 4 5 1 2 3 4 5 12345 (Scalable) ABCDwxyz w x y z w x y z w x y z w x y z w x y z w x y z FONT U-FONT T-FONT S-FONT R-FONT Q-FONT P-FONT GS FONT 0 FONT G Az 4 - -----/c70/c79/c78/c84/c32/c69/c32/c45/c45/c32/c40/c79/c67/c82/c45/c66/c41/c32/c65/c66/c67/c68/c119/c120/c121/c122/c32/c49/c50/c51/c52/c53 /c70/c79/c78/c84 /c70/c79/c78/c84 /c70/c79/c78/c84 /c70/c79/c78/c84 /c70/c32/c45/c45 /c68/c32/c45/c45 /c66/c32/c45/c45 /c65/c32/c45/c45 /c65/c66/c67/c68 /c65/c66/c67/c68 /c65/c66/c67/c68 /c65/c66/c67/c68 /c49/c50/c51/c52/c53 /c49/c50/c51/c52/c53 /c49/c50/c51/c52/c53 /c49/c50/c51/c52/c53 /c119/c120/c121/c122 /c119/c120/c121/c122 /c87/c88/c89/c90 /c119/c120/c121/c122 /c70/c79/c78/c84/c32/c72/c32/c45/c45/c32/c40/c79/c67/c82/c45/c65/c41/c32/c85/c80/c80/c69/c82/c32/c67/c65/c83/c69/c32/c79/c78/c76/c89 C R
```

```
FONT V-A B C D 1 2 3 4 5 w x y z
```

Figure 9 • Examples of the Standard Printer Fonts

To use one of these fonts, you must either use the change alphanumeric default font command ( ^CF ) or specify an alphanumeric field command ( ^A ). Refer to ZPL II Programming Guide Volume One for complete information on both commands.

The standard Zebra character set is Code 850 for character values greater than 20 HEX. There are six HEX character values below 20 HEX that are also recognized. Figure 10 shows how these character values are printed.

Note · Unidentified characters should default to a space.

<!-- image -->

Figure 10 • Recognized HEX Values below 20 HEX

|       | A HEX   | 1a              | will print a 0(numeric)   |
|-------|---------|-----------------|---------------------------|
| A HEX | 1b      | will print a a  | %                         |
| A HEX | 1c      | will print a a  | %                         |
| A HEX | 1d      | will print a a  | IJ                        |
| A HEX | 1e      | will print a    | ij                        |
| A HEX | 1f      | will  print a a |                           |

## Proportional and Fixed Spacing

Proportional spacing is different than fixed spacing. In Table 10, the intercharacter gap (space between characters) is constant for fonts A through H, which means that the spacing between all characters is the same. For example, the spacing between the letters MW is the same as between the letters IE .

The baseline is the imaginary line on which the bottom (base) of all characters (except any descenders) rest. The area between the baseline and the bottom of the matrix is used for any character 'descenders.' Baseline numbers define where the baseline is located in relationship to the top of the matrix. For example, the baseline for font 'E' is 23 dots down from the top of the matrix.

Table 10 • Intercharacter Gap and Baseline Parameters

| Font   | H x W(in dots)   | Type   | Intercharacter Gap (in dots)   | Baseline (in dots)   |
|--------|------------------|--------|--------------------------------|----------------------|
| A      | 9 x 5            | U-L-D  | 1                              | 7                    |
| B      | 11 x 7           | U      | 2                              | 11                   |
| C,D    | 18 x 10          | U-L-D  | 2                              | 14                   |
| E      | 28 x 15          | OCR-B  | 5                              | 23                   |
| F      | 26 x 13          | U-L-D  | 3                              | 21                   |
| G      | 60 x 40          | U-L-D  | 8                              | 48                   |
| H      | 21 x 13          | OCR-A  | 6                              | 21                   |
| GS     | 24 x 24          | SYMBOL | PROPORTIONAL                   | 3 x HEIGHT/4         |
| 0      | DEFAULT: 15 x 12 |        | PROPORTIONAL                   | 3 x HEIGHT/4         |

<!-- image -->

## Scalable Versus Bitmapped Fonts

For scalable fonts, setting the height and width equally produces characters that appear the most balanced. Balanced characters are pleasing to the eye because actual height and width are approximately equal to each other. This is achieved through the use of a smooth-scaling algorithm in the printer.

For bitmapped fonts, this balancing is built into the font. In actuality, the height of a bitmap font is slightly larger than the width. Bitmap fonts are always at the maximum size of the character's cell.

## Scalable Fonts

All dot parameters used in the commands to create scalable fonts are translated into a point size because scalable fonts are measured in point sizes, not dots. To determine how many dots to enter to obtain a particular point size, use the following formula. The actual point size will be an approximate value.

<!-- formula-not-decoded -->

- For printers using a 6 dot/mm printhead the 'dots per inch of printer' value is 152.4
- For printers using a 8 dot/mm printhead the 'dots per inch of printer' value is 203.2
- For printers using a 12 dot/mm printhead the 'dots per inch of printer' value is 304.8
- For printers using a 24 dot/mm printhead the 'dots per inch of printer' value is 609.6

The actual height and width of the character in dots will vary, depending on the font style and the particular character. Therefore, some characters will be smaller and some will be larger than the actual dot size requested. The baselines for all scalable fonts are calculated against the dot size of the cell. The baseline is 3/4 down from the top of the cell. For example, if the size of the cell is 80 dots, the baseline will be 60 dots (3/4) down from the top of the cell.

For more information concerning fonts and related commands, refer to the ~DB (Download Bitmap Font) and ~DS (Download Scalable Font) commands in ZPL II Programming Guide Volume One .

## Bitmapped Fonts

Internal bitmapped fonts can be magnified from 2 to 10 times their normal (default) size. The magnification factor is in whole numbers. Therefore, if the normal size of a bitmapped font is 9 dots high and 5 dots wide, a magnification factor of 3 would produce a character of 27 dots high and 15 dots wide. Height and width can be magnified independently.

## Magnification Factor

The font commands contain parameters for entering the height and width of printed characters. The values are always entered in dots. When entering these values for bitmapped fonts, use the following formula:

Base Height x Magnification Factor = Height Parameter Value

The same principle applies when calculating width.

Example:

Base height = 9 dots

```
Base width = 5 dots
```

To magnify a bitmapped character with the above specifics 3 times its size:

Height parameter = 27 [9 x 3]

Width parameter = 15 [5 x 3]

## Changing Bitmapped Font Size

Alphanumeric field command ( ^A ) parameters h and w control the magnification and, therefore, the ultimate size of the font. The parameter is specified in dots, but ZPL II actually uses an integer multiplier times the original height/width of the font. For example, if you specify

<!-- formula-not-decoded -->

you get characters three times their normal size (54 dots high), but if you specify

```
^AD,52
```

you receive the same result, not characters 52 dots high.

Defining only the height or width of a bitmapped font forces the magnification to be proportional to the parameter defined. If neither is defined, the ^CF height and width are used. For example, if the height is twice the standard height, the width will be twice the standard width.

If a ^CF command, with height and width parameters defined, is used to set the first font, any ^A commands (to select a different font) that follow must have the height and width parameter filled in.

If this is not done, the newly selected font will be magnified using values for the ^CF height and width parameters. The following is an example of what happens.

```
"F050,50"CFD,26.10^FDZEBRA....^FS "FO50.200"AA"FD2EBRA.-..^FS "F050,25o*FD"Bar Code.Bar None *2
```

```
"Bar Code, Bar None 1一 ZEBRA. Bar Code， Bar None
```

<!-- image -->

## Font Matrices

Type Key U = Uppercase, L = Lowercase, D = Descenders

## 6 dot/mm printhead

| Font   | Matrix           | Type   | Character Size   | Character Size   | Character Size   | Character Size   |
|--------|------------------|--------|------------------|------------------|------------------|------------------|
| Font   | HxW (in dots)    |        | HxW (in in.)     | Char./in.        | HxW (in mm)      | Char. /mm        |
| A      | 9 x 5            | U-L-D  | 0.059 x 0.039    | 25.4             | 1.50 x 0.99      | 1.01             |
| B      | 11 x 17          | U      | 0.072 x 0.059    | 16.9             | 1.82 x 1.50      | 0.066            |
| C, D   | 18 x 10          | U-L-D  | 0.118 x 0.079    | 12.7             | 2.99 x 2.00      | 0.05             |
| E      | 21 x 10          | OCR-B  | 0.138 x 0.085    | 11.7             | 3.50 x 2.16      | 0.46             |
| F      | 26 x 13          | U-L-D  | 0.170 x 0.105    | 9.53             | 4.32 x 2.67      | 0.37             |
| G      | 60 x 40          | U-L-D  | 0.394 x 0.315    | 3.18             | 10.0 x 8.00      | 0.125            |
| H      | 17 x 11          | OCR-A  | 0.111 x 0.098    | 10.2             | 2.81 x 2.48      | 0.40             |
| GS     | 24 x 24          | SYMBOL | 0.157 x 0.157    | 6.35             | 3.98 x 3.98      | 0.251            |
| 0      | Default: 15 x 12 |        |                  |                  |                  |                  |

## 8 dot/mm (203 dpi) printhead

| Font   | Matrix           | Type   | Character Size   | Character Size   | Character Size   | Character Size   |
|--------|------------------|--------|------------------|------------------|------------------|------------------|
| Font   | HxW (in dots)    |        | HxW (in in.)     | Char./in.        | HxW (in mm)      | Char. /mm        |
| A      | 9 X 5            | U-L-D  | 0.044 x 0.030    | 33.3             | 1.12 x 0.76      | 1.31             |
| B      | 11 X 17          | U      | 0.054 x 0.044    | 22.7             | 1.37 x 1.12      | 0.89             |
| C, D   | 18 X 10          | U-L-D  | 0.089 x 0.059    | 16.9             | 2.26 x 1.12      | 0.66             |
| E      | 28 x 15          | OCR-B  | 0.138 x 0.098    | 10.2             | 3.50 x 2.49      | 0.40             |
| F      | 26 x 13          | U-L-D  | 0.128 x 0.079    | 12.7             | 3.25 x 2.00      | 0.50             |
| G      | 60 x 40          | U-L-D  | 0.295 x 0.197    | 4.2              | 7.49 x 5.00      | 0.167            |
| H      | 21 x 13          | OCR-A  | 0.103 x 0.093    | 10.8             | 2.61 x 2.36      | 0.423            |
| GS     | 24 x 24          | SYMBOL | 0.118 x 0.118    | 8.5              | 2.99 x 2.99      | 0.334            |
| P      | 20 x 18          | U-L-D  | 0.098 x 0.089    | N/A              | 2.50 x 2.25      | N/A              |
| Q      | 28 x 24          | U-L-D  | 0.138 x 0.118    | N/A              | 3.50 x 3.00      | N/A              |
| R      | 35 x 31          | U-L-D  | 0.172 x 0.153    | N/A              | 4.38 x 3.88      | N/A              |
| S      | 40 x 35          | U-L-D  | 0.197 x 0.172    | N/A              | 5.00 x 4.38      | N/A              |
| T      | 48 x 42          | U-L-D  | 0.236 x 0.207    | N/A              | 6.00 x 5.25      | N/A              |
| U      | 59 x 53          | U-L-D  | 0.290 x 0.261    | N/A              | 7.38 x 6.63      | N/A              |
| V      | 80 x 71          | U-L-D  | 0.394 x 0.349    | N/A              | 10.00 x 8.88     | N/A              |
| 0      | Default: 15 x 12 | U-L-D  | Scalable         |                  | Scalable         |                  |

## 12 dot/mm (300 dpi) printhead

