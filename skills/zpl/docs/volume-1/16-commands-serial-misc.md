<!-- Source: ZPL II Programming Guide Volume 1 -->
<!-- Section: Serial, Set, and Misc Commands (^S*, ^T*, ^W*, ^X*, ^Z*) -->
<!-- Generated: 2025-11-02 04:52:35 -->


For ~JSB - or 0 the Backfeed parameter is listed as BEFORE

For ~JS10 - to 90 the Backfeed parameter is listed as the value entered

## ~JS

## Change Backfeed Sequence

Description The ~JS command is used to control the backfeed sequence. This command can be used on printers with or without built-in cutters.

These are the primary applications:

- to allow programming of the rest point of the cut edge of continuous media.
- provide immediate backfeed after peel-off when the printer is used in a print/apply application configuration.

This command stays in effect only until the printer is turned off, a new ~JS command is sent, or the setting is changed on the front panel. When a ~JS command is encountered, it overrides the current front panel setting for the Backfeed Sequence.

The most common way of eliminating backfeed is to operate in Rewind Mode. Rewind Mode does not backfeed at all. After a label prints, the leading edge of the next label is placed at the print line. This eliminates the need to backfeed and does not introduce a non printable area at the leading edge or bottom of the label. It also does not allow the label to be taken from the printer because it is not fed out from under the printhead.

Running in another mode with backfeed turned off allows the label to be removed and eliminates the time-reduction of the backfeed sequence.

Format ~JSb

This table identifies the parameters for this format:

| Parameters                                 | Details                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
|--------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| b = backfeed order in relation to printing | Accepted Values: A = 100 percent backfeed after printing and cutting B = 0 percent backfeed after printing and cutting, and 100 percent before printing the next label N = normal -90 percent backfeed after label is printed O = off -turn backfeed off completely 10 to 90 = percentage value The value entered must be a multiple of 10. Values not divisible by 10 are rounded to the nearest acceptable value. For example, ~JS55 is accepted as 50 percent backfeed. Default Value: N |

<!-- image -->

Comments When using a specific value, the difference between the value entered and 100 percent is calculated before the next label is printed. For example, a value of 40 means 40 percent of the backfeed takes place after the label is cut or removed. The remaining 60 percent takes place before the next label is printed.

The value for this command is also reflected in the Backfeed parameter on the printer configuration label.

For ~JSN - the Backfeed parameter is listed as DEFAULT

For ~JSA - or 100 the Backfeed parameter is listed as AFTER

For ~JSB - or 0 the Backfeed parameter is listed as BEFORE

For ~JS10 - to 90 the Backfeed parameter is listed as the value entered

<!-- image -->

## ^JT

## Head Test Interval

Description The ^JT command allows you to change the printhead test interval from every 100 labels to any desired interval. With the ^JT command, the printer is allowed to run the test after printing a label. When a parameter is defined, the printer runs the test after printing a set amount of labels.

The printer's default head test state is off. Parameters for running the printhead test are defined by the user.

Format ^JT####,a,b,c

This table identifies the parameters for this format:

| Parameters                                                    | Details                                                                                                         |
|---------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------|
| #### = four-digit number of labels printed between head tests | Accepted Values: 0000 to 9999 If a value greater than 9999 is entered, it is ignored. Default Value: 0000 (off) |
| a = manually select range of elements to test                 | Accepted Values: Y (yes) or N (no) Initial Value at Power-up: N                                                 |
| b = first element to check when parameter a is Y              | Accepted Values: 0 to 9999 Initial Value at Power-up: 0                                                         |
| c = last element to check when parameter a is Y               | Accepted Values: 0 to 9999 Initial Value at Power-up: 9999                                                      |

Comments The ^JT command supports testing a range of print elements. The printer automatically selects the test range by tracking which elements have been used since the previous test.

^JT also turns on Automatic Mode to specify the first and last elements for the head test. This makes it possible to select any specific area of the label or the entire print width.

If the last element selected is greater than the print width selected, the test stops at the selected print width.

Whenever the head test command is received, a head test is performed on the next label unless the count is set to 0 (zero).

<!-- image -->

<!-- image -->

## ^JU

## Configuration Update

Description The ^JU command sets the active configuration for the printer.

Format ^JUa

This table identifies the parameters for this format:

| Parameters               | Details                                                                                                                                                                                                                                   |
|--------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| a = active configuration | Accepted Values: F = reload factory values These values are lost at power-off if not saved with ^JUS . R = recall last saved values S = save current settings These values are used at power-on. Default Value: a value must be specified |

<!-- image -->

## ^JW

## Set Ribbon Tension

Description ^JW sets the ribbon tension for the printer it is sent to.

Format ^JWt

This table identifies the parameters for this format:

| Parameters   | Details                                                                               |
|--------------|---------------------------------------------------------------------------------------|
| t = tension  | Accepted Values: L = low M = medium H = high Default Value: a value must be specified |

Comments ^JW is used only for PAX series printers.

<!-- image -->

<!-- image -->

~JX

## Cancel Current Partially Input Format

Description The ~JX command cancels a format currently being sent to the printer. It does not affect any formats currently being printed, or any subsequent formats that might be sent.

Format ~JX

## ^JZ

## Reprint After Error

Description The ^JZ command reprints a partially printed label caused by a Ribbon Out , Media Out , or Head Open error condition. The label is reprinted as soon as the error condition is corrected.

This command remains active until another ^JZ command is sent to the printer or the printer is turned off.

## Format ^JZa

This table identifies the parameters for this format:

| Parameters              | Details                                                         |
|-------------------------|-----------------------------------------------------------------|
| a = reprint after error | Accepted Values: Y (yes) or N (no) Initial Value at Power-up: Y |

Comments ^JZ sets the error mode for the printer. If ^JZ changes, only labels printed after the change are affected.

If the parameter is missing or incorrect, the command is ignored.

<!-- image -->

<!-- image -->

~KB

## Kill Battery (Battery Discharge Mode)

Description To maintain performance of the rechargeable battery in the portable printers, the battery must be fully discharged and recharged regularly. The ~KB command places the printer in battery discharge mode. This allows the battery to be drained without actually printing.

Format ~KB

Comments While the printer is in Discharge Mode, the green power LED flashes in groups of three flashes.

Discharge Mode might be terminated by sending a printing format to the printer or by pressing either of the front panel keys.

If the battery charger is plugged into the printer, the battery is automatically recharged once the discharge process is completed.

<!-- image -->

^KD

## Select Date and Time Format (for Real Time Clock)

Description The ^KD command selects the format that the Real-Time Clock's date and time information presents as on a configuration label. This is also displayed on the Printer Idle LCD front panel display, and displayed while setting the date and time.

Format ^KDa

This table identifies the parameters for this format:

| Parameters                        | Details                                                                                                                                                                                               |
|-----------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| a = value of date and time format | Accepted Values: 0 = normal, displays Version Number of firmware 1 = MM/DD/YY (24-hour clock) 2 = MM/DD/YY (12-hour clock) 3 = DD/MM/YY (24-hour clock) 4 = DD/MM/YY (12-hour clock) Default Value: 0 |

Comments If the Real-Time Clock hardware is not present, Display Mode is set to 0 (Version Number).

If Display Mode is set to 0 (Version Number) and the Real-Time Clock hardware is present, the date and time format on the configuration label is presented in format 1.

If Display Mode is set to 0 (Version Number) and the Real-Time Clock hardware is present, the date and time format on the front panel display is presented in format 1.

<!-- image -->

<!-- image -->

<!-- image -->

^KL

## Define Language

Description The ^KL command selects the language displayed on the front panel.

Format ^KLa

This table identifies the parameters for this format:

| Parameters   | Details                                                                                                                                                                                             |
|--------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| a = language | Accepted Values: 1 = English 2 = Spanish 3 = French 4 = German 5 = Italian 6 = Norwegian 7 = Portuguese 8 = Swedish 9 = Danish 10 = Spanish2 11 = Dutch 12 = Finnish 13 = Japanese Default Value: 1 |

<!-- image -->

^KN

## Define Printer Name

Description The printer's network name and description can be set using the ^KN command. ^KN is designed to make your Zebra printer easy for users to identify. The name the administrator designates is listed on the configuration label and on the Web page generated by the printer.

Format ^KNa,b

This table identifies the parameters for this format:

| Parameters              | Details                                                                                                                                                                                  |
|-------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| a = printer name        | Accepted Values: up to 16 alphanumeric characters Default Value: if a value is not entered, the parameter is ignored If more than 16 characters are entered, only the first 16 are used. |
| b = printer description | Accepted Values: up to 35 alphanumeric characters Default Value: if a value is not entered, the parameter is ignored If more than 35 characters are entered, only the first 35 are used. |

Example · This is an example of how to change the printer's network name an description:

This shows how a configuration looks before using this command and after using this command:

^KNZebra1,desk\_printer

```
^XA ^XZ
```

## Before using this command:            After using this command:

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

^KP

## Define Password

Description The ^KP command is used to define the password that must be entered to access the front panel switches and LCD Setup Mode.

Format ^KP####

This table identifies the parameters for this format:

| Parameters                           | Details                                                              |
|--------------------------------------|----------------------------------------------------------------------|
| #### = mandatory four-digit password | Accepted Values: any four-digit numeric sequence Default Value: 1234 |

Example · This is an example of how to set a new front panel password:

^XA

^KP5678

^XZ

Comments If you forget your password, the printer can be returned to a default Setup Mode and the default password 1234 is valid again. Caution should be used, however - this also sets the printer configuration values back to their defaults.

To return the printer to the default factory settings using ZPL, send this:

^XA

^JUF

^XZ

To return the printer to the default factory settings using the control panel keys, see your printer's User Guide for the procedure.

<!-- image -->

## ^LH

## Label Home

Description The ^LH command sets the label home position.

The default home position of a label is the upper-left corner (position 0,0 along the x and y axis). This is the axis reference point for labels. Any area below and to the right of this point is available for printing. The ^LH command changes this reference point. For instance, when working with preprinted labels, use this command to move the reference point below the preprinted area.

This command affects only fields that come after it. It is recommended to use ^LH as one of the first commands in the label format.

Format ^LHx,y

This table identifies the parameters for this format:

| Parameters                    | Details                                                                                  |
|-------------------------------|------------------------------------------------------------------------------------------|
| x = x-axis position (in dots) | Accepted Values: 0 to 32000 Initial Value at Power-up: 0 or last permanently saved value |
| y = y-axis position (in dots) | Accepted Values: 0 to 32000 Initial Value at Power-up: 0 or last permanently saved value |

Depending on the printhead used in your printer, use one of these when figuring the values for x and y :

```
6 dots = 1 mm, 152 dots = 1 inch 8 dots = 1 mm, 203 dots = 1 inch 11.8 dots = 1 mm, 300 dots = 1 inch 24 dots = 1 mm, 608 dots = 1 inch
```

Comments To be compatible with existing printers, this command must come before the first ^FS (Field Separator) command. Once you have issued an ^LH command, the setting is retained until you turn off the printer or send a new ^LH command to the printer.

<!-- image -->

## ^LL

## Label Length

Description The ^LL command defines the length of the label. This command is necessary when using continuous media (media not divided into separate labels by gaps, spaces, notches, slots, or holes).

To affect the current label and be compatible with existing printers, ^LL must come before the first ^FS (Field Separator) command. Once you have issued ^LL , the setting is retained until you turn off the printer or send a new ^LL command.

Format ^LLy

This table identifies the parameters for this format:

| Parameters                    | Details                                                                                                                                                                                                                                                                                                                        |
|-------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| y = y-axis position (in dots) | Accepted Values: 1 to 32000 , not to exceed the maximum label size. While the printer accepts any value for this parameter, the amount of memory installed determines the maximum length of the label. Default Value: typically set through the LCD (if applicable), or to the maximum label length capability of the printer. |

Comments These formulas can be used to determine the value of y:

| For 6 dot/mm printheads...   | Label length in inches x 152.4 (dots/inch) = y   |
|------------------------------|--------------------------------------------------|
| For 8 dot/mm printheads...   | Label length in inches x 203.2 (dots/inch) = y   |
| For 12 dot/mm printheads...  | Label length in inches x 304.8 (dots/inch) = y   |
| For 24 dot/mm printheads...  | Label length in inches x 609.6 (dots/inch) = y   |

Values for y depend on the memory size. If the entered value for y exceeds the acceptable limits, the bottom of the label is cut off. The label also shifts down from top to bottom.

If multiple ^LL commands are issued in the same label format, the last ^LL command affects the next label unless it is prior to the first ^FS .

<!-- image -->

## ^LR

## Label Reverse Print

Description The ^LR command reverses the printing of all fields in the label format. It allows a field to appear as white over black or black over white.

Using the ^LR is identical to placing an ^FR command in all current and subsequent fields.

Format ^LRa

This table identifies the parameters for this format:

| Parameters                   | Details                                                                                         |
|------------------------------|-------------------------------------------------------------------------------------------------|
| a = reverse print all fields | Accepted Values: Y (yes) or N (no) Initial Value at Power-up: N or last permanently saved value |

Example · This is an example that shows printing white over black and black over white:

<!-- image -->

Comments The ^LR setting remains active unless turned off by ^LRN or the printer is turned off.

Note · ^GB needs to be used together with ^LR .

Only fields following this command are affected.

<!-- image -->

<!-- image -->

## ^LS

## Label Shift

Description The ^LS command allows for compatibility with Z-130 printer formats that are set for less than full label width. It is used to shift all field positions to the left so the same commands used on a Z-130 or Z-220 Printer can be used on other Zebra printers.

To determine the value for the ^LS command, use this formula:

```
Z-130 and Z-220 values for ^LHx + ^FOx (distance from edge of label) = printer value for ^LSa
```

If the print position is less than 0, set ^LS to 0.

Format ^LSa

Important · The ability to save the ^LS command depends on the version of firmware.

This table identifies the parameters for this format:

| Parameters                     | Details                                                     |
|--------------------------------|-------------------------------------------------------------|
| a = shift left value (in dots) | Accepted Values: -9999 to 9999 Initial Value at Power-up: 0 |

Comments When entering positive values, it is not necessary to use the + sign. The value is assumed to be positive unless preceded by a negative sign (-).

To be compatible with existing Zebra printers, this command must come before the first ^FS (Field Separator) command. Once you have issued an ^LS command, the setting is retained until you turn off the printer or send a new ^LS command to the printer.

## ^LT

## Label Top

Description The ^LT command moves the entire label format a maximum of 120 dot rows up or down from its current position, in relation to the top edge of the label. A negative value moves the format towards the top of the label; a positive value moves the format away from the top of the label.

This command can be used to fine-tune the position of the finished label without having to change any of the existing parameters.

Important · For some printer models, it is possible to request a negative value large enough to cause the media to backup into the printer and become unthreaded from the platen. This condition can result in a printer error or unpredictable results.

Format ^LTx

This table identifies the parameters for this format:

| Parameters                  | Details                                                                                         |
|-----------------------------|-------------------------------------------------------------------------------------------------|
| x = label top (in dot rows) | Accepted Values: -120 to 120 Default Value: a value must be specified or the command is ignored |

Comments The Accepted Value range for x might be smaller depending on the printer platform.

The ^LT command does not change the media rest position.

<!-- image -->

<!-- image -->

^MC

## Map Clear

Description In normal operation, the bitmap is cleared after the format has been printed. The ^MC command is used to retain the current bitmap. This applies to current and subsequent labels until cleared with ^MCY .

Format ^MCa

Important · To produce a label template, ^MC must be used with ^FV .

This table identifies the parameters for this format:

| Parameters    | Details                                                                                   |
|---------------|-------------------------------------------------------------------------------------------|
| a = map clear | Accepted Values: Y (clear bitmap) or N (do not clear bitmap) Initial Value at Power-up: Y |

Comments The ^MC command retains the image of the current label after formatting. It appears in the background of the next label printed.

<!-- image -->

<!-- image -->

^MD

## Media Darkness

Description The ^MD command adjusts the darkness relative to the current darkness setting.

Format ^MDa

This table identifies the parameters for this format:

| Parameters               | Details                                                                                                                               |
|--------------------------|---------------------------------------------------------------------------------------------------------------------------------------|
| a = media darkness level | Accepted Values: -30 to 30 , depending on current value Initial Value at Power-up: 0 If no value is entered, this command is ignored. |

Example •

- These examples show setting the printer to different darkness levels:
- If the current value (value on configuration label) is 16, entering the command ^MD-9 decreases the value to 7.
- If the current value (value on configuration label) is 1, entering the command ^MD15 increases the value to 16.
- If the current value (value on configuration label) is 25, entering the command ^MD10 increases only the value to 30, which is the maximum value allowed.

Each ^MD command is treated separately in relation to the current value as printed on the configuration label.

- is 0 to 30 in increments of 0.1. commands (ZPL darkness commands)

Important · The darkness setting range for the Xi III Plus The firmware is setup so that the ^MD and ~SD accepts that range of settings.

- Example · These are examples of the Xi III Plus Darkness Setting:

^MD8.3

~SD8.3

Example · For example, this is what would happen if two ^MD commands were received: Assume the current value is 15. An ^MD-6 command is received that changes the current value to 9. Another command, ^MD2 , is received. The current value changes to 17.

The two ^MD commands are treated individually in relation to the current value of 15.

Comments The ~SD command value, if applicable, is added to the ^MD command.

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

^MF

## Media Feed

Description The ^MF command dictates what happens to the media at power-up and at head-close after the error clears.

Format ^MFp,h

This table identifies the parameters for this format:

| Parameters                              | Details                                                                                                                                                                               |
|-----------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| p = feed action at power-up             | Accepted Values: F = feed to the first web after sensor C = (see ~JC on page 187 definition) L = (see ~JL on page 194 definition) N = no media feed Default Value: platform-dependent |
| h = feed action after closing printhead | Accepted Values: F = feed to the first web after sensor C = (see ~JC on page 187 definition) L = (see ~JL on page 194 definition) N = no media feed Default Value: platform-dependent |

