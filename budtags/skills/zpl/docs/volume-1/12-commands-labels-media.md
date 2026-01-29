<!-- Source: ZPL II Programming Guide Volume 1 -->
<!-- Section: Label & Media Commands (^L*, ^M*) -->
<!-- Generated: 2025-11-02 04:52:35 -->


This table identifies the parameters for this format:

| Parameters                     | Details                                                                               |
|--------------------------------|---------------------------------------------------------------------------------------|
| w = box width (in dots)        | Accepted Values: value of t to 32000 Default Value: value used for thickness (t) or 1 |
| h = box height (in dots)       | Accepted Values: value of t to 32000 Default Value: value used for thickness (t) or 1 |
| t = border thickness (in dots) | Accepted Values: 1 to 32000 Default Value: 1                                          |
| c = line color                 | Accepted Values: B (black) or W (white) Default Value: B                              |
| r = degree of corner- rounding | Accepted Values: 0 (no rounding) to 8 (heaviest rounding) Default Value: 0            |

For the w and h parameters, keep in mind that printers have a default of 6, 8, 12, or 24 dots/millimeter. This comes out to 153, 203, 300, or 600 dots per inch. To determine the values for w and h, calculate the dimensions in millimeters and multiply by 6, 8, 12, or 24.

If the width and height are not specified, you get a solid box with its width and height as specified by value t .

The roundness-index is used to determine a rounding-radius for each box. Formula:

<!-- formula-not-decoded -->

where the shorter side is the lesser of the width and height (after adjusting for minimum and default values).

ZPL Commands

^GB

<!-- image -->

Examples · Here are a few examples of graphic boxes:

Width: 1.5 inch; Height: 1 inch; Thickness: 10; Color: default; Rounding: default

Width: 0 inch; Height: 1 inch; Thickness: 20; Color: default; Rounding: default:

Width: 1 inch; Height: 0 inch; Thickness: 30; Color: default; Rounding: default

Width: 1.5 inch; Height: 1 inch; Thickness: 10; Color: default; Rounding: 5

<!-- image -->

## ^GC

## Graphic Circle

Description The ^GC command produces a circle on the printed label. The command parameters specify the diameter (width) of the circle, outline thickness, and color. Thickness extends inward from the outline.

Format ^GCd,t, c

This table identifies the parameters for this format:

| Parameters                     | Details                                                                            |
|--------------------------------|------------------------------------------------------------------------------------|
| d = circle diameter (in dots)  | Accepted Values: 3 to 4095 (larger values are replaced with 4095) Default Value: 3 |
| t = border thickness (in dots) | Accepted Values: 2 to 4095 Default Value: 1                                        |
| c = line color                 | Accepted Values: B (black) or W (white) Default Value: B                           |

- Example · This is an example of how to create a circle on the printed label:

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

^GD

## Graphic Diagonal Line

Description The ^GD command produces a straight diagonal line on a label. This can be used in conjunction with other graphic commands to create a more complex figure.

Format ^GDw,h,t,c,o

This table identifies the parameters for this format:

| Parameters                                  | Details                                                                                              |
|---------------------------------------------|------------------------------------------------------------------------------------------------------|
| w = box width (in dots)                     | Accepted Values: 3 to 32000 Default Value: value of t (thickness) or 1                               |
| h = box height (in dots)                    | Accepted Values: 3 to 32000 Default Value: value of t (thickness) or 1                               |
| t = border thickness (in dots)              | Accepted Values: 1 to 32000 Default Value: 1                                                         |
| c = line color                              | Accepted Values: B (black) or W(white) Default Value: B                                              |
| o = orientation (direction of the diagonal) | Accepted Values: R (or /) = right-leaning diagonal L (or \) = left-leaning diagonal Default Value: R |

Example · This is an example of how to create a diagonal line connecting one corner with the opposite corner of a box on a printed label:

<!-- image -->

<!-- image -->

<!-- image -->

## ^GE

## Graphic Ellipse

Description The ^GE command produces an ellipse in the label format.

Format ^GEw,h,t,c

This table identifies the parameters for this format:

| Parameters                     | Details                                                                                                              |
|--------------------------------|----------------------------------------------------------------------------------------------------------------------|
| w = ellipse width (in dots)    | Accepted Values: 3 to 4095 (larger values are replaced with 4095) Default Value: value used for thickness ( t ) or 1 |
| h = ellipse height (in dots)   | Accepted Values: 3 to 4095 Default Value: value used for thickness ( t ) or 1                                        |
| t = border thickness (in dots) | Accepted Values: 2 to 4095 Default Value: 1                                                                          |
| c = line color                 | Accepted Values: B (black) or W(white) Default Value: B                                                              |

Example · This is an example of how to create a ellipse on a printed label:

<!-- image -->

<!-- image -->

<!-- image -->

^GF

## Graphic Field

Description The ^GF command allows you to download graphic field data directly into the printer's bitmap storage area. This command follows the conventions for any other field, meaning a field orientation is included. The graphic field data can be placed at any location within the bitmap space.

Format ^GFa,b,c,d,data

This table identifies the parameters for this format:

| Parameters              | Details                                                                                                                                                                                                                                                                                                                                                                                                          |
|-------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| a = compression type    | Accepted Values: A = ASCII hexadecimal (follows the format for other download commands) B = binary (data sent after the c parameter is strictly binary) C = compressed binary (data sent after the c parameter is in compressed binary format. The data is compressed on the host side using Zebra's compression algorithm. The data is then decompressed and placed directly into the bitmap.) Default Value: A |
| b = binary byte count   | Accepted Values: 1 to 99999 This is the total number of bytes to be transmitted for the total image or the total number of bytes that follow parameter d . For ASCII download, the parameter should match parameter c . Out-of-range values are set to the nearest limit. Default Value: command is ignored if a value is not specified                                                                          |
| c = graphic field count | Accepted Values: 1 to 99999 This is the total number of bytes comprising the graphic format (width x height), which is sent as parameter d . Count divided by bytes per row gives the number of lines in the image. This number represents the size of the image, not necessarily the size of the data stream (see d ). Default Value: command is ignored if a value is not specified                            |

<!-- image -->

<!-- image -->

| Parameters        | Details                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
|-------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| d = bytes per row | Accepted Values: 1 to 99999 This is the number of bytes in the downloaded data that comprise one row of the image. Default Value: command is ignored if a value is not specified                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| data = data       | Accepted Values: ASCII hexadecimal data: 00 to FF Astring of ASCII hexadecimal numbers, two digits per image byte. CRand LF can be inserted as needed for readability. The number of two-digit number pairs must match the above count. Any numbers sent after count is satisfied are ignored. A comma in the data pads the current line with 00 (white space), minimizing the data sent. ~DN or any caret or tilde character prematurely aborts the download. Binary data: Strictly binary data is sent from the host. All control prefixes are ignored until the total number of bytes needed for the graphic format is sent. |

Example · This example downloads 8,000 total bytes of data and places the graphic data at location 100,100 of the bitmap. The data sent to the printer is in ASCII form.

^FO100,100^GFA,8000,8000,80,ASCII data

- Example · This example downloads 8,000 total bytes of data and places the graphic data at location 100,100 of the bitmap. The data sent to the printer is in binary form.

^FO100,100^GFB,8000,8000,80,Binary data

<!-- image -->

<!-- image -->

## ^GS

## Graphic Symbol

Description The ^GS command enables you to generate the registered trademark, copyright symbol, and other symbols.

Format ^GSo,h,w

This table identifies the parameters for this format:

| Parameters                                           | Details                                                                                                                                            |
|------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------|
| o = font orientation                                 | Accepted Values: N = normal R = rotate 90 degrees clockwise I = inverted 180 degrees B = bottom-up, 270 degrees Default Value: N or last ^FW value |
| h = character height proportional to width (in dots) | Accepted Values: 0 to 32000 Default Value: last ^CF value                                                                                          |
| w = character width proportional to height (in dots) | Accepted Values: 0 to 32000 Default Value: last ^CF value                                                                                          |

<!-- image -->

Example · Use the ^GS command followed by ^FD and the appropriate character (A through E) within the field data to generate the desired character:

PROGRAMMING

ZEBRAF

LANGUAGE II（ZPL I I TM )

- A=? (Registered Trade Mark)
- B =@ (Copyright)
- C = TM (Trade Mark)
- D= (Underw riters Laboratories approval)

E= (Canadian Standards Association approval)

<!-- image -->

<!-- image -->

~HB

## Battery Status

Description When the ~HB command is sent to the printer, a data string is sent back to the host. The string starts with an &lt;STX&gt; control code sequence and terminates by an &lt;ETX&gt;&lt;CR&gt;&lt;LF&gt; control code sequence.

Format ~HB

Parameters: when the printer receives the command, it returns:

&lt;STX&gt;bb.bb,hh.hh,bt&lt;ETX&gt;&lt;CR&gt;&lt;LF&gt;

| <STX>   | =   | ASCII start-of-text character                           |
|---------|-----|---------------------------------------------------------|
| bb.bb   | =   | current battery voltage reading to the nearest 1/4 volt |
| hh.hh   | =   | current head voltage reading to the nearest 1/4 volt    |
| bt      | =   | battery temperature in Celsius                          |
| <ETX>   | =   | ASCII end-of-text character                             |
| <CR>    | =   | ASCII carriage return                                   |
| <LF>    | =   | ASCII line feed character                               |

Comments This command is used for the power-supply battery of the printer and should not be confused with the battery backed-up RAM.

<!-- image -->

~HD

## Head Temperature Information

Description The ~HD command echoes printer status information that includes the power supply and head temperature using the terminal emulator.

Format ~HD

Example · This is an example of the ~HD command:

```
Head Temp = 29 Ambient Temp = Q0 Head Test = Passed Darkness Adjust = 23 Print Speed= 2 Slew Speed = 6 Backfeed Speed = 2 Static_pitch_length = 0521 Dynamic_pitch_length = @540 Max_dynamic_pitch_length = 0540 Min_dynamic_pitch_length = 0537 COMMAND PFX = FORMAT PFX =^:DELIMITER = P30 INTERFACE =None P31 INTERFACE = None P32 INTERFACE = Front Panel Revision 5 P33 INTERFACE = Hone P34 INTERFACE = None P35 INTERFACE = None Dynamic_top_position = @o08 No ribbon A/D = 0000
```

<!-- image -->

<!-- image -->

<!-- image -->

## ^HF

## Graphic Symbol

Description The ^HF command sends an object of ZPL format instructions to the host, in ~DF.

Format ^HF,o,h,w

This table identifies the parameters for this format:

| Parameters                                           | Details                                                                                                                        |
|------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------|
| o = font orientation                                 | Accepted Values: N = normal R = rotate I = inverted 180 degrees B = bottom-up, 270 degrees Default Value: N or last ^FW value. |
| h = character height proportional to width (in dots) | Accepted Value: 0 to 32000 Default Value: last ^CF value                                                                       |
| w = character width proportional to height (in dots) | Accepted Value: 0 to 32000 Default Value: last ^CF value                                                                       |

<!-- image -->

