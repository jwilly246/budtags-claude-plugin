<!-- Source: ZPL II Programming Guide Volume 1 -->
<!-- Section: Font Commands (^A) -->
<!-- Generated: 2025-11-02 04:52:35 -->

## Scalable/Bitmapped Font

Description The ^A command is a scalable/bitmapped font that uses built-in or TrueType ® fonts. ^A designates the font for the current ^FD statement or field. The font specified by ^A is used only once for that ^FD entry. If a value for ^A is not specified again, the default ^CF font is used for the next ^FD entry.

Format ^Afo,h,w

Important · Parameter f is required. If f is omitted it defaults to the last value of the ^CF command.

This table identifies the parameters for this format:

| Command                        | Details                                                                                                                                                                                                                                     |
|--------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| f = font name                  | Accepted Values: A through Z , and 1 to 9 Default Value: A Any font in the printer (downloaded, EPROM, stored fonts, fonts A through Z and 1 to 9 ).                                                                                        |
| o = font orientation           | Accepted Values: N = normal R = rotated 90 degrees (clockwise) I = inverted 180 degrees B = read from bottom up, 270 degrees Default Value: the last accepted ^FW value or the ^FW default                                                  |
| h = Character Height (in dots) | Scalable Accepted Values: 10 to 32000 Default Value: 15 or the last accepted ^CF value Bitmapped Accepted Values: multiples of height from 2 to 10 times the standard height, in increments of 1 Default Value: the last accepted ^CF value |
| w = width (in dots)            | Scalable Accepted Values: 10 to 32000 Default Value: 12 or last accepted ^CF value Bitmapped Accepted Values: multiples of width from 2 to 10 times the standard width, in increments of 1 Default Value: the last accepted ^CF value       |

<!-- image -->

<!-- image -->

## Scalable Font Command

Example · This is an example of a scalable font command:

## Bitmap Font Command

Example · This is an example of a bitmap font command:

<!-- image -->

Example · This is an example of the P - V fonts:

FONT V-A B C D 1 2 3 4 5 w x y z A B C D A B C D A B C D A B C D A B C D A B C D 1 2 3 4 5 1 2 3 4 5 1 2 3 4 5 1 2 3 4 5 1 2 3 4 5 1 2 3 4 5 12345 (Scalable) ABCDwxyz w x y z w x y z w x y z w x y z w x y z w x y z FONT U-FONT T-FONT S-FONT R-FONT Q-FONT P-FONT GS FONT 0 FONT G Az 4 - -----/c70/c79/c78/c84/c32/c69/c32/c45/c45/c32/c40/c79/c67/c82/c45/c66/c41/c32/c65/c66/c67/c68/c119/c120/c121/c122/c32/c49/c50/c51/c52/c53 /c70/c79/c78/c84 /c70/c79/c78/c84 /c70/c79/c78/c84 /c70/c79/c78/c84 /c70/c32/c45/c45 /c68/c32/c45/c45 /c66/c32/c45/c45 /c66/c32/c45/c45 /c65/c66/c67/c68 /c65/c66/c67/c68 /c65/c66/c67/c68 /c65/c66/c67/c68 /c49/c50/c51/c52/c53 /c49/c50/c51/c52/c53 /c49/c50/c51/c52/c53 /c49/c50/c51/c52/c53 /c119/c120/c121/c122 /c119/c120/c121/c122 /c87/c88/c89/c90 /c119/c120/c121/c122 /c70/c79/c78/c84/c32/c72/c32/c45/c45/c32/c40/c79/c67/c82/c45/c65/c41/c32/c85/c80/c80/c69/c82/c32/c67/c65/c83/c69/c32/c79/c78/c76/c89 C R

Comments Fonts are built using a matrix that defines standard height-to-width ratios. If you specify only the height or width value, the standard matrix for that font automatically determines the other value. If the value is not given or a 0 (zero) is entered, the height or width is determined by the standard font matrix.

## ^A@

## Use Font Name to Call Font

Description The ^A@ command uses the complete name of a font, rather than the character designation used in ^A . Once a value for ^A@ is defined, it represents that font until a new font name is specified by ^A@ .

Format

^A@o,h,w,d:o.x

This table identifies the parameters for this format:

| Parameters                     | Details                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
|--------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| o = font orientation           | Accepted Values: N = normal R = rotated 90 degrees (clockwise) I = inverted 180 degrees B = read from bottom up, 270 degrees Default Value: N or the last ^FW value                                                                                                                                                                                                                                                                                               |
| h = character height (in dots) | Default Value: magnification specified by w (character width) or the last accepted ^CF value. The base height is used if none is specified. Scalable the value is the height in dots of the entire character block. Magnification factors are unnecessary, because characters are scaled. Bitmapped the value is rounded to the nearest integer multiple of the font's base height, then divided by the font's base height to give a magnification nearest limit. |
| w = width (in dots)            | Default Value: magnification specified by h (height) or the last accepted ^CF value. The base width is used if none is specified. Scalable the value is the width in dots of the entire character block. Magnification factors are unnecessary, because characters are scaled. Bitmapped the value is rounded to the nearest integer multiple of the font's base width, then divided by the font's base width to give a magnification nearest limit.              |
| d = drive location of font     | Accepted Values: R: , E: , B: , and A: Default Value: R :                                                                                                                                                                                                                                                                                                                                                                                                         |
| o = font name                  | Accepted Values: any valid font Default Value: if an invalid or no name is entered, the default set by ^CF is used. If no font has been specified in ^CF , font A is used. The font named carries over on all subsequent ^A@ commands without a font name.                                                                                                                                                                                                        |
| x = extension                  | Fixed Value: .FNT                                                                                                                                                                                                                                                                                                                                                                                                                                                 |

<!-- image -->

<!-- image -->

Example · This example is followed by a table that identifies the called out lines of code:

<!-- image -->

|   1 | Starts the label format.                                                                                                                                                                |
|-----|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|   2 | Searches non-volatile printer memory ( B: ) for CYRI_UB.FNT. When the font is found, the ^A@ command sets the print orientation to normal and the character size to 50 dots by 50 dots. |
|   3 | Sets the field origin at 100,100.                                                                                                                                                       |
|   4 | Prints the field data, Zebra Printer Fonts on the label.                                                                                                                                |
|   5 | Calls the font again and character size is decreased to 40 dots by 40 dots.                                                                                                             |
|   6 | Sets the new field origin at 100,150.                                                                                                                                                   |
|   7 | Prints the field data, This uses the B:CYRI_UB.FNT on the label.                                                                                                                        |
|   8 | Ends the label format.                                                                                                                                                                  |

Comments For more information on scalable and bitmap fonts, see ZPL II Programming Guide Volume Two .

