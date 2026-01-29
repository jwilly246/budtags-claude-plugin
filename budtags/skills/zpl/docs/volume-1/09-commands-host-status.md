<!-- Source: ZPL II Programming Guide Volume 1 -->
<!-- Section: Host & Status Commands (^H*, ~H*) -->
<!-- Generated: 2025-11-02 04:52:35 -->


<!-- image -->

<!-- image -->

~DB

## Download Bitmap Font

Description The ~DB command sets the printer to receive a downloaded bitmap font and defines native cell size, baseline, space size, and copyright.

This command consists of two portions, a ZPL II command defining the font and a structured data segment that defines each character of the font.

Format ~DBd:o.x,a,h,w,base,space,#char,',data

This table identifies the parameters for this format:

| Parameters                                         | Details                                                                                                         |
|----------------------------------------------------|-----------------------------------------------------------------------------------------------------------------|
| d = drive to store font                            | Accepted Values: R: , E: , B: , and A: Default Value: R:                                                        |
| o = name of font                                   | Accepted Values: 1 to 8 alphanumeric characters Default Value: if a name is not specified, UNKNOWN is used      |
| x = extension                                      | Fixed Value: .FNT                                                                                               |
| a = orientation of native font                     | Fixed Value: normal                                                                                             |
| h = maximum height of cell (in dots)               | Accepted Values: 0 to 32000 Default Value: a value must be specified                                            |
| w = maximum width of cell (in dots)                | Accepted Values: 0 to 32000 Default Value: a value must be specified                                            |
| base = dots from top of cell to character baseline | Accepted Values: 0 to 32000 Default Value: a value must be specified                                            |
| space = width of space or non-existent characters  | Accepted Values: 0 to 32000 Default Value: a value must be specified                                            |
| #char = number of characters in font               | Accepted Values: 1 to 256 (must match the characters being downloaded) Default Value: a value must be specified |

<!-- image -->

| Parameters                                                           | Details                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
|----------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| ' = copyright holder                                                 | Accepted Values: 1 to 63 alphanumeric characters Default Value: a value must be specified                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| data = structured ASCII data that defines each character in the font | The # symbol signifies character code parameters, which are separated with periods. The character code is from 1 to 4 characters to allow for large international character sets to be downloaded to the printer. The data structure is: #xxxx.h.w.x.y.i.data #xxxx = character code h = bitmap height (in dot rows) w = bitmap width (in dot rows) x = x-offset (in dots) y = y-offset (in dots) i = typesetting motion displacement (width, including inter character gap of a particular character in the font) data = hexadecimal bitmap description |

Example · This is an example of how to use the ~DB command. It shows the first two characters of a font being downloaded to DRAM.

```
~DBR:TIMES.FNT,N,5,24,3,10,2,ZEBRA 1992, #0025.5.16.2.5.18. OOFF OOFF FFOO FFOO FFFF #0037.4.24.3.6.26. OOFFOO OFOOFO OFOOFO OOFFOO
```

<!-- image -->

<!-- image -->

~DE

## Download Encoding

Description The standard encoding for TrueType Windows® fonts is always Unicode. The ZPL II field data must be converted from some other encoding to Unicode that the Zebra printer understands. The required translation tables are provided with ZTools and downloaded with the ~DE command.

Format ~DEd:o.x,s,data

This table identifies the parameters for this format:

| Parameters            | Details                                                                                                                                                                                    |
|-----------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| d = location of table | Accepted Values: R: , E: , B: , and A: Default Value: R:                                                                                                                                   |
| o = name of table     | Accepted Values: any valid name, up to 8 characters Default Value: if a name is not specified, UNKNOWN is used                                                                             |
| x = extension         | Fixed Value: .DAT                                                                                                                                                                          |
| s = table size        | Accepted Values: the number of memory bytes required to hold the Zebra downloadable format of the font Default Value: if an incorrect value or no value is entered, the command is ignored |
| data = data string    | Accepted Values: a string of ASCII hexadecimal values Default Value: if no data is entered, the command is ignored                                                                         |

Example · This is an example of how to download the required translation table:

~DER:JIS.DAT,27848,300021213001...

(27848 two-digit hexadecimal values)

Comments For more information on ZTools, see the program documentation included with the software.

<!-- image -->

## ^DF

## Download Format

Description The ^DF command saves ZPL II format commands as text strings to be later merged using ^XF with variable data. The format to be stored might contain field number ( ^FN ) commands to be referenced when recalled.

While use of stored formats reduces transmission time, no formatting time is saved-this command saves ZPL II as text strings formatted at print time.

Enter the ^DF stored format command immediately after the ^XA command, then enter the format commands to be saved.

Format ^DFd:o.x

This table identifies the parameters for this format:

| Parameters                | Details                                                                                                    |
|---------------------------|------------------------------------------------------------------------------------------------------------|
| d = device to store image | Accepted Value: R: , E: , B: , and A: Default Value: R:                                                    |
| o = image name            | Accepted Values: 1 to 8 alphanumeric characters Default Value: if a name is not specified, UNKNOWN is used |
| x = extension             | Fixed Value: .ZPL                                                                                          |

<!-- image -->

<!-- image -->

## ~DG

## Download Graphics

Description The ~DG command downloads an ASCII Hex representation of a graphic image. If .GRF is not the specified file extension, .GRF is automatically appended.

For more saving and loading options when downloading files, see ~DY on page 130.

Format ~DGd:o.x,t,w,data

This table identifies the parameters for this format:

| Parameters                                     | Details                                                                                                                                                |
|------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------|
| d = device to store image                      | Accepted Values: R: , E: , B: , and A: Default Value: R:                                                                                               |
| o = image name                                 | Accepted Values: 1 to 8 alphanumeric characters Default Value: if a name is not specified, UNKNOWN is used                                             |
| x = extension                                  | Fixed Value: .GRF                                                                                                                                      |
| t = total number of bytes in graphic           | See the formula in the examples below.                                                                                                                 |
| w = number of bytes per row                    | See the formula in the examples below.                                                                                                                 |
| data = ASCII hexadecimal string defining image | The data string defines the image and is an ASCII hexadecimal representation of the image. Each character represents a horizontal nibble of four dots. |

This is the key for the examples that follow:

x = width of the graphic in millimeters y = height of the graphic in millimeters

z = dots/mm = print density of the printer being programmed

8 = bits/byte

- Examples · These are some example related to the ~DG command:

To determine the t parameter use this formula:

<!-- formula-not-decoded -->

To determine the correct t parameter for a graphic 8 mm wide, 16 mm high, and a print density of 8 dots/mm, use this formula:

⎛

⎞

<!-- formula-not-decoded -->

## Raise any portion of a byte to the next whole byte.

To determine the w parameter (the width in terms of bytes per row) use this formula :

⎛

<!-- formula-not-decoded -->

To determine the correct w parameter for a graphic 8 mm wide and a print density of 8 dots/mm, use this formula:

⎛

<!-- formula-not-decoded -->

## Raise any portion of a byte to the next whole byte.

Parameter w is the first value in the t calculation.

The data parameter is a string of hexadecimal numbers sent as a representation of the graphic image. Each hexadecimal character represents a horizontal nibble of four dots. For example, if the first four dots of the graphic image are white and the next four black, the dot-by-dot binary code is 00001111. The hexadecimal representation of this binary value is 0F. The entire graphic image is coded in this way, and the complete graphic image is sent as one continuous string of hexadecimal values.

Comments Do not use spaces or periods when naming your graphics. Always use different names for different graphics.

If two graphics with the same name are sent to the printer, the first graphic is erased and replaced by the second graphic.

<!-- image -->

<!-- image -->

~DN

## Abort Download Graphic

Description After decoding and printing the number of bytes in parameter t of the ~DG command, the printer returns to normal Print Mode. Graphics Mode can be aborted and normal printer operation resumed by using the ~DN command.

Format ~DN

Comments If you need to stop a graphic from downloading, you should abort the transmission from the host device. To clear the ~DG command, however, you must send a ~DN command.

## ~DS

## Download Scalable Font

Description The ~DS command is used to set the printer to receive a downloadable scalable font and defines the size of the font in bytes. ~DS is used for downloading Intellifont data to the printer. For downloading TrueType fonts, see ~DT on page 128.

The ~DS command, and its associated parameters, is the result of converting a vendorsupplied font for use on a Zebra printer. To convert this font use the ZTools utility.

Format ~DSd:o.x,s,data

This table identifies the parameters for this format:

| Parameters                                        | Details                                                                                                    |
|---------------------------------------------------|------------------------------------------------------------------------------------------------------------|
| d = device to store image                         | Accepted Values: R: , E: , B: , and A: Default Value: R:                                                   |
| o = image name                                    | Accepted Values: 1 to 8 alphanumeric characters Default Value: if a name is not specified, UNKNOWN is used |
| x = extension                                     | Fixed Value: .FNT                                                                                          |
| s = size of font in bytes                         | Fixed Value: this number is generated by ZTools and should not be changed                                  |
| data = ASCII hexadecimal string that defines font | Fixed Value: this number is generated by ZTools and should not be changed                                  |

Example · This example shows the first three lines of a scalable font that was converted using the ZTools program and is ready to be downloaded to the printer. If necessary, the destination and object name can be changed.

~DSB:CGTIMES.FNT,37080, OOFFOOFFOOFFOOFF

FFOAECB28FFFOOFF

Comments Downloaded scalable fonts are not checked for integrity. If they are corrupt, they cause unpredictable results at the printer.

<!-- image -->

<!-- image -->

<!-- image -->

## ~DT

## Download TrueType Font

Description Use ZTools to convert a TrueType font to a Zebra-downloadable format. ZTools creates a downloadable file that includes a ~DT command. For information on converting and downloading Intellifont information, see the ~DS command on page 127.

Format ~DTd:o.x,s,data

This table identifies the parameters for this format:

| Parameters         | Details                                                                                                                                                                                                         |
|--------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| d = font location  | Accepted Values: R: , E: , B: , and A: Default Value: R:                                                                                                                                                        |
| o = font name      | Accepted Values: any valid TrueType name, up to 8 characters Default Value: if a name is not specified, UNKNOWN is used                                                                                         |
| x = extension      | Fixed Value: .DAT                                                                                                                                                                                               |
| s = font size      | Accepted Values: the number of memory bytes required to hold the Zebra-downloadable format of the font Default Value: if an incorrect value or no value is entered, the command is ignored                      |
| data = data string | Accepted Values: a string of ASCII hexadecimal values (two hexadecimal digits/byte). The total number of two-digit values must match parameter s . Default Value: if no data is entered, the command is ignored |

Example · This is an example of how to download a true type font:

~DTR:FONT,52010,00AF01B0C65E...

(52010 two-digit hexadecimal values)

<!-- image -->

<!-- image -->

## ~DU

## Download Unbounded TrueType Font

Description Some international fonts, such as Asian fonts, have more than 256 printable characters. These fonts are supported as large TrueType fonts and are downloaded to the printer with the ~DU command. Use ZTools to convert the large TrueType fonts to a Zebra-downloadable format.

The Field Block ( ^FB ) command cannot support the large TrueType fonts.

Format ~DUd:o.x,s,data

This table identifies the parameters for this format:

