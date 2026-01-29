<!-- Source: ZPL II Programming Guide Volume 1 -->
<!-- Section: Index and Reference Material -->
<!-- Generated: 2025-11-02 04:52:35 -->

Comments It is important to remember that if you choose the N setting, the printer assumes that the media and its position relative to the printhead are the same as before power was turned off or the printhead was opened. Use the ^JU command to save changes.

<!-- image -->

^ML

## Maximum Label Length

Description The ^ML command lets you adjust the maximum label length.

Format ^MLa,b,c,d

This table identifies the parameters for this format:

| Parameters                             | Details                                                                                                                                                                                                                                                                                    |
|----------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| a = maximum label length (in dot rows) | Accepted Values: 0 to maximum length of label Default Value: last permanently saved value                                                                                                                                                                                                  |
| b = maximum logical paper out counter  | Accepted Values: must be greater than the actual label length or the printer indicates a paper out error after each label Default Value: set to one inch longer than twice the label length                                                                                                |
| c = maximum physical paper out counter | Accepted Values: must be greater than the actual notch or hole or the printer indicates a paper out condition after each label Default Value: is set to one half an inch                                                                                                                   |
| d = maximum ribbon out counter         | Accepted Values: allows for the ribbon sensors to occasionally get an incorrect ribbon reading without causing an error condition Default Value: set to one half of a millimeter Important • The printer ignores ribbon indications that are less than one-half of a millimeter in length. |

Comments For calibration to work properly, you must set the maximum label length equal to or greater than your actual label length.

<!-- image -->

<!-- image -->

^MM

## Print Mode

Description The ^MM command determines the action the printer takes after a label or group of labels has printed. This bulleted list identifies the different modes of operation:

- Tear-off - after printing, the label advances so the web is over the tear bar. The label, with liner attached, can be torn off manually.
- Peel-off - after printing, the label moves forward and activates a Label Available Sensor. Printing stops until the label is manually removed from the printer.

Power Peel - liner automatically rewinds using an optional internal rewind spindle.

Value Peel - liner feeds down the front of the printer and is manually removed.

Prepeel - after each label is manually removed, the printer feeds the next label forward to prepeel a small portion of the label away from the liner material. The printer then backfeeds and prints the label. The prepeel feature assists in the proper peel operation of some media types.

- Rewind - the label and backing are rewound on an (optional) external rewind device. The next label is positioned under the printhead (no backfeed motion).
- Applicator - when used with an application device, the label move far enough forward to be removed by the applicator and applied to an item.
- Cutter - after printing, the media feeds forward and is automatically cut into predetermined lengths.

Format ^MMa,b

This table identifies the parameters for this format:

| Parameters         | Details                                                                                                                                                                                                                                                                |
|--------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| a = desired mode   | Accepted Values: T = Tear-off P = Peel-off (not available on S -300) R = Rewind A = Applicator (depends on printer model) C = Cutter Default Value: T The values available for parameter a are dependent on the printer being used and whether it supports the option. |
| b = prepeel select | Accepted Values: Y (yes) or N (no) Default Value: Y The command is ignored if parameters are missing or invalid. The current value of the command remains unchanged.                                                                                                   |

Comments Be sure to select the appropriate value for the print mode being used to avoid unexpected results.

<!-- image -->

^MN

## Media Tracking

Description The ^MN command relays to the printer what type of media is being used (continuous or non-continuous) for purposes of tracking. This bulleted list shows the types of media associated with this command:

- Continuous Media - this media has no physical characteristic (web, notch, perforation, mark, et cetera) to separate labels. Label length is determined by the ^LL command.
- Non-continuous Media - this media has some type of physical characteristic (web, notch, perforation, mark, et cetera) to separate the labels.

## Format ^MNa

This table identifies the parameters for this format:

| Parameters           | Details                                                                                                                                                                                                                  |
|----------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| a = media being used | Accepted Values: N = continuous media *Y = non-continuous media web sensing *W = non-continuous media web sensing M = non-continuous media mark sensing Default Value: a value must be entered or the command is ignored |

* provides the same result.

<!-- image -->

<!-- image -->

^MP

## Mode Protection

Description The ^MP command is used to disable the various mode functions on the front panel. Once disabled, the settings for the particular mode function can no longer be changed and the LED associated with the function does not light.

Because this command has only one parameter, each mode must be disabled with an individual ^MP command.

Format ^MPa

This table identifies the parameters for this format:

| Parameters          | Details                                                                                                                                                                                                                                                                                                                                            |
|---------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| a = mode to protect | Accepted Values: D = disable Darkness Mode P = disable Position Mode C = disable Calibration Mode E = enable all modes S = disable all mode saves (modes can be adjusted but values are not saved) W = disable Pause F = disable Feed X = disable Cancel M = disable menu changes Default Value: a value must be entered or the command is ignored |

- Example • This example disables these modes, D and C .

^XA

^MPD

^MPC

^XZ

<!-- image -->

<!-- image -->

## ^MT

## Media Type

Description The ^MT command selects the type of media being used in the printer. There are two choices for this command:

- Thermal Transfer Media - this media uses a high-carbon black or colored ribbon. The ink on the ribbon is bonded to the media.
- Direct Thermal Media - this media is heat sensitive and requires no ribbon.

## Format ^MTa

This table identifies the parameters for this format:

| Parameters          | Details                                                                                                                               |
|---------------------|---------------------------------------------------------------------------------------------------------------------------------------|
| a = media type used | Accepted Values: T = thermal transfer media D = direct thermal media Default Value: a value must be entered or the command is ignored |

<!-- image -->

<!-- image -->

## ^MU

## Set Units of Measurement

Description The ^MU command sets the units of measurement the printer uses. ^MU works on a field-by-field basis. Once the mode of units is set, it carries over from field to field until a new mode of units is entered.

^MU also allows for printing at lower resolutions - 600 dpi printers are capable of printing at 300, 200, and 150 dpi; 300 dpi printers are capable of printing at 150 dpi.

Format ^MUa,b,c

This table identifies the parameters for this format:

| Parameters                            | Details                                                                                           |
|---------------------------------------|---------------------------------------------------------------------------------------------------|
| a = units                             | Accepted Values: D = dots I = inches M = millimeters Default Value: D                             |
| b = format base in dots per inch      | Accepted Values: 150 , 200 , 300 Default Value: a value must be entered or the command is ignored |
| c = desired dots-per- inch conversion | Accepted Values: 300 , 600 Default Value: a value must be entered or the command is ignored       |

q

a

<!-- image -->

Example · This is an example of Setting Units:

Assume 8 dot/millimeter (203 dot/inch) printer.

Field based on dots:

^MUd^FO100,100^GB1024,128,128^FS

Field based on millimeters:

^MUm^FO12.5,12.5^GB128,16,16^FS

Field based on inches:

^MUi^FO.493,.493^GB5.044,.631,.631^FS

## Example · This is an example of Converting dpi Values.

Convert a 150 dpi format to a 300 dpi format with a base in dots:

^MUd,150,300

Convert a 150 dpi format to a 600 dpi format with a base in dots:

<!-- formula-not-decoded -->

Convert a 200 dpi format to a 600 dpi format with a base in dots:

<!-- formula-not-decoded -->

To reset the conversion factor to the original format, enter matching values for parameters b and c :

^MUd,150,150

^MUd,200,200

^MUd,300,300

^MUd,600,600

Comments This command should appear at the beginning of the label format to be in proper ZPL II format.

To turn the conversion off, enter matching values for parameter b and c .

<!-- image -->

<!-- image -->

^MW

## Modify Head Cold Warning

Description The ^MW command allows you to set the head cold warning indicator based on the operating environment.

Format ^MWy

This table identifies the parameters for this format:

| Parameters                   | Details                                                                     |
|------------------------------|-----------------------------------------------------------------------------|
| a = enable head cold warning | Accepted Values: y = enable head cold warning n = disable head cold warning |

Important · When a parameter is not given, the instruction is ignored .

<!-- image -->

~NC

## Network Connect

Description The ~NC command is used to connect a particular printer to a network by calling up the printer's network ID number.

Format ~NC###

This table identifies the parameters for this format:

| Parameters   | Parameters                                                  | Details                                               |
|--------------|-------------------------------------------------------------|-------------------------------------------------------|
| ###          | = network ID number assigned (must be a three- digit entry) | Accepted Values: 001 to 999 Default Value: 000 (none) |

Comments Use this command at the beginning of any label format to specify which printer on the network is going to be used. Once the printer is established, it continues to be used until it is changed by another ~NC command. This command must be included in the label format to wake up the printer .

The commands ^MW, ~ NC , ^NI , ~NR , and ~NT are used only with ZNET RS-485 printer networking.

<!-- image -->

<!-- image -->

## ^NI

## Network ID Number

Description The ^NI command is used to assign a network ID number to the printer. This must be done before the printer can be used in a network.

Format ^NI###

This table identifies the parameters for this format:

| Parameters   | Parameters                                                  | Details                                               |
|--------------|-------------------------------------------------------------|-------------------------------------------------------|
| ###          | = network ID number assigned (must be a three- digit entry) | Accepted Values: 001 to 999 Default Value: 000 (none) |

Comments The last network ID number set is the one recognized by the system.

The commands ~NC , ^NI , ~NR , and ~NT are used only with ZNET RS-485 printer networking.

<!-- image -->

~NR

## Set All Network Printers Transparent

Description The ~NR command sets all printers in the network to be transparent, regardless of ID or current mode.

Format ~NR

Comments The commands ~NC , ^NI , ~NR , and ~NT are used only with ZNET RS-485 printer networking.

<!-- image -->

<!-- image -->

<!-- image -->

## ^NS

## Change Networking Settings

Description The ^NS command is used to change network settings.

Format ^NSa,b,c,d

This table identifies the parameters for this format:

| Parameters          | Details                                                                                                                       |
|---------------------|-------------------------------------------------------------------------------------------------------------------------------|
| a = network setting | Accepted Values: IP Resolution. a (ALL) , b (BOOTP), c (DHCP and BOOTP), d (DHCP), g (GLEANING ONLY), r (RARP), p (permanent) |
| b = IP Address      | Accepted Values: 0 to 255                                                                                                     |
| c = Subnet Mask     | Accepted Values: 0 to 255                                                                                                     |
| d = Default Gateway | Accepted Values: 0 to 255                                                                                                     |

<!-- image -->

~NT

## Set Currently Connected Printer Transparent

Description The ~NT command sets the currently connected network printer to be transparent.

Format ~NT

Comments With Z Series ®  printers, the ~NT command functions the same as the ~NR command. All Z Series printers on a network receive the transmission.

The commands ~NC , ^NI , ~NR , and ~NT are used only with ZNET RS-485 printer networking.

<!-- image -->

<!-- image -->

## ^PF

## Slew Given Number of Dot Rows

Description The ^PF command causes the printer to slew labels (move labels at a high speed without printing) a specified number of dot rows from the bottom of the label. This allows faster printing when the bottom portion of a label is blank.

Format ^PF#

This table identifies the parameters for this format:

| Parameters                      | Details                                                                                      |
|---------------------------------|----------------------------------------------------------------------------------------------|
| # = number of dots rows to slew | Accepted Values: 0 to 32000 Default Value: a value must be entered or the command is ignored |

## ^PH ~PH

## Slew to Home Position

Description The ^PH or ~PH command causes the printer to feed one blank label.

The ~PH command feeds one label after the format currently being printed is done or when the printer is placed in pause.

The ^PH command feeds one blank label after the current format prints.

Format ^PH or ~PH

<!-- image -->

<!-- image -->

<!-- image -->

^PM

## Printing Mirror Image of Label

Description The ^PM command prints the entire printable area of the label as a mirror image. This command flips the image from left to right.

Format ^PMa

This table identifies the parameters for this format:

| Parameters                             | Details                                             |
|----------------------------------------|-----------------------------------------------------|
| a = print mirror image of entire label | Accepted Values: Y (yes) or N (no) Default Value: N |

Example · This is an example of printing a mirror image on a label:

## ZPL II CODE

^XA^PMY

^FO100,100

^CFG

^FDMIRROR^FS

^FO100,160

- ^FDIMAGE^FS
- ^XZ

Comments If the parameter is missing or invalid, the command is ignored. Once entered, the ^PM command remains active until ^PMN is received or the printer is turned off.

## GENERATED LABEL

<!-- image -->

<!-- image -->

## ^PO

## Print Orientation

Description The ^PO command inverts the label format 180 degrees. The label appears to be printed upside down. If the original label contains commands such as ^LL , ^LS , ^LT and ^PF , the inverted label output is affected differently.

Format ^POa

This table identifies the parameters for this format:

| Parameters                   | Details                                                    |
|------------------------------|------------------------------------------------------------|
| a = invert label 180 degrees | Accepted Values: N (normal) or I (invert) Default Value: N |

Example · This is an example of printing a label at 180 degrees:

<!-- image -->

The ^POI command inverts the x, y coordinates. All image placement is relative to these inverted coordinates. Therefore, a different ^LH (Label Home) can be used to move the print back onto the label.

Comments If multiple ^PO commands are issued in the same label format, only the last command sent to the printer is used.

Once the ^PO command is sent, the setting is retained until another ^PO command is received or the printer is turned off.

<!-- image -->

<!-- image -->

## ^PP ~PP

## Programmable Pause

Description The ~PP command stops printing after the current label is complete (if one is printing) and places the printer in Pause Mode.

The ^PP command is not immediate. Therefore, several labels might print before a pause is performed. This command pauses the printer after the current format prints.

The operation is identical to pressing PAUSE on the front panel of the printer. The printer remains paused until PAUSE is pressed or a ~PS (Print Start) command is sent to the printer.

Format ^PP or ~PP

<!-- image -->

## Print Quantity

Description The ^PQ command gives control over several printing operations. It controls the number of labels to print, the number of labels printed before printer pauses, and the number of replications of each serial number.

Format ^PQq,p,r,o

This table identifies the parameters for this format:

| Parameters                                      | Details                                                                     |
|-------------------------------------------------|-----------------------------------------------------------------------------|
| q = total quantity of labels to print           | Accepted Value: 1 to 99,999,999 Default Value: 1                            |
| p = pause and cut value (labels between pauses) | Accepted Value: 1 to 99,999,999 Default Value: 0 (no pause)                 |
| r = replicates of each serial number            | Accepted Value: 0 to 99,999,999 replicates Default Value: 0 (no replicates) |
| o = override pause count                        | Accepted Value: Y (yes) or N (no) Default Value: N                          |

If the o parameter is set to Y , the printer cuts but does not pause, and the printer does not pause after every group count of labels has been printed. With the o parameter set to N (default), the printer pauses after every group count of labels has been printed.

Example · This example shows the control over print operations:

^PQ50,10,1,Y : This example prints a total of 50 labels with one replicate of each serial number. It prints the total quantity in groups of 10, but does not pause after every group.

^PQ50,10,1,N : This example prints a total of 50 labels with one replicate of each serial number. It prints the total quantity in groups of 10, pausing after every group.

<!-- image -->

<!-- image -->

## ^PR

## Print Rate

Description The ^PR command determines the media and slew speed (feeding a blank label) during printing.

The printer operates with the selected speeds until the setting is reissued or the printer is turned off.

The print speed is application-specific. Because print quality is affected by media, ribbon, printing speeds, and printer operating modes, it is very important to run tests for your applications.

Important · Some models go to default print speed when power is turned off.

Format ^PRp,s,b

<!-- image -->

This table identifies the parameters for this format:

| Parameters         | Details                                                                                                                                                                                                                                                                                                                                                                                                   |
|--------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| p = print speed    | Accepted Values: A or 2 = 50.8 mm/sec. (2 inches/sec.) B or 3 = 76.2 mm/sec. (3 inches/sec.) C or 4 = 101.6 mm/sec. (4 inches/sec.) 5 = 127 mm/sec.(5 inches/sec.) D or 6 = 152.4 mm/sec. (6 inches/sec.) E or 8 = 203.2 mm/sec. (8 inches/sec.) 9 = 220.5 mm/sec. 9 inches/sec.) 10 = 245 mm/sec.(10 inches/sec.) 11 = 269.5 mm/sec.(11 inches/sec.) 12 = 304.8 mm/sec. 12 inches/sec.) Default Value: A |
| s = slew speed     | Accepted Values: A or 2 = 50.8 mm/sec. (2 inches/sec.) B or 3 = 76.2 mm/sec. (3 inches/sec.) C or 4 = 101.6 mm/sec. (4 inches/sec.) 5 = 127 mm/sec. 5 inches/sec.) D or 6 = 152.4 mm/sec. (6 inches/sec.) E or 8 = 203.2 mm/sec. (8 inches/sec.) 9 = 220.5 mm/sec. (9 inches/sec.) 10 = 245 mm/sec. (10 inches/sec.) 11 = 269.5 mm/sec. 11 inches/sec.) 12 = 304.8 mm/sec. 12 inches/sec.)                |
| b = backfeed speed | Accepted Values: A or 2 = 50.8 mm/sec. (2 inches/sec.) B or 3 = 76.2 mm/sec. (3 inches/sec.) C or 4 = 101.6 mm/sec. (4 inches/sec.) 5 = 127 mm/sec.(5 inches/sec.) D or 6 = 152.4 mm/sec. (6 inches/sec.) E or 8 = 203.2 mm/sec. (8 inches/sec.) 9 = 220.5 mm/sec. 9 inches/sec.) 10 = 245 mm/sec. 10 inches/sec.) 11 = 269.5 mm/sec. 11 inches/sec.) 12 = 304.8 mm/sec. 12 inches/sec.) Default Value: A |

<!-- image -->

Comments The speed setting for p , s , and b is dependent on the limitations of the printer. If a particular printer is limited to a rate of 6 ips (inches per second), a value of 12 can be entered but the printer performs only at a 6 ips rate. See your printer's User Guide for specifics on performance.

<!-- image -->

## ~PR

## Applicator Reprint

Description The ~PR command is supported only by the PAX and PAX 2-Series printers. If the ~PR command is enabled (see ^JJ on page 192), the last label printed reprint, similar to the applicator asserting the Reprint signal on the applicator port.

Format ~PR

Comments Pressing PREVIOUS on the front panel also causes the last label to reprint.

<!-- image -->

<!-- image -->

<!-- image -->

## ~PS

## Print Start

Description The ~PS command causes a printer in Pause Mode to resume printing. The operation is identical to pressing PAUSE on the front panel of the printer when the printer is already in Pause Mode.

Format ~PS

<!-- image -->

## ^PW

## Print Width

Description The ^PW command allows you set the print width.

Format ^PWa

This table identifies the parameters for this format:

| Parameters                | Details                                                                                                                                                                               |
|---------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| a = label width (in dots) | Accepted Values: 2 , to the width of the label If the value exceeds the width of the label, the width is set to the label's maximum size. Default Value: last permanently saved value |

Limitation Not all Zebra printers support the ^PW command.

<!-- image -->

<!-- image -->

~RO

## Reset Advanced Counter

Description The ~RO command resets the advanced counters used by the printer to monitor label generation in inches, centimeters, and number of labels. Two resettable counters are available and can be reset.

Format ~ROc

This table identifies the parameters for this format:

| Parameters         | Details                                                                                    |
|--------------------|--------------------------------------------------------------------------------------------|
| c = counter number | Accepted Values: 1 or 2 Default Value: a value must be specified or the command is ignored |

Example · This is an example of the ~RO command.

<!-- image -->

<!-- image -->

<!-- image -->

## ^SC

## Set Serial Communications

Description The ^SC command allows you to change the serial communications parameters you are using.

Format ^SCa,b,c,d,e,f

This table identifies the parameters for this format:

| Parameters                     | Details                                                                                                                                                                 |
|--------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| a = baud rate                  | Accepted Values: 110 ; 600 ; 1,200 ; 2400 ; 4800 ; 9600 ; 14400 ; 19200 ; 28800 ; 38400 ; or 57600; 115200 Default Value: must be specified or the parameter is ignored |
| b = word length (in data bits) | Accepted Values: 7 or 8 Default Value: must be specified                                                                                                                |
| c = parity                     | Accepted Values: N (none), E (even), or O (odd) Default Value: must be specified                                                                                        |
| d = stop bits                  | Accepted Values: 1 or 2 Default Value: must be specified                                                                                                                |
| e = protocol mode              | Accepted Values: X (XON/XOFF), D (DTR/DSR), or R (RTS) Default Value: must be specified                                                                                 |
| f = Zebra protocol             | Accepted Values: A = ACK/NAK N = none Z = Zebra Default Value: must be specified                                                                                        |

Comments If any of the parameters are missing, out of specification, not supported by a particular printer, or have a ZPL-override DIP switch set, the command is ignored.

A ^JUS command causes the changes in Communications Mode to persist through power-up and software resets.

<!-- image -->

<!-- image -->

## ~SD

## Set Darkness

Description The ~SD command allows you to set the darkness of printing. ~SD is the equivalent of the darkness setting parameter on the front panel display.

Format ~SD##

This table identifies the parameters for this format:

| Parameters                                       | Details                                                               |
|--------------------------------------------------|-----------------------------------------------------------------------|
| ## = desired darkness setting (two-digit number) | Accepted Values: 00 to 30 Default Value: last permanently saved value |

Example · These are examples of the Xi III Plus

^MD8.3

~SD8.3

Comments The ^MD command value, if applicable, is added to the ~SD command.

- Darkness Setting:

<!-- image -->

<!-- image -->

## ^SE

## Select Encoding

Description The ^SE command was created to select the desired ZPL or ZPL II encoding table.

Format ^SEd:o.x

This table identifies the parameters for this format:

| Parameters                     | Details                                                                                 |
|--------------------------------|-----------------------------------------------------------------------------------------|
| d = location of encoding table | Accepted Values: R: , E: , B: , and A: Default Value: R:                                |
| o = name of encoding table     | Accepted Value: 1 to 8 alphanumeric characters Default Value: a value must be specified |
| x = extension                  | Fixed Value: .DAT                                                                       |

<!-- image -->

<!-- image -->

^SF

## Serialization Field (with a Standard ^FD String)

Description The ^SF command allows you to serialize a standard ^FD string. Fields serialized with this command are right-justified or end with the last character of the string. The increment string is aligned with the mask, starting with the right-most position. The maximum size of the mask and increment string is 3K combined.

Format ^SFa,b

This table identifies the parameters for this format:

| Parameters           | Details                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
|----------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| a = mask string      | The mask string sets the serialization scheme. The length of the string mask defines the number of characters in the current ^FD string to be serialized. The mask is aligned to the characters in the ^FD string starting with the right-most position. Mask String placeholders: D or d - Decimal numeric 0-9 H or h - Hexadecimal 0-9 plus a-f or A-F O or o - Octal 0-7 A or a - Alphabetic a-z or A-Z N or n - Alphanumeric 0-9 plus a-z or A-Z                                                                   |
| b = increment string | The increment string is the value to be added to the field on each label. The default value is equivalent to a decimal value of one. The string is composed of any characters defined in the serial string. Invalid characters are assumed to be equal to a value of zero in that character position. The increment value for alphabetic strings start with ' A ' or ' a ' as the zero placeholder. This means to increment an alphabetic character by one, a value of ' B ' or ' b ' must be in the increment string. |

For characters that do not get incremented, the % character needs to be added to the increment string.

<!-- image -->

q

a

Example · This is an example of serializing a ^FD string:

## ZPL II CODE

^XA

- ^FO100,100

^CF0,100

- ^FD12A^SFnnA,F^FS
- ^PQ3
- ^XZ

Note: The ZPL II code above will generate three separate labels, seen to the right.

<!-- image -->

This mask has the first characters as alphanumeric ( nn = 12) and the last digit as uppercase alphabetic (A). The decimal value of the increment number is equivalent to 5 (F). The number of labels generated depends on the number specified by the ^PQ command.

In a similar instance, the ^FD string could be replaced with either of the ^FD strings below to generate a series of label, determined by ^PQ .

```
^FDBL0000^SFAAdddd,1
```

The print sequence on this series of labels is:

```
BL0000, BL0001,...BL0009, BL0010,... BL0099, BL0100,...BL9999, BM0000...
```

^FDBL00-0^SFAAdd%d,1%1

The print sequence on this series of labels is:

```
BL00-0, BL01-1, BL02-2,...BL09-9, BL11-0, BL12-1...
```

<!-- image -->

<!-- image -->

## ^SL

## Set Mode and Language (for Real-Time Clock)

Description The ^SL command is used to specify the Real-Time Clock's mode of operation and language for printing information.

Format ^SLa,b

This table identifies the parameters for this format:

| Parameters   | Details                                                                                                                                                                                                                                                                                                                                                                                                                       |
|--------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| a = mode     | Accepted Values: S = Start Time Mode. This is the time that is read from the Real-Time Clock when label formatting begins (when ^XA is received). The first label has the same time placed on it as the last label. T = Time Now Mode. This is the time that is read from the Real-Time Clock when the label to be printed is placed in print queue. Time Now is similar to a serialized time or date field. Default Value: S |
| b = language | Accepted Values: 1 = English 2 = Spanish 3 = French 4 = German 5 = Italian 6 = Norwegian 7 = Portuguese 8 = Swedish 9 = Danish 10 = Spanish 2 11 = Dutch 12 = Finnish Default Value: the language selected with ^KL or the front panel                                                                                                                                                                                        |

<!-- image -->

## ^SN

## Serialization Data

Description The ^SN command allows the printer to index data fields by a selected increment or decrement value, making the data fields increase or decrease by a specified value each time a label is printed. This can be performed on 100 to 150 fields in a given format and can be performed on both alphanumeric and bar code fields. A maximum of 12 of the rightmost integers are subject to indexing. The first integer found when scanning from right to left starts the indexing portion of the data field.

If the alphanumeric field to be indexed ends with an alpha character, the data is scanned, character by character, from right to left until a numeric character is encountered. Serialization takes place using the value of the first number found.

Format ^SNv,n,z

This table identifies the parameters for this format:

Example •

| Parameters                        | Details                                                                                                                    |
|-----------------------------------|----------------------------------------------------------------------------------------------------------------------------|
| v = starting value                | Accepted Values: 12-digits maximum for the portion to be indexed Default Value: 1                                          |
| n = increment or decrement value  | Accepted Values: 12-digit maximum Default Value: 1 To indicate a decrement value, precede the value with a minus (-) sign. |
| z = add leading zeros (if needed) | Accepted Values: Y (yes) or N (no) Default Value: N                                                                        |

## This example shows incrementing by a specified value:

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

Comments Incrementing and decrementing takes place for each serial-numbered field when all replicates for each serial number have been printed, as specified in parameter r of the ^PQ (print quality) command.

If, during the course of printing serialized labels, the printer runs out of either paper or ribbon, the first label printed (after the media or ribbon has been replaced and calibration completed) has the same serial number as the partial label printed before the out condition occurred. This is done in case the last label before the out condition did not fully print. This is controlled by the ^JZ command.

## Using Leading Zeros

In the ^SN command, the z parameter determines if leading zeros are printed or suppressed. Depending on which value is used ( Y = print leading zeros; N = do not print leading zeros), the printer either prints or suppresses the leading zeros.

The default value for this parameter is N (do not print leading zeros).

## Print Leading Zeros

The starting value consists of the right-most consecutive sequence of digits. The width (number of digits in the sequence) is determined by scanning from right to left until the first non-digit (space or alpha character) is encountered. To create a specific width, manually place leading zeros as necessary.

## Suppressing Leading Zeros

The starting value consists of the right-most consecutive sequence of digits, including any leading spaces. The width (number of digits in the sequence) is determined by scanning from right to left until the first alpha character (except a space) is encountered. To create a specific width, manually place leading spaces or zeros as necessary. Suppressed zeros are replaced by spaces. During the serialization process, when the entire number contains all zeros, the last zero is not suppressed.

The ^SN command replaces the Field Data ( ^FD ) command within a label formatting program.

<!-- image -->

## ^SO

## Set Offset (for Real-Time Clock)

Description The ^SO command is used to set the secondary and the tertiary offset from the primary Real-Time Clock.

Format ^SOa,b,c,d,e,f,g

This table identifies the parameters for this format:

| Parameters         | Details                                                                               |
|--------------------|---------------------------------------------------------------------------------------|
| a = clock set      | Accepted Values: 2 (secondary) or 3 (tertiary) Default Value: value must be specified |
| b = months offset  | Accepted Values: -32000 to 32000 Default Value: 0                                     |
| c = days offset    | Accepted Values: -32000 to 32000 Default Value: 0                                     |
| d = years offset   | Accepted Values: -32000 to 32000 Default Value: 0                                     |
| e = hours offset   | Accepted Values: -32000 to 32000 Default Value: 0                                     |
| f = minutes offset | Accepted Values: -32000 to 32000 Default Value: 0                                     |
| g = seconds offset | Accepted Values: -32000 to 32000 Default Value: 0                                     |

<!-- image -->

<!-- image -->

## ^SP

## Start Print

Description The ^SP command allows a label to start printing at a specified point before the entire label has been completely formatted. On extremely complex labels, this command can increase the overall throughput of the print.

The command works as follows: Specify the dot row at which the ^SP command is to begin. This creates a label segment . Once the ^SP command is processed, all information in that segment prints. During the printing process, all of the commands after the ^SP continue to be received and processed by the printer.

If the segment after the ^SP command (or the remainder of the label) is ready for printing, media motion does not stop. If the next segment is not ready, the printer stops mid-label and wait for the next segment to be completed. Precise positioning of the ^SP command requires a trial-and-error process, as it depends primarily on print speed and label complexity.

The ^SP command can be effectively used to determine the worst possible print quality. You can determine whether using the ^SP command is appropriate for the particular application by using this procedure.

If you send the label format up to the first ^SP command and then wait for printing to stop before sending the next segment, the printed label is a sample of the worst possible print quality. It drops any field that is out of order.

If the procedure above is used, the end of the label format must be:

^SP#^FS

Format ^SPa

This table identifies the parameters for this format:

| Parameters                    | Details                                      |
|-------------------------------|----------------------------------------------|
| a = dot row to start printing | Accepted Values: 0 to 32000 Default Value: 0 |

<!-- image -->

Example · In this example, a label 800 dot rows in length uses ^SP500 . Segment 1 prints while commands in Segment 2 are being received and formatted.

<!-- image -->

<!-- image -->

<!-- image -->

## Halt ZebraNet Alert

Description The ^SQ command is used to stop the ZebraNet Alert option.

Format ^SQa,b,c

This table identifies the parameters for this format:

| Parameters         | Details                                                                                                                                                                                                                                                                                                                                                                                                      |
|--------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| a = condition type | Accepted Values: A = paper out B = ribbon out C = printhead over-temp D = printhead under-temp E = head open F = power supply over-temp G = ribbon-in warning (Direct Thermal Mode) H = rewind full I = cut error J = printer paused K = PQ job completed L = label ready M = head element out P = power on Q = clean printhead R = media low S = ribbon low T = replace head U = battery low V = all errors |
| b = destination    | Accepted Values: A = serial port B = parallel port C = e-mail address D = TCP/IP E = UDP/IP F = SNMP trap * = wild card to stop alerts for all destinations                                                                                                                                                                                                                                                  |
| c = halt messages  | Accepted Values: Y (halt messages) or N (start messages) Default Value: Y                                                                                                                                                                                                                                                                                                                                    |

## ^SR

## Set Printhead Resistance

command allows you to set the printhead resistance.

Description The ^SR

Format ^SR####

This table identifies the parameters for this format:

| Parameters                                         | Details                                                                  |
|----------------------------------------------------|--------------------------------------------------------------------------|
| #### = resistance value (four-digit numeric value) | Accepted Value: 0488 to 1175 Default Value: last permanently saved value |

Comments To avoid damaging the printhead, this value should be less than or equal to the value shown on the printhead being used. Setting a higher value could damage the printhead.

Note · New models automatically set head resistance.

<!-- image -->

<!-- image -->

<!-- image -->

## ^SS

## Set Media Sensors

Description The ^SS command is used to change the values for media, web, ribbon, and label length set during the media calibration process. The media calibration process is described in your specific printer's user's guide.

Format ^SSw,m,r,l,m2,r2,a,b,c

This table identifies the parameters for this format:

| Parameters                                       | Details                                                                                                   |
|--------------------------------------------------|-----------------------------------------------------------------------------------------------------------|
| w = web (three-digit value)                      | Accepted Values: 000 to 100 Default Value: value shown on the media sensor profile or configuration label |
| m = media (three-digit value)                    | Accepted Values: 000 to 100 Default Value: value shown on the media sensor profile or configuration label |
| r =ribbon (three-digit value)                    | Accepted Values: 001 to 100 Default Value: value shown on the media sensor profile or configuration label |
| l = label length (in dots, four-digit value)     | Accepted Values: 0001 to 32000 Default Value: value calculated in the calibration process                 |
| m2 = intensity of media LED (three-digit value)  | Accepted Values: 000 to 100 Default Value: value calculated in the calibration process                    |
| r2 = intensity of ribbon LED (three-digit value) | Accepted Values: 000 to 100 Default Value: value calculated in the calibration process                    |
| a = mark sensing (three-digit value)             | Accepted Values: 000 to 100 Default Value: value calculated in the calibration process                    |
| b = mark media sensing (three- digit value)      | Accepted Values: 000 to 100 Default Value: value calculated in the calibration process                    |
| c = mark LED sensing (three- digit value)        | Accepted Values: 000 to 100 Default Value: value calculated in the calibration process                    |

Example · Below is an example of a media sensor profile. Notice the numbers from 000 to 100 and where the words WEB, MEDIA, and RIBBON appear in relation to those numbers. Also notice the black vertical spike. This represents where the printer sensed the transition from media-to-web-to-media.

<!-- image -->

The media and sensor profiles produced vary in appearance from printer to printer.

Comments The m2 and r2 parameters have no effect in Stripe ® S -300 and S -500 printers.

Maximum values for parameters depend on which printer platform is being used.

<!-- image -->

<!-- image -->

## ^ST

## Set Date and Time (for Real-Time Clock)

Description The ^ST command sets the date and time of the Real-Time Clock.

<!-- formula-not-decoded -->

This table identifies the parameters for this format:

| Parameters   | Details                                                                  |
|--------------|--------------------------------------------------------------------------|
| a = month    | Accepted Values: 01 to 12 Default Value: current month                   |
| b = day      | Accepted Values: 01 to 31 Default Value: current day                     |
| c = year     | Accepted Values: 1998 to 2097 Default Value: current year                |
| d = hour     | Accepted Values: 00 to 23 Default Value: current hour                    |
| e = minute   | Accepted Values: 00 to 59 Default Value: current minute                  |
| f = second   | Accepted Values: 00 to 59 Default Value: current second                  |
| g = format   | Accepted Values: A = a.m. P = p.m. M = 24-hour military Default Value: M |

## ^SX

## Set ZebraNet Alert

Description The ^SX command is used to configure the ZebraNet Alert System.

Format ^SXa,b,c,d,e,f

This table identifies the parameters for this format:

Note · The values in this table apply to firmware V48\_12\_4 and above.

| Parameters         | Details                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
|--------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| a = condition type | Accepted Values: A = paper out B = ribbon out C = printhead over-temp D = printhead under-temp E = head open F = power supply over-temp G = ribbon-in warning (Direct Thermal Mode) H = rewind full I = cut error J = printer paused K = PQ job completed L = label ready M = head element out P = power on Q = clean printhead R = media low S = ribbon low T = replace head U = battery low V = all errors Default Value: if the parameter is missing or invalid, the command is ignored |

<!-- image -->

<!-- image -->

| Parameters                                           | Details                                                                                                                                                                                                                           |
|------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| b = destination for route alert                      | Accepted Values: A = serial port B* = parallel port C = e-mail address D = TCP/IP E = UDP/IP F = SNMP trap Default Value: if this parameter is missing or invalid, the command is ignored * Requires bidirectional communication. |
| c = enable condition set alert to this destination   | Accepted Values: Y (yes) or N (no) Default Value: Y or previously configured value                                                                                                                                                |
| d = enable condition clear alert to this destination | Accepted Values: Y (yes) or N (no) Default Value: N or previously configured value Parameters e and f are sub-options based on destination. If the sub-options are missing or invalid, these parameters is ignored.               |
| e = destination setting                              | Accepted Values: Internet e-mail address (e.g. user@company.com) IP address (for example, 10.1.2.123) SNMP trap IP or IPX addresses                                                                                               |
| f = port number                                      | Accepted Values: TCP port # ( 0 to 65535 ) UPD port # ( 0 to 65535 )                                                                                                                                                              |

Example · This is an example of the different ( b ) destinations that you can send for the condition type ( a ):

Serial:

^SXA,A,Y,Y

Parallel:

^SXA,B,Y,Y

E-Mail:

^SXA,C,Y,Y,admin@company.com

TCP: ^SXA,D,Y,Y,123.45.67.89,1234

UDP: ^SXA,E,Y,Y,123.45.67.89,1234

SNMP Trap: ^SXA,F,Y,Y,255.255.255.255

Comments In the example above for SNMP Trap, entering 255.255.255.255 broadcasts the notification to every SNMP manager on the network. To route the device to a single SNMP manager, enter a specific address (123.45.67.89).

## ^SZ

## Set ZPL

Description The ^SZ command is used to select the programming language used by the printer. This command gives you the ability to print labels formatted in both ZPL and ZPL II.

This command remains active until another ^SZ command is sent to the printer or the printer is turned off.

## Format ^SZa

This table identifies the parameters for this format:

| Parameters      | Details                                              |
|-----------------|------------------------------------------------------|
| a = ZPL version | Accepted Values: 1 = ZPL 2 = ZPL II Default Value: 2 |

Comments If the parameter is missing or invalid, the command is ignored.

<!-- image -->

<!-- image -->

~TA

## Tear-off Adjust Position

Description The ~TA command lets you adjust the rest position of the media after a label is printed, which changes the position at which the label is torn or cut.

Format ~TA###

Important · These are some important facts about this command:

- For 600 dpi printers, the step size doubles.
- If the number of characters is less than 3, the command is ignored.

This table identifies the parameters for this format:

| Parameters                                                                    | Details                                                                |
|-------------------------------------------------------------------------------|------------------------------------------------------------------------|
| ### = change in media rest position (3-digit value in dot rows must be used.) | Accepted Values: -120 to 120 Default Value: last permanent value saved |

Comments If the parameter is missing or invalid, the command is ignored.

<!-- image -->

<!-- image -->

## ^TO

## Transfer Object

Description The ^TO command is used to copy an object or group of objects from one storage device to another. It is similar to the copy function used in PCs.

Source and destination devices must be supplied and must be different and valid for the action specified. Invalid parameters cause the command to be ignored.

The asterisk (*) can be used as a wild card for object names and extensions. For instance, ZEBRA.* or * .GRF are acceptable forms for use with the ^TO command.

At least one source parameter ( d , o , or x ) and one destination parameter ( s , o , or x ) must be specified. If only ^TO is entered, the command is ignored.

Format ^TOd:o.x,s:o.x

This table identifies the parameters for this format:

| Parameters                                  | Details                                                                                                                                                      |
|---------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------|
| d = source device of stored object          | Accepted Values: R: , E: , B: , and A: Default Value: if a drive is not specified, all objects are transferred to the drive set in parameter s               |
| o = stored object name                      | Accepted Values: any existing object conforming to Zebra conventions Default Value: if a name is not specified, * is used -all objects are selected          |
| x = extension                               | Accepted Values: any extension conforming to Zebra conventions Default Value: if an extension is not specified, * is used -all extensions are selected       |
| s = destination device of the stored object | Accepted Values: R: , E: , B: , and A: Default Value: a destination must be specified                                                                        |
| o = name of the object at destination       | Accepted Values: up to 8 alphanumeric characters Default Value: if a name is not specified, the name of the existing object is used                          |
| x = extension                               | Accepted Values: any extension conforming to Zebra conventions Default Value: if an extension is not specified, the extension of the existing object is used |

Comments Parameters o , x , and s support the use of the wild card (*).

If the destination device does not have enough free space to store the object being copied, the command is canceled.

Zebra files ( Z:*.* ) cannot be transferred. These files are copyrighted by Zebra Technologies.

## Transferring Objects

These are some examples of using the ^TO command.

To copy the object ZLOGO.GRF from DRAM to an optional Memory Card and rename it ZLOGO1.GRF , write the following format:

```
^XA ^TOR:ZLOGO.GRF,B:ZLOGO1.GRF ^XZ
```

To copy the object SAMPLE.GRF from an optional Memory Card to DRAM and keep the same name, write this format:

```
^ XA ^TOB:SAMPLE.GRF,R:SAMPLE.GRF ^XZ
```

## Transferring Multiple Objects

The asterisk ( * ) can be used to transfer multiple object files (except *.FNT ) from DRAM to the Memory Card. For example, assume you have several object files that contain logos. These files are named LOGO1.GRF , LOGO2.GRF , and LOGO3.GRF .

To transfer all these files to the memory card using the name NEW instead of LOGO, place an asterisk after the names NEW and LOGO in the transfer command. This copies all files beginning with LOGO in one command.

```
^XA ^TOR:LOGO*.GRF,B:NEW*.GRF ^XZ
```

During a multiple transfer, if a file is too big to be stored on the memory card, that file is skipped. All remaining files attempt to be transferred. All files that can be stored within the space limitations are transferred, while other files are ignored.

<!-- image -->

~WC

## Print Configuration Label

Description The ~WC command is used to generate a printer configuration label. The printer configuration label contains information about the printer setup, such as sensor type, network ID, ZPL mode, firmware version, and descriptive data on the R: , E: , B: , and A: devices.

Format ~WC

Comments This command works only when the printer is idle.

FIRMWARE IN THIS PRINTER IS COPYRIGHTED

<!-- image -->

<!-- image -->

<!-- image -->

^WD

## Print Directory Label

Description The ^WD command is used to print a label listing bar codes, objects stored in DRAM, or fonts.

For bar codes, the list shows the name of the bar code. For fonts, the list shows the name of the font, the number to use with ^Af command, and size. For objects stored in DRAM, the list shows the name of the object, extension, size, and option flags. All lists are enclosed in a double-line box.

Format ~WDd:o.x

This table identifies the parameters for this format:

| Parameters                   | Details                                                                                                                                                                                                                                                                                                |
|------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| d = source device - optional | Accepted Values: R: , E: , B: , A: and Z: Default Value: R:                                                                                                                                                                                                                                            |
| o =object name- optional     | Accepted Values: 1 to 8 alphanumeric characters Default Value: * The use of a ? (question mark) is also allowed.                                                                                                                                                                                       |
| x = extension- optional      | Accepted Values: any extension conforming to Zebra conventions .FNT = font .BAR = bar code .ZPL = stored ZPL format .GRF = GRF graphic .CO = memory cache .DAT = font encoding .STO = data storage .PNG = PNG graphic * = all objects Default Value: * The use of a ? (question mark) is also allowed. |

Example •

```
To print a label listing all objects in DRAM, enter: ^XA ^WDR:*.* ^XZ
```

<!-- image -->

<!-- image -->

<!-- image -->

- Example · To print a label listing all resident bar codes, enter:

^XA ^WDZ:*.BAR ^XZ

- Example · To print a label listing all resident fonts, enter:

^XA ^WDZ:*.FNT ^XZ

<!-- image -->

<!-- image -->

^XA

## Start Format

Description The ^XA command is used at the beginning of ZPL II code. It is the opening bracket and indicates the start of a new label format. This command is substituted with a single ASCII control character STX (control-B, hexadecimal 02).

Format ^XA

Comments Valid ZPL II format requires that label formats should start with the ^XA command and end with the ^XZ command.

<!-- image -->

## ^XB

## Suppress Backfeed

Description The ^XB command suppresses forward feed of media to tear-off position depending on the current printer mode. Because no forward feed occurs, a backfeed before printing of the next label is not necessary; this improves throughput. When printing a batch of labels, the last label should not contain this command.

Format ^XB

## ^XB in the Tear-off Mode

Normal Operation:

backfeed, print, and feed to rest

^XB Operation:

print (Rewind Mode)

## ^XB in Peel-off Mode

Normal Operation:

backfeed, print, and feed to rest

^XB Operation:

print (Rewind Mode)

<!-- image -->

<!-- image -->

^XF

## Recall Format

Description The ^XF command recalls a stored format to be merged with variable data. There can be multiple ^XF commands in one format, and they can be located anywhere within the code.

When recalling a stored format and merging data using the ^FN (Field Number) function, the calling format must contain the ^FN command to merge the data properly.

While using stored formats reduces transmission time, no formatting time is saved. The ZPL II format being recalled is saved as text strings that need to be formatted at print time.

Format ^XFd:o.x

This table identifies the parameters for this format:

| Parameters                        | Details                                                                                                    |
|-----------------------------------|------------------------------------------------------------------------------------------------------------|
| d = source device of stored image | Accepted Values: R: , E: , B: , and A: Default Value: search priority ( R: , E: , B: , and A: )            |
| o = name of stored image          | Accepted Values: 1 to 8 alphanumeric characters Default Value: if a name is not specified, UNKNOWN is used |
| x = extension l                   | Fixed Value: .ZPL                                                                                          |

Example · This is an example of using the ^XF command to recall the format

- STOREFMT.ZPL from DRAM and insert new reference data in the ^FN fields:

## ZPL II CODE

## GENERATED LABEL

<!-- image -->

^XA

^XFR:STOREFMT.ZPL^FS

^FN1^FDZEBRA^FS

^FN2^FDLABEL^FS

^XZ

<!-- image -->

## ^XG

## Recall Graphic

Description The ^XG command is used to recall one or more graphic images for printing. This command is used in a label format to merge graphics, such as company logos and piece parts, with text data to form a complete label.

An image can be recalled and resized as many times as needed in each format. Other images and data might be added to the format.

Format ^XGd:o.x,mx,my

This table identifies the parameters for this format:

| Parameters                               | Details                                                                                                    |
|------------------------------------------|------------------------------------------------------------------------------------------------------------|
| d = source device of stored image        | Accepted Values: R: , E: , B: , and A: Default Value: search priority ( R: , E: , B: , and A: )            |
| o = name of stored image                 | Accepted Values: 1 to 8 alphanumeric characters Default Value: if a name is not specified, UNKNOWN is used |
| x = extension l                          | Fixed Value: .GRF                                                                                          |
| mx = magnification factor on the x- axis | Accepted Values: 1 to 10 Default Value: 1                                                                  |
| my = magnification factor on the y- axis | Accepted Values: 1 to 10 Default Value: 1                                                                  |

Example · This is an example of using the ^XG command to recall the image SAMPLE.GRF from DRAM and print it in five different sizes in five different locations on the same label:

^XA

^FO100,100^XGR:SAMPLE.GRF,1,1^FS

^FO100,200^XGR:SAMPLE.GRF,2,2^FS

^FO100,300^XGR:SAMPLE.GRF,3,3^FS

^FO100,400^XGR:SAMPLE.GRF,4,4^FS

^FO100,500^XGR:SAMPLE.GRF,5,5^FS

^XZ

<!-- image -->

<!-- image -->

<!-- image -->

^XZ

## End Format

Description The ^XZ command is the ending (closing) bracket. It indicates the end of a label format. When this command is received, a label prints. This command can also be issued as a single ASCII control character ETX (Control-C, hexadecimal 03).

Format ^XZ

Comments Label formats must start with the ^XA command and end with the ^XZ command to be in valid ZPL II format.

## ^ZZ

## Printer Sleep

Description The ^ZZ command places the printer in an idle or shutdown mode.

Format ^ZZt,b

This table identifies the parameters for this format:

| Parameters                                         | Details                                                                                                                                                |
|----------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------|
| t = number of second (idle time) prior to shutdown | Accepted Values: 0 to 999999 - setting 0 disables automatic shutdown Default@ Value: last permanently saved value or 0                                 |
| b = label status at shutdown                       | Accepted Values: Y = indicates to shutdown when labels are still queued N = indicates all labels must be printed before shutting down Default Value: N |

Comments The ^ZZ command is only valid on the PA400 and PT400 battery-powered printers.

<!-- image -->

<!-- image -->

<!-- image -->

Notes · \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

<!-- image -->

## RFID Commands

<!-- image -->

This section contains the ZPL II commands for RFID-specific applications.

For more information about the RFID commands, refer to the RFID Programming Guide . A copy is available on the User CD provided with your printer and online at http://www.zebra.com/manuals.

<!-- image -->

## RFID Command Overview

In addition to reading or encoding RFID tags, the RFID ZPL commands also provide for RFID exception handling, such as setting the number of read/write retries before declaring a transponder defective (set with ^RR , ^RT , and ^WT ) or setting the number of labels that will be attempted if an error occurs (set with ^RS ).

For example, if an RFID label fails to program correctly or if the transponder cannot be detected, the printer ejects the label and prints VOID across it. The printer will try to print another label with the same data and format for the number of RFID labels specified by the ^RS command. If the problem persists, the printer follows the error handling instructions specified by the ^RS command: the printer may remove the problematic format from the print queue and proceed with the next format (if one exists in the buffer), or it may place the printer in Pause or Error mode.

Important · Consider the following before using any command in this section:

- Each command lists the printers that support it. Before using a particular command, verify that your printer is listed.
- If a parameter in the following tables is designated as not applicable for a particular printer, any value entered for the parameter will be ignored, but the place holder for the field is required.

<!-- image -->

^HR

## Calibrate RFID Transponder Position

Description This command initiates an RFID transponder calibration for a specific RFID label and returns the results to the host computer. This calibration is used to determine the optimal programming position for RFID media that may not meet the transponder placement specifications for the printer.

<!-- image -->

Note · Do not perform transponder calibration for RFID media that meets the transponder placement specifications for your printer. Doing so will slow the printer's throughput unnecessarily. To order media that is designed for use with your RFID printer, contact your authorized Zebra reseller.

During transponder calibration, the printer feeds the RFID label one-dot row at a time while taking readings (via the READ TAG command and the WRITE TAG commands) to profile the RFID transponder. Based on the results, the printer determines the optimal programming position for the label and returns a results table to the host. The calibrated value is used as the programming position for the ^RS command, can be overwritten by the ^RS command, and is saved to nonvolatile memory (the value is saved even if the power is turned off).

This calibration takes into account the print mode, backfeed mode, and tear off position. The RUN option in the RFID TAG CALIB front panel parameter performs the same calibration but does not create a results table.

Important · If a label format specifies a value for parameter p (read/write position of the transponder) in the ^RS command, that value will be used for the programming position for all RFID labels until a new position is specified or until the printer is turned Off ( O ) and then back On ( I ).

## Printers That Support This Command

- RXi
- R110 PAX 4

Format

^HRa,b

This table identifies the parameters for this format.

| Parameters       | Details                                                                                                                |
|------------------|------------------------------------------------------------------------------------------------------------------------|
| a = start string | User text to appear before the results table. Accepted values: any string less than 65 characters Default value: start |
| b = end string   | User text to appear after the results table. Accepted values: any string less than 65 characters Default value: end    |

## Comments

- Based on the recommended transponder placement position for most RFID labels, the printer's default RFID programming position is zero for the R110 PAX 4. For other RFID printers, the default programming position is the label length minus 1 mm (0.04 in.). To return to the default programming position at any time, use the RESTORE option in the RFID TAG CALIB front panel parameter.
- At the end of calibration, a results table is returned to the host. Each line in the results table appears as:

Row, Read Result, Write Result

```
where Row = the dot row where calibration occurred Read Result = results of calibration (R = read, ' ' = unable to read) Write Result = results of calibration (W = write, ' ' = unable to write)
```

<!-- image -->

Example •

- If the following command is sent to the printer:

```
^XA^HR^XZ
```

The printer starts the transponder calibration and returns a results table such as the following:

```
start position=195 215, , 214, , 213, , 212, , 211, , 210, ,W 209,R, 208, , 207, , 206, ,W 205,R, 204, , 203, , 202, ,W 201,R,W 200,R,W 199,R,W 198,R,W 197,R,W 196,R,W 195,R,W <---**** 194,R,W 193,R,W 192,R,W 191,R,W 190,R,W 189,R, 188, , 187, , 186, , 185, , . . . end
```

In this example, the optimal programming position is 195. This is identified at the top of the table ( position=195 ) and with an the arrow ( &lt;---**** ) in the table.

<!-- image -->

^RB

## Define EPC Data Structure

Description This command defines the structure of EPC data, which can be read from or written to an RFID transponder. For more information about EPC specifications, refer to the EPC Global web site.

RFID transponders can have different partitions defined. This command specifies the number of partitions and how many bits are in each partition.

Important · All parameters in this command are persistent and will be used in subsequent formats if not provided. The values are initially set to the default values.

## Printers That Support This Command

- RXi
- R110 PAX 4

Format ^RBn,p0,p1,p2, ..., p15

This table identifies the parameters for this format.

| Parameters   | Parameters                    | Details                                                                                                                            |
|--------------|-------------------------------|------------------------------------------------------------------------------------------------------------------------------------|
| n            | = total bit size of the field | Accepted values: 1 to n , where n is the bit size of the tag. Default value: 96                                                    |
| p1           | ... p15 = partition sizes     | Specify each partition size. These must add up to the total bit size. Accepted values: 1 to 64 bit total bit size Default value: 1 |

Example 1 · The following command specifies that there are 96 bits used with three fields. Fields 1, 2, and 3 contain 10, 26, and 60 bits, respectively.

<!-- formula-not-decoded -->

The ZPL code to write to a tag with this format would look like this:

```
^RFW,E^FD1000.67108000.1122921504606846976^FS
```

When writing to the tag, the data will be stored in the tag in the following way:

- Field 1 contains 1000 . This value is stored in the first 10 bits
- Field 2 contains 67108000 . This value is stored in the next 26 bits.
- Field 3 contains 1122921504606846976 . This value is stored in the remaining 60 bits.

<!-- image -->

<!-- image -->

<!-- image -->

- Example 2 · The following command specifies that there are 64 bits used with eight 8-bit fields.

<!-- formula-not-decoded -->

The ZPL code to write to a tag with this format would look like this:

<!-- formula-not-decoded -->

When writing to the tag, each set of data is written in its respective 8-bit field.

Example 3 · This example uses the SGTIN-64 standard, which defines 64-bit structure in the following way:

|          | Header            | Filter Value         | Company Prefix Index      | Item Reference                     | Serial Number                 |
|----------|-------------------|----------------------|---------------------------|------------------------------------|-------------------------------|
| SGTIN-64 | 2 bits            | 3 bits               | 14 bits                   | 20 bits                            | 25 bits                       |
|          | 10 (binary value) | 8 (decimal capacity) | 16,383 (decimal capacity) | 9 to 1,048,575 (decimal capacity*) | 33,554,431 (decimal capacity) |

* Capacity of Item Reference field varies with the length of the company prefix.

The ZPL code to write to a tag with this format would look like this:

```
^XA ^RB64,2,3,14,20,25 ^RFW,E^FD0,3,12345,544332,22335221^FS ^XZ
```

These commands would put

- 0 in the header
- 3 as the filter value
- 12345 as the company prefix
- 544332 as the item reference
- 22335221 as the serial number

To read this EPC data and print the results on the label, you would use the following code:

```
^XA ^RB64,2,3,14,20,25 ^FO50,50^A0N,40^FN0^FS ^FN0^RFR,E^FS ^XZ
```

The resulting label would look like this:

0.3.12345.544332.22335221

<!-- image -->

<!-- image -->

^RF

## Read or Write RFID Format

Description This command allows you to read or write to an RFID tag.

<!-- image -->

Note · When using this command to read a tag, you may use a field variable to print the tag data on the label or to return the data to the host.

## Printers That Support This Command

- RXi
- R110 PAX 4

Format

^RFo,t,b

This table identifies the parameters for this format.

| Parameters                | Details                                                                                                                                            |
|---------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------|
| o = operation             | The action to be performed. Accepted values: W = write to the tag L = write with LOCK (if supported by tag type) R = read the tag Default value: W |
| t = type                  | Accepted values: A = ASCII H = Hexadecimal E = EPC (ensure proper setup with the ^RB command) Default value: H                                     |
| b = starting block number | Accepted values: 0 to n , where n is the maximum number of blocks for the tag. Default value: 0                                                    |

<!-- image -->

## Examples •

## Write ASCII

This example writes 96-bit data.

```
^XA ^RS4 ^RFw,a^FD00 my data^FS ^XZ
```

## Write Hex

This example writes 64-bit data.

```
^XA ^RS3 ^RFW,H^FD1122334455667788^FS ^XZ
```

## Write EPC

This example writes 96-bit data, as specified by the ^RB command.

```
^XA ^RB96,8,3,3,20,24,38 ^RFw,e^FD16,3,5,78742,146165,1234567891^FS ^XZ
```

<!-- image -->

<!-- image -->

^RM

## Enable RFID Motion

Description This command enables or disables RFID motion. By default, labels automatically print at the end of the format. This command allows you to inhibit the label from actually moving when it reaches the program position, which is useful for debugging, setup, and custom applications. This parameter is not persistent (carried over from label to label).

## Printers That Support This Command

- RXi
- R110 PAX 4

## Format ^RMe

This table identifies the parameters for this format.

| Parameters   | Details                                                                                 |
|--------------|-----------------------------------------------------------------------------------------|
| e = enable   | Accepted values: Y = Yes, move the label N = No, do not move the label Default value: Y |

<!-- image -->

## ^RN

## Detect Multiple RFID Tags in Encoding Field

Description This command enables or disables detection of multiple RFID tags in the encoding field. By default, the printer checks for more than one tag in the field before attempting to read or write. If more than one tag is found, the label over the antenna support is voided, and the RFID ERR STATUS parameter on the front panel displays MULTIPLE TAGS . To speed up printing and encoding by up to 200 ms, the check may be disabled. This parameter is persistent (carried over from label to label).

## Printers That Support This Command

- RXi with firmware version R60.13.03 or higher
- R110 PAX 4

Format ^RNe

The following table identifies the parameters for this format.

| Parameters   | Details                                                                                                   |
|--------------|-----------------------------------------------------------------------------------------------------------|
| e = enable   | Accepted Values: Y = Yes, check for multiple tags N = No, do not check for multiple tags Default Value: Y |

<!-- image -->

<!-- image -->

~RO

## Reset Advanced Counters

Description The ~RO command resets the advanced counters used by the printer to monitor label generation in inches and centimeters, the number of labels printed, and the number of valid and voided RFID labels. Any single error during programming of an RFID tag will result in that label being considered 'void' by the counter.

Four resettable counters are available. The values for the counters are displayed on the printer configuration label.

## Printers That Support This Command

- RXi
- R110 PAX 4

## Format ~ROc

This table identifies the parameters for this format:

| Parameters         | Details                                                                                                                                                                           |
|--------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| c = counter number | Accepted Values: 1 = counter 1 2 = counter 2 3 = valid RFID label counter 4 = voided RFID label counter Default Value: None. If a value is not specified, the command is ignored. |

Example 1 · This example shows how the counter portion of the printer configuration labels looks when counter 1 is reset by sending ~RO1 .

<!-- image -->

<!-- image -->

<!-- image -->

This example shows how the counter portion of the printer configuration labels

Example 2 · looks when the RFID counters are reset by sending ~RO3 and ~RO4 .

<!-- image -->

<!-- image -->

^RR

## Specify RFID Retries for a Block

Description This command changes the number of times that the printer attempts to read or write to a particular block of a single RFID tag. By default, the printer will attempt six retries. This command is persistent and will be used in subsequent formats if not provided.

<!-- image -->

<!-- image -->

Important · This command is not the same as the number of labels to try parameter in the ^RS command.

## Printers That Support This Command

- RXi
- R110 PAX 4

## Format ^RRn

This table identifies the parameters for this format.

| Parameters            | Details                                   |
|-----------------------|-------------------------------------------|
| n = number of retries | Accepted values: 0 to 10 Default value: 0 |

## Examples •

## Set read block retries to 5

```
^XA ^FN1^RR5^RFR,H^FS ^HV1^FS
```

^XZ

## Set write block retries to 2

```
^XA ^RR2^RFW,H^FD1234^FS ^XZ
```

## ^RS

## RFID Setup

Description This command sets up parameters including tag type, read/write position of the transponder, and error handling.

<!-- image -->

Important · Use care when using this command in combination with ^RT or ^RFR for reading tag data. Problems can occur if the data read from the tag is going to be printed on the label. Any data read from the transponder must be positioned to be printed above the read/write position. Failure to do this will prevent read data from being printed on the label.

## Printers That Support This Command

- RXi
- R110 PAX 4

Format ^RSt,p,v,n,e,a,c,s

This table identifies the parameters for this format.

<!-- image -->

| Parameters                                 | Details                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
|--------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| t = tag type                               | Accepted Values: 0 = None 1 = EPC Class 0 2 = EPC Class 0 Plus 3 = EPC Class 1 64-bit 4 = EPC Class 1 96-bit 5 = ISO 18000-06B Default value: 4 Because some countries restrict the frequencies that can be used for RFID, not all tag types listed may be supported by your RFID printer. If you specify a tag type that is not supported, the printer will use the default value.                                                                                                                                                                                                                    |
| p = read/write position of the transponder | Sets the read/write position of the transponder in the vertical (Y axis) in dot rows from the top of the label. Set to 0 (no movement) if the transponder is already in the effective area without moving the media. Important • If a label format specifies a value for this parameter, this value will be used for the programming position for all labels until a new position is specified or until the printer is powered Off ( O ) and then back On ( I ). Accepted values: 0 to label length Default value: For the R110 PAX 4: zero For other RFID printers: label length minus 1 mm(1/16 in.) |

<!-- image -->

| Parameters                       | Details                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
|----------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| v = length of void printout      | Sets the length of the void printout in vertical (Yaxis) dot rows. Accepted values: 0 to label length Default value: label length                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| n = number of labels             | The number of labels that will be attempted in case of read/encode failure. Accepted values: 1 to 10 Default value: 3                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| e = error handling               | If an error persists after the specified number of labels are tried, perform this error handling action. Accepted values: N = No action (printer drops the label format causing the error and moves to the next queued label) P = Place printer in Pause mode (label format stays in the queue until the user cancels) E = Place printer in Error mode (label format stays in the queue until the user cancels) Default value: N Note • You can set the printer to send an error message to the host for each failure. To enable or disable this unsolicited error message, refer to the ^SX and ^SQ ZPL |
| a = signals on applicator        | When the value for parameter p (read/write position of the transponder) is nonzero, this parameter changes the number of start and stop print signals required for printing. In Single mode, one start print command is required. In Double mode, two are required, so the printer will resume printing only after the second start print command is received. Accepted values: S = single signal D = double signal Default value: S                                                                                                                                                                     |
| c = certify tag with a pre-read* | * Not used in this version of the printer. The encoder does this automatically.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| s = void print speed             | If a label is voided, the speed at which 'VOID' will be printed across the label. Accepted values: any valid print speed Default value: the printer's maximum print speed                                                                                                                                                                                                                                                                                                                                                                                                                                |

<!-- image -->

Example 1 · This example sets the printer to move the media to 800 dots from the top of the media [or label length minus 800 from the bottom (leading edge) of the media] and voids the rest of the media in case of an error. The printer will try to print two labels and then will pause if printing and encoding fail.

```
^XA ^RS,800,,2,P^FS ^XZ
```

Figure 2 shows the resulting voided label. Note where the void starts. The media has been moved 800 dot rows from the top of the label (label length minus 800 dot rows from the bottom (leading edge) of a label) to bring the transponder into the effective area to read/write a tag. If the printer fails the operation, the rest of the media is voided.

Figure 2 • Sample Void Label, Remainder of Label Voided

<!-- image -->

<!-- image -->

Example 2 · This example sets the printer to move the media to 800 dots from the top of the media [or label length - 500 from the bottom (leading edge) of the media] and prints 'VOID' 500 dots in vertical length (Y axis) in case of an error.

```
^XA ^RS,800,500,2,P^FS ^XZ
```

Figure 3 shows the resulting voided label. Note where the void starts. The media has been moved 800 dot rows from the top of the label [label length minus 800 dot rows from the bottom (leading edge) of a label] to bring the transponder into the effective area to read/write a tag. If the printer fails the operation, an area that is 500 dot rows of the media is voided instead of the entire rest of the media.

Figure 3 • Sample Void Label, 500 Dot Row Area Voided

<!-- image -->

<!-- image -->

## ^RT

## Read RFID Tag

Description This command tells the printer to read the current RFID tag data. The data can be sent back to the host via the ^HV command.

<!-- image -->

Note · It is recommended that you use the ^RF , ^RM , and ^RR commands rather than the ^RT command. The ^RT command is provided only for backward-compatibility with label formats that were developed for other Zebra RFID printers.

## Printers That Support This Command

- RXi
- R110 PAX 4

Format

^RT#,b,n,f,r,m

This table identifies the parameters for this format.

| Parameters                             | Details                                                                                                                                                                                                                                                                                      |
|----------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| # = number to be assigned to the field | Accepted values: 0 to 9999 Default value: 0                                                                                                                                                                                                                                                  |
| b = starting block number              | Accepted values: 0 to n , where n is the maximum number of blocks for the tag. Default value: 0                                                                                                                                                                                              |
| n = number of blocks to read*          | Accepted values: 1 to n , where n is the maximum number of blocks for the tag type minus the starting block number. For example, if the tag has 8 blocks (starting with block 0) and you start with block 6, n can be 2. This would return block 6 and block 7 information. Default value: 1 |
| f = format                             | Accepted values: 0 = ASCII 1 = Hexadecimal Default value: 0                                                                                                                                                                                                                                  |

*Not applicable for RFID printers supported by this Volume One.

<!-- image -->

| Parameters            | Details                                                                                                                                                                                 |
|-----------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| r = number of retries | Changes the number of times that the printer attempts to read a particular block of a single RFID tag. (Same retry rules as the ^RR command.) Accepted values: 0 to 10 Default value: 0 |
| m = motion            | Enables or disables RFID motion for the current field. Accepted values: 0 = Feed label after writing. 1 = No feed after writing. Other ZPL may cause a feed. Default value: 0           |

*Not applicable for RFID printers supported by this Volume One.

Example · This sample reads a tag, prints the data on a label, and sends the string Tag Data: xxxxxxxx back to the host. The data read will go into the ^FN1 location of the format. The printer will retry the command five times, if necessary.

^XA

^FO20,120^A0N,60^FN1^FS

^RT1,,,,5^FS

^HV1,,Tag Data:^FS

^XZ

<!-- image -->

## ^RW

## Set RFID Read and Write Power Levels

Description This command sets the read and write power levels. This function is useful when using different tag types or transponders that require different power levels to obtain the best read and write abilities.

## Printers That Support This Command

- RXi
- R110 PAX 4

Format ^RWr,w

This table identifies the parameters for this format:

| Parameters      | Details                                                                                                                                      |
|-----------------|----------------------------------------------------------------------------------------------------------------------------------------------|
| r = read power  | Sets the power level to match the desired output as calibrated in the factory. Accepted Values: H = high M = medium L = low Default Value: H |
| w = write power | Sets the power level to match the desired output as calibrated in the factory. Accepted Values: H = high M = medium L = low Default Value: H |

<!-- image -->

<!-- image -->

## ^RZ

## Set RFID Tag Password

Description This command lets you define the password for the tag during writing.

<!-- image -->

Important · Only certain tags support this feature, so check to ensure that this command can be used with your particular tag type.

## Printers That Support This Command

- RXi
- R110 PAX 4

Format

^RZp

The following table identifies the parameters for this format.

| Parameters   | Details                                                   |
|--------------|-----------------------------------------------------------|
| p = password | Accepted values: 00 to FF (hexadecimal) Default value: 00 |

<!-- image -->

## ^WT

## Write Tag

Description This command allows you to program the current RFID tag.

<!-- image -->

<!-- image -->

Note · It is recommended that you use the ^RF , ^RM , ^RR , and ^WV commands rather than the ^WT command. The ^WT command is provided only for backward-compatibility with label formats that were developed for older Zebra RFID printers.

Important · Check the amount of data memory available for the tag that you will be using. If more is sent than the memory can hold, the printer truncates the data.

## Printers That Support This Command

- RXi
- R110 PAX 4

Format ^WTb,r,m,w,f,v

This table identifies the parameters for this format.

| Parameters            | Details                                                                                                                                                                                                                           |
|-----------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| b = block number      | This parameter is tag-dependent. For most tags, use block 0. For EPC Class 0 Plus, block 0 is EPC data, and block 1 is user data. Accepted values: 0 to n , where n is the maximum number of blocks for the tag. Default value: 0 |
| r = number of retries | Changes the number of times that the printer attempts to write to a particular block of a single RFID tag. (Same function as the ^RR command.) Accepted values: 0 to 10 Default value: 0                                          |
| m = motion            | Enables or disables RFID motion. (Same function as the ^RM command.) Accepted values: 0 = Feed label after writing.) 1 = No Feed after writing. Other ZPL may cause a feed. Default value: 0                                      |
| w = write protect     | Accepted values: 0 = Not write protected. 1 = Write protect. Default value: 0                                                                                                                                                     |

<!-- image -->

| Parameters            | Details                                                                                                                                                                                                                                                                                                          |
|-----------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| f = data format       | Accepted values: 0 = ASCII 1 = Hexadecimal Default value: 0                                                                                                                                                                                                                                                      |
| v = verify valid data | For reliability, some manufacturers encode tags with known data (such as A5A5 ). This parameter flags whether the preprogrammed data is verified. (Same function as the ^WV command) Accepted values: N = Do not verify Y = Verify valid data [Hex A5A5 in the first two bytes] before writing) Default value: N |

Example · This sample encodes data 'RFIDRFID' and will try writing up to five times, if necessary.

<!-- formula-not-decoded -->

<!-- image -->

## ^WV

## Verify RFID Write Operation

Description If write verify is enabled, this command verifies the RFID write operation to ensure that the tag about to be programmed contains the hex data 'A5A5' in the first two bytes. This parameter is not persistent (carried over from label to label).

## Printers That Support This Command

- RXi
- R110 PAX 4

Format ^WVe

This table identifies the parameters for this format.

| Parameters   | Details                                  |
|--------------|------------------------------------------|
| e = enable   | Accepted values: Y or N Default value: N |

<!-- image -->

<!-- image -->

Notes · \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

<!-- image -->

B

## Wireless Print Server Commands

This section contains new or modified ZPL commands for the Wireless Print Server.

<!-- image -->

<!-- image -->

^KP

## Define Printer Password

Description The ^KP command defines the password that must be entered to modify the printer's parameters. This is different from the wireless password.

Format ^KPa

This table identifies the parameters for this format:

| Parameters                        | Details                                           |
|-----------------------------------|---------------------------------------------------|
| a = mandatory four-digit password | Accepted Values: 0000 to 9999 Default Value: 1234 |

Comments If you forget the printer's password, you can return all printer parameters to the factory defaults, which resets the password to 1234 . Print a configuration label to use as a baseline before using this option because all printer parameters are set back to their defaults. Refer to the user guide for your printer for instructions for printing a configuration label.

<!-- image -->

^NB

## Search for Wired Print Server during Network Boot

Description The ^NB command tells the printer to search for a wired print server at bootup.

Format ^NBa

This table identifies the parameters for this format:

Table 12 shows the results of this check:

| Parameters                                    | Details                                                     |
|-----------------------------------------------|-------------------------------------------------------------|
| a = Check for Wired Print Server at Boot Time | Accepted Values: C (check), S (skip check) Default Value: S |

Table 12 • Results of Check for Wired Print Server

| Wired Print Server Connected?   | Checkfor Wired Print Server?   | Results                                                                                                                                                                                                           |
|---------------------------------|--------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Yes                             | Skip                           | The printer skips the check for a wired print server. The wired print server is not acknowledged, and the Wireless Print Server is used as the primary print server.                                              |
| Yes                             | Check                          | The printer checks for a wired print server. If the wired print server is detected, it is used as the primary print server. If it is not detected, the Wireless Print Server is used as the primary print server. |
| No                              | Skip                           | The printer uses the Wireless Print Server as the primary print server without taking the time to check for a wired print server.                                                                                 |
| No                              | Check                          | During bootup, the printer tries for 70 seconds to detect a wired print server. If the printer cannot find one, it uses the wireless print server as the primary print server.                                    |

<!-- image -->

^NN

## Set SNMP

Description The ^NN command sets the SNMP (Simple Network Management Protocol) parameters.

Format ^NNa,b,c,d,e,f

This table identifies the parameters for this format:

Important · If a parameter does not have a default value, the printer uses the previously defined value.

| Parameters              | Details                                                                                                          |
|-------------------------|------------------------------------------------------------------------------------------------------------------|
| a = system name         | Same as printer name. Accepted Values: Up to 17 alphanumeric characters                                          |
| b = system contact      | Any contact information as desired (such as a name or phrase). Accepted Values: Up to 50 alphanumeric characters |
| c = system location     | The printer's model information. Accepted Values: Up to 50 alphanumeric characters                               |
| d = get community name  | Accepted Values: Up to 20 alphanumeric characters Default Value: public                                          |
| e = set community name  | Accepted Values: Up to 20 alphanumeric characters Default Value: public                                          |
| f = trap community name | Accepted Values: Up to 20 alphanumeric characters Default Value: public                                          |

<!-- image -->

<!-- image -->

^NP

## Set Primary/Secondary Device

Description The ^NP command specifies to use the printer's or the print server's LAN/WLAN settings at boot time. The default is to use the printer's settings.

When the printer is set as the primary device, you can set it up using ZPL commands or the SetWLAN utility, and any wired print server inserted into the printer will get these settings.

Important · If you use the printer as primary, any wired print server inserted into the printer loses the original settings if the printer is set to check for the wired print server (see ^NB on page 307 ) and using gleaning only for IP protocol does not work.

Format ^NPa

This table identifies the parameters for this format:

Important · If a parameter does not have a default value, the printer uses the previously defined value.

| Parameters                   | Details                                            |
|------------------------------|----------------------------------------------------|
| a = Device to Use as Primary | Accepted Values: P (printer), M (MPS/print server) |

<!-- image -->

<!-- image -->

<!-- image -->

^NS

## Change Wired Networking Settings

Description The ^NS command changes the wired print server network settings.

Format ^NSa,b,c,d,e,f,g,h,i

This table identifies the parameters for this format:

Important · If a parameter does not have a default value, the printer uses the previously defined value.

| Parameters                      | Details                                                                                                                                                                                                           |
|---------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| a = IP resolution               | Accepted Values: A = (all) B = (BOOTP) C = (DHCP and BOOTP) D = (DHCP) G = (gleaning only) R = (RARP) P = (permanent) Note • Use of gleaning only is not recommended when the Wireless Print Server is installed. |
| b = IP address                  | Accepted Values: Any properly formatted IP address in the xxx.xxx.xxx.xxx format.                                                                                                                                 |
| c = subnet mask                 | Accepted Values: Any properly formatted subnet mask in the xxx.xxx.xxx.xxx format.                                                                                                                                |
| d = default gateway             | Accepted Values: Any properly formatted gateway in the xxx.xxx.xxx.xxx format.                                                                                                                                    |
| e = WINS server address         | Accepted Values: Any properly formatted WINS server in the xxx.xxx.xxx.xxx format.                                                                                                                                |
| f = connection timeout checking | Accepted Values: Y (yes), N (no)                                                                                                                                                                                  |
| g = timeout value               | Time, in seconds, before the connection times out. Accepted Values: 0 through 9999                                                                                                                                |
| h = ARP broadcast interval      | Time, in minutes, that the broadcast is sent to update the device's ARP cache.                                                                                                                                    |
| i = base raw port number        | The port number that the printer should use for its RAW data. Accepted Values: 0 through 99999 Default Value: 9100                                                                                                |

<!-- image -->

<!-- image -->

<!-- image -->

^NT

## Set SMTP

Description The ^NT command sets the Simple Mail Transfer Protocol (SMTP) parameters, which allows you to set the e-mail settings for alerts.

Format ^NTa,b

This table identifies the parameters for this format:

Important · The parameters in this table that do not have a Default Value use what ever is currently defined.

| Parameters              | Details                                                                                   |
|-------------------------|-------------------------------------------------------------------------------------------|
| a = SMTP Server Address | Accepted Values: Any properly formatted server address in the xxx.xxx.xxx.xxx format      |
| b = Print Server Domain | Accepted Values: Any properly formatted print server domain in the xxx.xxx.xxx.xxx format |

<!-- image -->

^NW

## Set Web Authentication Timeout Value

Description The ^NW command sets the timeout value for the printer home page. The printer prompts for the printer password only the first time that certain screens are accessed until 1) the web authentication timeout value is reached (default value is 5 minutes) or 2) the printer is reset. At that time, the printer prompts for the password again.

## Format ^NWa

The following table identifies the parameters for this format.

| Parameters        | Details                                                                                                                                                                                                                 |
|-------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| a = Timeout Value | The timeout value in minutes for an IP address to be authenticated to the printer web pages. Accepted Values: 0 (no secure pages can be accessed without entering the printer password) to 255 minutes Default Value: 5 |

<!-- image -->

^WA

## Set Antenna Parameters

Description The ^WA command sets the values for the receive and transmit antenna.

Format ^WAa,b

This table identifies the parameters for this format:

| Parameters           | Details                                                              |
|----------------------|----------------------------------------------------------------------|
| a = receive antenna  | Accepted Values: D (diversity), L (left), R (right) Default Value: D |
| b = transmit antenna | Accepted Values: D (diversity), L (left), R (right) Default Value: D |

<!-- image -->

## ^WE

## Set Wireless Encryption Values

Description The ^WE command sets WEP (wireless encryption) values.

Format ^WEa,b,c,d,e,f,g,h

Important · Be sure to include the exact number of commas required in this command when setting encryption keys (parameters e through h ). A missing or extra comma in this command causes the keys to be stored in the wrong slots and can disable the wireless system.

This table identifies the parameters for this format:

| Parameters                               | Details                                                                                                                                                                                                                                                                                                                                                                                         |
|------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| a = encryption mode                      | Accepted Values: OFF, 40 (40-bit encryption), 128 (128-bit encryption) Default Value: OFF                                                                                                                                                                                                                                                                                                       |
| b = encryption index                     | Tells the printer which encryption key to use. Accepted Values: 1 (key 1), 2 (key 2), 3 (key 3), 4 (key 4) Default Value: 1                                                                                                                                                                                                                                                                     |
| c = authentication type                  | Accepted Values: O (open system), S (shared key) Default Value: O If you enabled Shared Key authentication with Encryption Mode set to OFF, this value resets to Open.                                                                                                                                                                                                                          |
| d = encryption key storage               | Accepted Values: H (hex key storage), S (string key storage) Default Value: S                                                                                                                                                                                                                                                                                                                   |
| e, f, g, h = encryption keys 1 through 4 | Accepted Values: The actual value for the encryption key The encryption mode affects what can be entered for the encryption keys: • For 40-bit, encryption keys can be set to any 5 hex pairs or any 10 alphanumeric character. • For 128-bit, encryption keys can be set to any 13 hex pairs or any 26 alphanumeric character. When using hex storage, do not add a leading 0x on the WEP key. |

Example 1 · This example sets encryption to 40-bit, activates encryption key 1, and sets encryption key 1 to the string 12345 . Encryption Key Storage parameters are left blank with commas as placeholders for the fields. The printer uses the default values for these parameters, as follow:

^WE40,,,,12345

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

- .This example sets encryption to 128-bit, activates encryption key 2, and sets

Example 2 · encryption keys 1 and 2 to hex values:

```
^WE128,2,,H,12345678901234567890123456,98765432109876543 210987654
```

The value for encryption key 1 is stored and can be activated in the future by the following command:

```
^WE128,1
```

- Example 3 · This example sets encryption to 128-bit, activates encryption key 4, and sets encryption key 4 to a hex value:

```
^WE128,4,,H,,,,98765432109876543210987654
```

Values are not required for encryption keys 1 through 3 when setting encryption key 4. In this example, commas are used as placeholders for the fields for encryption keys 1 through 3. Any previously stored values for these encryption keys do not change.

Important · Make sure that you include the exact number of commas required to get to the slot for encryption key 4 (parameter h ).

<!-- image -->

## ^WI

## Change Wireless Network Settings

Description The ^WI command changes the wireless network settings.

Format ^WIa,b,c,d,e,f,g,h,i

This table identifies the parameters for this format:

Important · If a parameter does not have a default value, the printer uses the previously defined value.

| Parameters                      | Details                                                                                                                                                                                      |
|---------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| a = IP resolution               | Accepted Values: A = all B = BOOTP C = DHCP and BOOTP D = DHCP G = gleaning only R = RARP P = permanent Use of gleaning only is not recommended when the Wireless Print Server is installed. |
| b = IP address                  | Accepted Values: Any properly formatted IP address in the xxx.xxx.xxx.xxx format.                                                                                                            |
| c = subnet mask                 | Accepted Values: Any properly formatted subnet mask in the xxx.xxx.xxx.xxx format.                                                                                                           |
| d = default gateway             | Accepted Values: Any properly formatted gateway in the xxx.xxx.xxx.xxx format.                                                                                                               |
| e = WINS server address         | Accepted Values: Any properly formatted WINS server in the xxx.xxx.xxx.xxx format.                                                                                                           |
| f = connection timeout checking | Accepted Values: Y (yes), N (no)                                                                                                                                                             |
| g = timeout value               | Time, in seconds, before the connection times out. Accepted Values: 0 through 9999                                                                                                           |
| h = ARP broadcast interval      | Time, in minutes, that the broadcast is sent to update devices ARP cache.                                                                                                                    |
| i = base raw port number        | The port number that the printer should use for its RAW data. Accepted Values: 0 through 99999 Default Value: 9100                                                                           |

<!-- image -->

<!-- image -->

^WL

## Set LEAP Parameters

Description The ^WL command sets the LEAP mode, user name, and password.

<!-- image -->

Note · LEAP is only available with some wireless cards.

Format ^WLa,b,c

This table identifies the parameters for this format.

| Parameters    | Details                                              |
|---------------|------------------------------------------------------|
| a = mode      | Accepted Values: OFF , ON                            |
| b = user name | Accepted Values: Any 4 to 40 alphanumeric characters |
| c = password  | Accepted Values: Any 4 to 40 alphanumeric characters |

<!-- image -->

~WL

## Print Network Configuration Label

Description The ~WL command generates a network configuration label (Figure 4).

Format ~WL

Figure 4 • Network Configuration Label

<!-- image -->

FIRMWARE IN THIS PRINTER IS COPYRIGHTED

<!-- image -->

^WP

## Set Wireless Password

Description The ^WP command sets the four-digit wireless password (not the same as the general printer password). If the wireless password is 0000 , the Wireless Print Server runs in an 'unprotected' mode, which means that you do not need to enter the password through the front panel to view or modify wireless settings.

If a wireless password is set, the values for the following parameters will not appear through the front panel until the wireless password is entered:

- MAC Address
- ESSID
- Auth Type
- Leap Mode (if applicable)
- Encryption Mode
- Encryption Index
- Reset Network

Format ^WPa,b

This table identifies the parameters for this format.

| Parameters                | Details                                                |
|---------------------------|--------------------------------------------------------|
| a = old wireless password | Accepted Values: 0000 through 9999 Default Value: 0000 |
| b = new wireless password | Accepted Values: 0000 through 9999 Default Value: 0000 |

<!-- image -->

## ^WR

## Set Transmit Rate

Description The ^WR command changes the transmission parameters.

Format ^WRa,b,c,d,e

This table identifies the parameters for this format:

Important · If a parameter does not have a default value, the printer uses the previously defined value.

| Parameters         | Details                                                           |
|--------------------|-------------------------------------------------------------------|
| a = rate 1         | Sets the 1 Mb/s transmit rate. Accepted Values: Y (On), N (Off)   |
| b = rate 2         | Sets the 2 Mb/s transmit rate. Accepted Values: Y (On), N (Off)   |
| c = rate 5.5       | Sets the 5.5 Mb/s transmit rate. Accepted Values: Y (On), N (Off) |
| d = rate 11        | Sets the 11 Mb/s transmit rate. Accepted Values: Y (On), N (Off)  |
| e = transmit power | Accepted Values: 1 , 5 , 20 , 30 , 50 , 100                       |

<!-- image -->

<!-- image -->

~WR

## Reset Wireless Card

Description The ~WR command reinitializes the wireless card and the print server when the Wireless Print Server is running.

Format ~WR

<!-- image -->

## ^WS

## Set Wireless Card Values

Description The ^WS command sets the wireless card values for ESSID, Operating Mode, and Card Preamble.

Format ^WSe,o,p

This table identifies the parameters for this format:

| Parameters                 | Details                                                                                                                                                                                                           |
|----------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| e = ESSID value            | Accepted Values: Any value up to 32 characters, including all ASCII and Extended ASCII characters, including the space character. When this parameter is left blank, the ESSID is not changed. Default Value: 125 |
| o = operating mode         | Accepted Values: I (infrastructure), A (adhoc) Default Value: I                                                                                                                                                   |
| p = wireless card preamble | Accepted Values: L (long), S (short) Default Value: L                                                                                                                                                             |

<!-- image -->

Notes · \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

## Symbols

^KP , define printer password, 306

^MW, 228

^NB , network boot, 307

^NN , set SNMP parameters, 308

^NP , set primary/secondary device, 309

^NS , change wired network settings, 310

^NT , set SMTP, 312

^NW , set web authentication timeout value, 313

^WA , set antenna parameters, 314

^WE , set wireless encryption values, 315

^WI , change wireless network settings, 317

^WL , set LEAP parameters, 318

^WP , set wireless password, 320

^WR , set transmit rate, 321

~WL , print network configuration label, 319

- ~WR , reset wireless card, 322

~WS , set wireless card values, 323

## A

abort download graphic, 126

authentication timeout for printer home page, 313

advanced counter reset, 246 advanced counter reset, 290 alphanumeric default font change, 107 antenna parameter setting via ZPL, 314 applicator reprint, 243 authentication type setting via ZPL command, 315 auxiliary port set, 192

## B

backfeed sequence change, 200, 201 bar code field default, 101 battery set condition, 190 battery status, 160 bitmap font download, 120 box, 151

## C

cache on, 113 calibration RFID tag using ZPL (^HR), 281 Canadian DOC compliance, xiv cancel all, 184 cancel format, 198 caret change, 105 change alphanumeric default font, 107 change backfeed sequence, 200, 201 change caret, 105 change delimiter, 106 change international font, 109 change memory letter designation, 112 change network settings, 232 change tilde, 115 change wired network settings, 310 circle, 153 CODABLOCK, 43

considerations for ^FD character set, 46

considerations for the ^BY, 45

## Index

<!-- image -->

```
code 11, 17 code 128 subsets, 49 subsets A and C, 52 subsets a, b, and c, 47 code 39, 21 code 49, 25 automatic mode, 28 field data character set, 28 code 93, 39 full ASCII mode, 41 code validation, 116 comment, 150 communications diagnostics, 188 enable, 188 configuation update, 204 configuration using ZPL commands, 305 configuration label print, 269 contact information, xvi counter reset (~RO), 290 current partially input format cancel, 206 currently connected printer set transparent, 233 customer support, xvii
```

```
D darkness set, 248 data matrix, 97 date for real time clock set, 262 define EPC data structure (^RB), 284 define language, 210 define password, 212 define printer name, 211 define printer password via ZPL, 306 delete object, 177 delimiter change, 106 description information display, 175 detect multiple RFID tags (^RN), 289 diagnostics disable, 189 diagonal line, 154 directory label print, 270 disable diagnostics, 189
```

```
discharge mode battery, 208 display description information, 175 download bitmap font, 120 download encoding, 122 download format, 123 download graphic abort, 126 download graphics, 124, 130 download scalable font, 127 download true type font, 128 download unbounded true type font, 129
```

## E

```
EAN-13, 63 EAN-8, 35 Electronic Product Code (EPC) define EPC data structure (^RB), 284 ellipse, 155 enable RFID motion (^RM), 288 encoding download, 122 select, 249 encryption set LEAP parameters, 318 set values via ZPL, 315 end format, 276 erase download graphics, 131 ESSID setting via ZPL, 323
```

## F

```
FCC compliance, xiii feedback suppress, 273 field field reverse, 142 orientation, 149 parameter, 141 separator, 143 typeset, 144 variable, 148 field block, 131, 132 field clock real time clock, 134 field data, 135 field hexadecimal indicator, 136 field number, 139 field orientation, 149 field origin, 140 field parameter, 141
```

```
field reverse print, 142 field separator, 143 field typeset, 144 field variable, 148 flash memory initialize, 185 font identifier, 118 font name to call font, 15 fonts p-v, 14 format cancel, 198 download, 123 end, 276 pause, 198 recall, 274
```

set, 272

## G

## graphic

box, 151 circle, 153 diagonal line, 154 ellipse, 155 field, 156 recall, 275 symbol, 158 graphic field, 156 graphics download, 124, 130 erase download, 131 upload, 174

graphing sensor calibration, 191

## H

head test fatal, 196 interval, 203 non-fatal, 197 head test fatal, 196 head test interval, 203 head test non-fatal, 197 host directory list, 172 graphic, 163 identification, 165 RAM status, 166 status return, 167 host directory list, 172 host graphic, 163

host identification, 165

host RAM status, 166

host status return, 167

host verification command (^HV), 171

## I

image load, 179 move, 181 save, 182 image load, 179 image move, 181 image save, 182 industrial 2 of 5, 68 initialize Flash memory, 185 interleaved 2 of 5, 19 international font change, 109

## K

kill battery, 208

## L

label maximum length, 221 reverse print, 215 shift, 216 top, 217 label home, 213 label length, 214 set, 194 language define, 210 LEAP mode setting using ZPL, 318 liability, xiv LOGMARS, 74

## M

```
map clear, 218 maximum label length, 221 media darkness, 219 feed, 220 tracking, 223 type, 225 media darkness, 219 media sensor set, 260
```

```
media sensor calibration, 187 set, 187 media tracking, 223 media type, 225 memory letter designation change, 112 mirror image printing, 236 mode protection, 224 modify head warning, 228 motion in RFID label, 288 MSI, 76 multiple field origin locations, 137
```

## N

network change settings, 232 connect, 229 ID number, 230 network boot command, 307 network configuration label print via ZPL, 319 network connect, 229 network ID number, 230 network printers set all transparent, 231 network settings setting via ZPL, 317 number of retries for block (^RR), 292

## O

object delete, 177 offset for real time clock set, 255 optional memory reset, 186

## P

```
password define, 212 set printer password, 306 set wireless password, 320 passwords RFID tag password, 300 pause programmable, 238 pause format, 198 PDF417, 30 consideration for ^FD, 34 POSTNET, 103
```

```
power on reset, 199 primary/secondary device setting via ZPL, 309 print start, 244 width, 245 print mode, 222 print network configuration label via ZPL command, 319 print orientation, 237 print quantity, 239 print rate, 240 print start, 244 print width, 245 printer sleep, 277 printer name define, 211 printer password setting, 306 printer sleep, 277 printer web pages set timeout value, 313 printhead resistance set, 259 printing mirror image of label, 236 programmable pause, 238 proprietary statement, xiii
```

## Q

QR code normal mode, 84 quantity print, 239

## R

```
read power change using ZPL, 299 read RFID tag read or write RFID format (^RF), 286 read RFID tag (^RT), 297 real time clock set language, 252 set mode, 252 real time clock date format select, 209 real time clock time format select, 209 recall format, 274 recall graphic, 275 related documents, xviii
```

```
reprint after error, 207 applicator, 243 reset power on, 199 reset advanced counter, 246, 290 reset advanced counters (~RO), 290 reset optional memory, 186 reset wireless card, 322 return data to host computer (^HV), 171 RFID calibrate RFID tag using ZPL (^HR), 281 change read power using ZPL, 299 change write power using ZPL, 299 detect multiple tags, 289 enable motion, 288 number of retries for block (^RR), 292 RFID setup command (^RS), 293 verify write operation (^WV), 303 ribbon tension set, 205
```

## S

scalable font, 12 download, 127 select encoding, 249 sensor calibration graphing, 191 serial communications set, 247 serialization data, 253 serialization field standard ^FD string, 250 set all network printers transparent, 231 set auxiliary port, 192 set battery condition, 190 set darkness, 248 set dots millimeter, 195 set dots per millimeter, 195 set label length, 194 set RFID tag password (^RZ), 300 set serial communications, 247 set units of measurements, 226 SGTIN-64 standard programming example, 285 slew home position, 235 slew given number dot rows, 234 slew to home position, 235 SMTP parameters setting via ZPL, 312

SNMP parameters setting via ZPL, 308 specify number of retries for block (^RR), 292 start print, 256 support, xvii symbol, 158, 162

## T

tear-off adjust position, 266 tilde change, 115 time for real time clock set, 262 timeout value for printer home page, 313 transfer object, 267 transmit rate setting via ZPL, 321 transponders calibration using ZPL (^HR), 281 true type font download, 128

## U

unbounded true type font download, 129 units of measurement set, 226 UPC/EAN extensions, 90 UPC-A, 95 UPC-E, 37 update configuration, 204 upload graphics, 174 UPS maxicode, 60 considerations for ^FD, 61 use font name to call font, 15

## V

verify RFID write operation (^WV), 303

## W

web authentication timeout value, 313 width print, 245 wired print server ^NB to set check for, 307 change network settings, 310 wireless card reset via ZPL, 322 setting values via ZPL, 323 wireless password setting via ZPL, 320

Wireless Print Server change network settings, 317 ZPL commands, 305 write power change using ZPL, 299 write RFID format (^RF), 286 write RFID tag (^WT), 301

## Z

Zebra support, xvii ZebraNet Alert halt, 258 set, 263 ZPL set, 265 ZPL commands ^B7, 30

Wireless Print Server commands, 305

<!-- image -->

## Zebra Technologies Corporation

333 Corporate Woods Parkway Vernon Hills, Illinois 60061.3109 U.S.A. Telephone: +1 847.634.6700 Facsimile: +1 847.913.8766

## Zebra Technologies Europe Limited

Zebra House The Valley Centre, Gordon Road High Wycombe Buckinghamshire HP13 6EQ, UK Telephone: +44 (0) 1494 472872 Facsimile: +44 (0) 1494 450103

## Part # 45541L-002 Rev. A

