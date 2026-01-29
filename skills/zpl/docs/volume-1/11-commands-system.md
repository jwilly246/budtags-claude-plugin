<!-- Source: ZPL II Programming Guide Volume 1 -->
<!-- Section: System & Job Commands (^J*, ~J*) -->
<!-- Generated: 2025-11-02 04:52:35 -->


This table identifies the parameters for this format:

| Parameters                             | Details                                     |
|----------------------------------------|---------------------------------------------|
| # = number to be assigned to the field | Accepted Values: 0 to 9999 Default Value: 0 |

Example · This example recalls the format ( ^XF ) saved with ^DF and inserts field number data.

<!-- image -->

## Comments

- The same ^FN value can be stored with several different fields.
- If a label format contains a field with ^FN and ^FD , the data in that field prints for any other field containing the same ^FN value.

<!-- image -->

<!-- image -->

<!-- image -->

## ^FO

## Field Origin

Description The ^FO command sets a field origin, relative to the label home ( ^LH ) position. ^FO sets the upper-left corner of the field area by defining points along the x-axis and y-axis independent of the rotation.

Format ^FOx,y

This table identifies the parameters for this format:

| Parameters                    | Details                                      |
|-------------------------------|----------------------------------------------|
| x = x-axis location (in dots) | Accepted Values: 0 to 32000 Default Value: 0 |
| y = y-axis location (in dots) | Accepted Values: 0 to 32000 Default Value: 0 |

Comments If the value entered for the x or y parameter is too high, it could position the field origin completely off the label.

For examples of code and generated labels using the ^FO command, see ^FT on page 144.

<!-- image -->

## ^FP

## Field Parameter

Description The ^FP command allows vertical formatting of the font field, commonly used for printing Asian fonts.

Format ^FPd,g

This table identifies the parameters for this format:

| Parameters                                   | Details                                                                                                                                              |
|----------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------|
| d = direction                                | Accepted Values: H = horizontal printing (left to right) V = vertical printing (top to bottom) R = reverse printing (right to left) Default Value: H |
| g = additional inter-character gap (in dots) | Accepted Values: 0 to 9999 Default Value: 0 if no value is entered                                                                                   |

## Example · This is an example of how to implement reverse and vertical print:

<!-- image -->

Comments When using reverse printing, the origin specified in ^FT is the lower- left corner of the right-most text character.

<!-- image -->

^FR

## Field Reverse Print

Description The ^FR command allows a field to appear as white over black or black over white. When printing a field and the ^FR command has been used, the color of the output is the reverse of its background.

Format ^FR

Example · In this example, the ^GB command creates areas of black allowing the printing to appear white:

<!-- image -->

<!-- image -->

Comments The ^FR command applies to only one field and has to be specified each time. When multiple ^FR commands are going to be used, it might be more convenient to use the ^LR command.

<!-- image -->

## ^FS

## Field Separator

Description The ^FS command denotes the end of the field definition. Alternatively, ^FS command can also be issued as a single ASCII control code SI (Control-O, hexadecimal 0F).

Format ^FS

<!-- image -->

<!-- image -->

## ^FT

## Field Typeset

Description The ^FT command also sets the field position, relative to the home position of the label designated by the ^LH command. The typesetting origin of the field is fixed with respect to the contents of the field and does not change with rotation.

Format ^FTx,y

This table identifies the parameters for this format:

| Parameters                    | Details                                                                             |
|-------------------------------|-------------------------------------------------------------------------------------|
| x = x-axis location (in dots) | Accepted Values: 0 to 32000 Default Value: position after last formatted text field |
| y = y-axis location (in dots) | Accepted Values: 0 to 32000 Default Value: position after last formatted text field |

Text The origin is at the start of the character string, at the baseline of the font. Normally the baseline is the bottom of most characters, except for those with descenders, such as g, y, et cetera.

Bar Codes The origin is at the base of the bar code, even when an interpretation is present below the bar code, or if the bar code has guard bars.

Graphic Boxes The origin is at the bottom-left corner of the box.

Images The origin is at the bottom-left corner of the rectangular image area.

Example · The example below shows the differences in font orientation when using ^FT and ^FO relative to their ^LH position. The origin point of the font when using the ^FT command is always at the left of the baseline position of the first element or character in the field.

In normal orientation, all characters rest on the baseline. In rotated orientation, all characters are drawn to the right of the label from the baseline. In inverted orientation, all characters draw down from the baseline and print to the left. In bottom orientation, all characters draw towards the left of the label from the baseline and printer to the right. The dot shows the origin point for both the ^FT and ^FO font orientations.

<!-- image -->

Examples · These are examples of the various font orientations:

<!-- image -->

Continued …

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

## …Continued

Examples · These are examples of the various font orientations:

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

Example · This is an example of the ^FT command and concatenation:

<!-- image -->

When a coordinate is missing, the position following the last formatted field is assumed. This remembering simplifies field positioning with respect to other fields. Once the first field is positioned, other fields follow automatically.

There are several instances where using the ^FT command without specifying x and y parameters is not recommended:

- when positioning the first field in a label format
- at any time with the ^FN (Field Number) command
- following an ^SN (Serialization Data) command

<!-- image -->

<!-- image -->

## ^FV

## Field Variable

Description ^FV replaces the ^FD (field data) command in a label format when the field is variable.

Format ^FVa

This table identifies the parameters for this format:

| Parameters                            | Details                                                                                                  |
|---------------------------------------|----------------------------------------------------------------------------------------------------------|
| a = variable field data to be printed | Accepted Values: 0 to 3072 character string Default Value: if no data is entered, the command is ignored |

- Example · This is an example of how to use the ^MC and ^FV command:

<!-- image -->

Comments ^FV fields are always cleared after the label is printed. ^FD fields are not cleared.

<!-- image -->

<!-- image -->

## ^FW

## Field Orientation

Description The ^FW command sets the default orientation for all command fields that have an orientation (rotation) parameter. Fields can be rotated 0, 90, 180, or 270 degrees clockwise by using this command.

The ^FW command affects only fields that follow it. Once you have issued a ^FW command, the setting is retained until you turn off the printer or send a new ^FW command to the printer.

Format ^FWr

This table identifies the parameters for this format:

| Parameters       | Details                                                                                                                                                |
|------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------|
| r = rotate field | Accepted Value: N = normal R = rotated 90 degrees I = inverted 180 degrees B = bottom-up 270 degrees, read from bottom up Initial Value at Power-up: N |

Comments If the ^FW command is entered with the r parameter missing, the command is ignored.

^FW affects only the orientation in commands where the rotation parameter has not been specifically set. If a command has a specific rotation parameter, that value is used.

<!-- image -->

<!-- image -->

## ^FX

## Comment

Description The ^FX command is useful when you want to add non-printing informational comments or statements within a label format. Any data after the ^FX command up to the next caret (^) or tilde (~) command does not have any effect on the label format. Therefore, you should avoid using the caret (^) or tilde (~) commands within the ^FX statement.

Format ^FXc

This table identifies the parameters for this format:

| Parameters               | Details                          |
|--------------------------|----------------------------------|
| c = non printing comment | Creates a non-printable comment. |

- Example · This is an example of how to use the ^FX
- command effectively.

<!-- image -->

Comments Correct usage of the ^FX command includes following it with the ^FS command.

<!-- image -->

<!-- image -->

## ^GB

## Graphic Box

Description The ^GB command is used to draw boxes and lines as part of a label format. Boxes and lines are used to highlight important information, divide labels into distinct areas, or to improve the appearance of a label. The same format command is used for drawing either boxes or lines.

Format ^GBw,h,t,c,r
