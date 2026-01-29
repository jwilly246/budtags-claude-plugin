<!-- Source: ZPL II Programming Guide Volume 1 -->
<!-- Section: Image Commands (^I*) -->
<!-- Generated: 2025-11-02 04:52:35 -->

| Parameters         | Details                                                                                                                                                                                                         |
|--------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| d = font location  | Accepted Values: R: , E: , B: , and A: Default Value: R:                                                                                                                                                        |
| o = font name      | Accepted Values: 1 to 8 alphanumeric characters Default Value: if a name is not specified, UNKNOWN is used                                                                                                      |
| x = extension      | Fixed Value: .FNT                                                                                                                                                                                               |
| s = font size      | Accepted Values: the number of memory bytes required to hold the Zebra-downloadable format of the font Default Value: if no data is entered, the command is ignored                                             |
| data = data string | Accepted Values: a string of ASCII hexadecimal values (two hexadecimal digits/byte). The total number of two-digit values must match parameter s . Default Value: if no data is entered, the command is ignored |

Example · This is an example of how to download an unbounded true type font:

~DUR:KANJI,86753,60CA017B0CE7...

(86753 two-digit hexadecimal values)

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

## ~DY

## Download Graphics

Description The ~DY command downloads to the printer graphic objects in any supported format. This command can be used in place of ~DG for more saving and loading options.

Format ~DYd:f,b,x,t,w,data

This table identifies the parameters for this format:

| Parameters                              | Details                                                                                                                                                                                                                                                                             |
|-----------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| d = file location                       | Accepted Values: R: , E: , B: , and A: Default Value: R:                                                                                                                                                                                                                            |
| f = file name                           | Accepted Values: 1 to 8 alphanumeric characters Default Value: if a name is not specified, UNKNOWN is used                                                                                                                                                                          |
| b = format downloaded in data field (f) | Accepted Values: A = uncompressed bitmap ( .GRF , ASCII) B = uncompressed bitmap ( .GRF , binary) C = AR-compressed bitmap ( .GRF , compressed binary- used only by Zebra's BAR-ONE ® v5) P = PNG image ( .PNG ) Default Value: a value must be specified                           |
| x = extension of stored file            | Accepted Values: G = raw bitmap ( .GRF ) P = store as compressed ( .PNG ) Default Value: .GRF , unless parameter b is set to P ( .PNG )                                                                                                                                             |
| t = total number of bytes in file       | .GRF images: the size after decompression into memory .PNG images: the size of the .PNG file                                                                                                                                                                                        |
| w = total number of bytes per row       | .GRF images: number of bytes per row .PNG images: value ignored-data is encoded directly into .PNG data                                                                                                                                                                             |
| data = data                             | ASCII hexadecimal encoding, ZB64, or binary data, depending on b . a, p = ASCII hexadecimal or ZB64 b, c = binary When binary data is sent, all control prefixes and flow control characters are ignored until the total number of bytes needed for the graphic format is received. |

Comments For more information on ZB64 encoding and compression, see ZPL II Programming Guide Volume Two .

~EG

## Erase Download Graphics

See ^ID on page 177.

ZPL Commands

~EG

<!-- image -->

^FB

## Field Block

Description The ^FB command allows you to print text into a defined block type format. This command formats an ^FD or ^SN string into a block of text using the origin, font, and rotation specified for the text string. The ^FB command also contains an automatic word-wrap function.

Format ^FBa,b,c,d,e

This table identifies the parameters for this format:

| Parameters                                                     | Details                                                                                                                                                                                             |
|----------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| a = width of text block line (in dots)                         | Accepted Values: 0 to the width of the label (or 9999 ) Default Value: 0 If the value is less than font width or not specified, text does not print.                                                |
| b = maximumnumber of lines in text block                       | Accepted Values: 1 to 9999 Default Value: 1 Text exceeding the maximum number of lines overwrites the last line. Changing the font size automatically increases or decreases the size of the block. |
| c = add or delete space between lines (in dots)                | Accepted Values: -9999 to 9999 Default Value: 0 Numbers are considered to be positive unless preceded by a minus sign. Positive values add space; negative values delete space.                     |
| d = text justification                                         | Accepted Values: L (left), C (center), R (right), J (justified) Default Value: L Last line is left-justified if J is used.                                                                          |
| e = hanging indent (in dots) of the second and remaining lines | Accepted Values: 0 to 9999 Default Value: 0                                                                                                                                                         |

<!-- image -->

Example · These are examples of how the ^FB command affects field data.

## Comments on the ^FB Command

```
This scheme can be used to facilitate special functions: \& = carriage return/line feed \(*) = soft hyphen (word break with a dash) \\ = backslash (\)
```

Item 1: ^CI13 must be selected to print a backslash (\).

Item 2: If a soft hyphen is placed near the end of a line, the hyphen is printed. If it is not placed near the end of the line, it is ignored.

```
(*) = any alphanumeric character
```

- If a word is too long to print on one line by itself (and no soft hyphen is specified), a hyphen is automatically placed in the word at the right edge of the block. The remainder of the word is on the next line. The position of the hyphen depends on word length, not a syllable boundary. Use a soft hyphen within a word to control where the hyphenation occurs.
- Maximum data-string length is 3K, including control characters, carriage returns, and line feeds.
- Normal carriage returns, line feeds, and word spaces at line breaks are discarded.
- When using ^FT (Field Typeset), ^FT uses the baseline origin of the last possible line of text. Increasing the font size causes the text block to increase in size from bottom to top. This could cause a label to print past its top margin.
- When using ^FO (Field Origin), increasing the font size causes the text block to increase in size from top to bottom.
- If ^SN is used instead of ^FD , the field does not print.
- ^FS terminates an ^FB command. Each block requires its own ^FB command.

<!-- image -->

<!-- image -->

## ^FC

## Field Clock (for Real-Time Clock)

Description The ^FC command is used to set the clock-indicators (delimiters) and the clock mode for use with the Real-Time Clock hardware. This command must be included within each label field command string each time the Real-Time Clock values are required within the field.

Format ^FCa,b,c

This table identifies the parameters for this format:

| Parameters                              | Details                                                                                          |
|-----------------------------------------|--------------------------------------------------------------------------------------------------|
| a = primary clock indicator character   | Accepted Values: any ASCII character Default Value: %                                            |
| b = secondary clock indicator character | Accepted Values: any ASCII character Default Value: none-this value cannot be the same as a or c |
| c = third clock indicator character     | Accepted Values: any ASCII character Default Value: none-this value cannot be the same as a or b |

Example · Entering these ZPL sets the primary clock indicator to %, the secondary clock indicator to {, and the third clock indicator to #. The results are printed on a label with Primary, Secondary, and Third as field data.

<!-- image -->

## GENERATED LABEL

Comments The ^FC command is ignored if the Real-Time Clock hardware is not present.

For more details on the Real Time Clock, see the Zebra Real Time Clock Guide .

<!-- image -->

<!-- image -->

## ^FD

## Field Data

Description The ^FD command defines the data string for the field. The field data can be any printable character except those used as command prefixes ( ^ and ~ ).

Format ^FDa

This table identifies the parameters for this format:

| Parameters             | Details                                                                                                            |
|------------------------|--------------------------------------------------------------------------------------------------------------------|
| a = data to be printed | Accepted Values: any ASCII string up to 3072 characters Default Value: none-a string of characters must be entered |

Comments The ^ and ~ characters can be printed by changing the prefix characters-see the ^CD ~CD on page 106 and ^CT ~CT on page 115 commands. The new prefix characters cannot be printed.

Characters with codes above 127, or the ^ and ~ characters, can be printed using the ^FH and ^FD commands.

- ^CI13 must be selected to print a backslash (\).

<!-- image -->

<!-- image -->

## ^FH

## Field Hexadecimal Indicator

Description The ^FH command allows you to enter the hexadecimal value for any character directly into the ^FD statement. The ^FH command must precede each ^FD command that uses hexadecimals in its field.

Within the ^FD statement, the hexadecimal indicator must precede each hexadecimal value. The default hexadecimal indicator is \_ (underscore). There must be a minimum of two characters designated to follow the underscore. The a parameter can be added when a different hexadecimal indicator is needed.

This command can be used with any of the commands that have field data (that is ^FD , ^FV (Field Variable), and ^SN (Serialized Data)).

Valid hexadecimal characters are:

<!-- image -->

## Format ^FHa

This table identifies the parameters for this format:

| Parameters                | Details                                                                                                                    |
|---------------------------|----------------------------------------------------------------------------------------------------------------------------|
| a = hexadecimal indicator | Accepted Values: any character except current format and control prefix (^ and ~ by default) Default Value: _ (underscore) |

Example · This is an example of how to enter a hexadecimal value directly into a ^FD statement:

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

## ^FM

## Multiple Field Origin Locations

Description The ^FM command allows you to control the placement of bar code symbols.

It designates field locations for the PDF417 ( ^B7 ) and Micro-PDF417 ( ^BF ) bar codes when the structured append capabilities are used. This allows printing multiple bar codes from the same set of text information.

The structured append capability is a way of extending the text printing capacity of both bar codes. If a string extends beyond what the data limitations of the bar code are, it can be printed as a series: 1 of 3, 2 of 3, 3 of 3. Scanners read the information and reconcile it into the original, unsegmented text.

The ^FM command triggers multiple bar code printing on the same label with ^B7 and ^BF only. When used with any other commands, it is ignored.

<!-- formula-not-decoded -->

This table identifies the parameters for this format:

| Parameters   | Parameters                                   | Details                                                                                                      |
|--------------|----------------------------------------------|--------------------------------------------------------------------------------------------------------------|
| x1           | = x-axis location of first symbol (in dots)  | Accepted Values: 0 to 32000 e = exclude this bar code from printing Default Value: a value must be specified |
| y1           | = y-axis location of first symbol (in dots)  | Accepted Values: 0 to 32000 e = exclude this bar code from printing Default Value: a value must be specified |
| x2           | = x-axis location of second symbol (in dots) | Accepted Values: 0 to 32000 e = exclude this bar code from printing Default Value: a value must be specified |
| y2           | = y-axis location of second symbol (in dots) | Accepted Values: 0 to 32000 e = exclude this bar code from printing Default Value: a value must be specified |
| …            | = continuation of X,Y pairs                  | Maximum number of pairs: 60                                                                                  |

<!-- image -->

<!-- image -->

<!-- image -->

Example · This example assumes a maximum of three bar codes:

<!-- image -->

Example · This example assumes a maximum of three bar codes, with bar code 2 of 3 omitted:

<!-- image -->

<!-- image -->

If e is entered for any of the x, y values, the bar code does not print.

Example · Symbol 2 of 3 in this example is still excluded:

<!-- image -->

<!-- image -->

Comments Subsequent bar codes print once the data limitations of the previous bar code have been exceeded. For example, bar code 2 of 3 prints once 1 of 3 has reached the maximum amount of data it can hold. Specifying three fields does not ensure that three bar codes print; enough field data to fill three bar code fields has to be provided.

The number of the x,y pairs can exceed the number of bar codes generated. However, if too few are designated, no symbols print.

<!-- image -->

## ^FN

## Field Number

Description The ^FN command numbers the data fields. This command is used in both ^DF (Store Format) and ^XF (Recall Format) commands.

In a stored format, use the ^FN command where you would normally use the ^FD (Field Data) command. In recalling the stored format, use ^FN in conjunction with the ^FD command.

## Format ^FN#
