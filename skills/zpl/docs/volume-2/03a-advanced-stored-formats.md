<!-- Source: ZPL II Programming Guide Volume 2 -->
<!-- Section: Chapter 3: Advanced Techniques - Stored Formats & Serialization -->
<!-- Generated: 2025-11-02 04:52:35 -->

## Advanced Techniques

<!-- image -->

This section presents information and commands for using advanced techniques, such as special effects, serialized data fields, control commands, program delimiters, communications, and memory cards.

## Contents

| Special Effects for Print Fields . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .         |   41 |
|------------------------------------------------------------------------------------------------------------|------|
| Serialized Data. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .   |   41 |
| Variable Data . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .  |   41 |
| Stored Formats. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .    |   42 |
| Initialize/Erase Stored Formats . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .                |   42 |
| Download Format Command. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .                     |   42 |
| Field Number Command . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .                 |   42 |
| Field Allocate . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .     |   43 |
| Recall Stored Format Command . . . . . . . . . . . . . . . . . . . . . . . . . . . . .                     |   43 |
| Control Commands . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .         |   44 |
| Test and Setup Commands . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .                  |   44 |
| Calibration and Media Feed Commands . . . . . . . . . . . . . . . . . . . . . . .                          |   45 |
| Cancel/Clear Commands. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .                 |   45 |
| Printer Control Commands . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .                 |   45 |
| Set Dots/Millimeter. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .         |   47 |
| Host Status Commands. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .                |   47 |
| Changing Delimiters and Command Prefixes . . . . . . . . . . . . . . . . . . . . .                         |   49 |
| Communication Diagnostics Commands. . . . . . . . . . . . . . . . . . . . . . . . .                        |   49 |
| Networking . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . |   50 |
| Assigning Network IDs/Chaining Multiple Printers. . . . . . . . . . . . . . . .                            |   50 |
| Connecting Printers into the Network . . . . . . . . . . . . . . . . . . . . . . . . .                     |   50 |
| Graphic Commands. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .          |   51 |
| Boxes and Lines . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .          |   51 |
| Working with Hex Graphic Images. . . . . . . . . . . . . . . . . . . . . . . . . . . .                     |   51 |
| Alternative Data Compression Scheme for ~DG and ~DB Commands.                                              |   52 |
| Recalling a Hexadecimal Graphic Image. . . . . . . . . . . . . . . . . . . . . . .                         |   53 |

| Contents (Continued)                                                   |    |
|------------------------------------------------------------------------|----|
| Image Move . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . | 53 |
| Reducing Download Time of Graphic Images . . . .                       | 53 |
| Transferring Object Between Storage Devices . . .                      | 54 |
| Deleting Graphics from Memory . . . . . . . . . . . . . .              | 55 |
| Defining and Using the AUTOEXEC.ZPL Function                           | 55 |
| Memory, Flash Cards, and Font Cards . . . . . . . . . . .              | 56 |

## Special Effects for Print Fields

ZPL II includes a few 'Special Effects' commands, which are outlined below. For more information on each one of the commands listed, refer to ZPL II Programming Guide Volume One .

Reverse Printing a Field The ^FR (Field Reverse Print) command allows a field to appear as white over black or black over white. When printing a field, the ^FR command indicates that it will print the field the opposite of its background color.

Reverse Printing a Label The ^LR (Label Reverse Print) command reverses the printing of all fields in the label format. It allows a field to appear as white over black or black over white. ^LR functions like ^FR , but it applies to all fields in a label. The ^LR command remains active until turned off.

Printing a Mirror Image The ^PM (Print Mirror Image of Label) command prints the entire printable area of the label as a mirror image. This command flips the image from left to right.

Printing a Label Inverted 180 Degrees The ^PO (Print Orientation) command inverts the label format 180 degrees. In essence, the label is printed upside down.

## Serialized Data

The ^SN (Serialization Data) command allows the printer to index data fields by a selected increment or decrement value (that is, make the data fields increase or decrease by a specified value) each time a label is printed. This can be performed on up to 100 to 150 fields in a given format and can be performed on both alphanumeric and bar code fields. A maximum of 12 of the right-most integers are subject to indexing. The first integer found when scanning from right to left starts the indexing portion of the data field.

If the alphanumeric field to be indexed ends with an alpha character, the data will be scanned, character-by-character, from right to left until a numeric character is encountered. Serialization will take place using the value of the first number found.

## Variable Data

To increase throughput, you can set up a program that uses variable data fields. Then, instead of formatting the whole label each time a label is printed, the printer will have to format only the changed data field. To use this capability, you must use the ^MC and ^FV commands.

<!-- image -->

## Stored Formats

You can create formats and save them in volatile memory. A stored format can then be recalled and merged with downloaded data to form a complete label. This process saves transmission time but not formatting time. It is particularly useful if you are not working with an intelligent input device.

## To create a format, complete these steps:

1. Design the label.
2. Replace variable data fields with field numbers.
3. Allocate space for the size of the field.
4. Give the format a name.
5. Save the format to the printer.

You can store multiple formats, limited by available DRAM. If you try to save a format that would overload memory, that format is not stored. You DO NOT receive an error message that the format is not stored. You will learn that the format was not stored only when you try to recall it (and are unable to do so) or if you print the List of Formats.

If the power is turned off, all stored formats in DRAM will be lost.

## Initialize/Erase Stored Formats

Stored formats can be selectively erased using the ^ID command.

## Download Format Command

The ^DF (Download Format) command saves the ZPL II format commands as text strings to be later merged using ^XF with variable data. The format to be stored may contain Field Number ( ^FN ) commands to be referenced when recalled.

While use of stored formats will reduce transmission time, no formatting time is saved since this command saves the ZPL II as text strings which need to be formatted at print time.

## Field Number Command

The ^FN (Field Number) command is used to number the data fields. This command is used in both Store Format and Recall Format operations.

When storing a format, the ^FN command is used where you would normally use the ^FD (Field Data) command. When recalling the stored format, use ^FN in conjunction with the ^FD (Field Data) command.

## Field Allocate

Use the ^FA (Field Allocate) command to allocate space for the field to be saved.

## Recall Stored Format Command

The ^XF (Recall Format) command recalls a stored format to be merged with variable data. There can be multiple ^XF commands and they can be located anywhere in the label format.

When recalling a stored format and merging data utilizing the ^FN (Field Number) function, the calling format must contain the ^FN command to properly merge the data.

While use of stored formats will reduce transmission time, no formatting time is saved because the format being recalled was saved as text strings that need to be formatted at print time.

Example · These are examples of using stored format:

Working with Stored Format commands involves designing and saving a stored format, then recalling and merging the format with some variable data.

The following is an example of how to use the various Stored Format commands. First, enter the following format and send it to the printer. Notice that no label is printed. (DATA Indicator went On and Off.)

- ^XA^DFFORMAT^FS
- ^LH30,30
- ^BY2,3,100
- ^FO120,100^CFD^FN1^FA9^FS
- ^FO120,160^B3^FN2^FA6^FS
- ^XZ

Second, enter the following format and send it to the printer. The label shown will be printed.

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

## Control Commands

Control commands may be sent from the host at any time to elicit an immediate response from the printer. Control commands may be sent in a group or singly.

A control command causes the printer to take direct software action (such as clearing the memory), physical action (such as moving to next home position), or a combination (such as feeding a label and calculating and storing its length).

The basic format for using all of the control commands is:

~(2-letter command) - For example, ~DG

## Test and Setup Commands

The following commands, presented in alphabetical order, are used to test various elements of the printer and its status.

Table 2 • Test and Setup Commands

| Command                   | Function                                                                                                                                                                                                                                                                                                                                                                                                   |
|---------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| ~HM (Memory Status)       | Sending this command to the printer immediately returns a memory status message to host. Use this command whenever you need to know the status of the memory.                                                                                                                                                                                                                                              |
| ~HS (Host Status)         | Sending this command to the printer immediately returns a three-line printer status message to the host. Use this command whenever you need to know the status of the printer.                                                                                                                                                                                                                             |
| ~JR (Power On Reset)      | This command resets all of the printer's internal software, performs a power-on self-test, clears the buffer and DRAM,and resets communication parameters and default values. ~JR performs the same function as a manual power-on reset.                                                                                                                                                                   |
| ~JN (Head Test Fatal)     | This command resets the printhead element error override, acting as a toggle for ~JO . The printer then goes into fault status (turns head indicator on steadily) if any subsequent execution of the printing element test detects bad printing elements. This command is only functional on certain printer platforms.                                                                                    |
| ~JO (Head Test Non-Fatal) | This command overrides a failure of head element status check and allows printing to continue. The override is canceled when the printer is turned off or receives a ~JR or ~JN command. The printhead test will not produce an error if the ~JO override is active. This command is only functional on certain printer platforms.                                                                         |
| ^JT (Head Test Interval)  | This command lets you change the printhead test interval from 100 to any desired interval. The printer automatically performs an internal printhead element test, which occurs every 100 labels. This takes place during formatting which minimizes a delay in printing. Therefore, the test may be performed while the printer is in PAUSE. This command is only functional on certain printer platforms. |

## Calibration and Media Feed Commands

The following commands, presented in alphabetical order, are used to perform various media and ribbon calibrations and also set the media feed mode for the printer.

<!-- image -->

Table 3 • Calibration and Media Feed Commands

| Command                            | Function                                                                                                                                                        |
|------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------|
| ~JC (Set Media Sensor Calibration) | Forces a label length measurement and recalibrates the media and ribbon sensors. Note • In continuous mode, only the media and ribbon sensors are recalibrated. |
| ~JG (Graphing Sensor Calibration)  | Forces a label length measurement, recalibrates the media and ribbon sensors, and prints a graph (media sensor profile) of the sensor values.                   |
| ~JL (Set Label Length)             | Sets the label length. Depending on the size of the label, the printer will feed one or more blank labels.                                                      |
| ^MF (Media Feed)                   | Dictates what happens to the media at power up and after an error is cleared.                                                                                   |

## Cancel/Clear Commands

The following command controls the contents of the Zebra input buffer.

Table 4 • Cancel/Clear Commands

| Command          | Function                                                                                                                                                                                                                                                     |
|------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| ~JA (Cancel All) | Cancels all format commands in the buffer. It also cancels any batches that may be printing. The printer stops printing after the current label (if one is printing) is finished printing. All internal buffers are cleared of data. The DATA LED turns off. |

## Printer Control Commands

The following commands control various printer operations:

Table 5 • Printer Control Commands

| Command                             | Function                                                                                                                                                                                                                                          |
|-------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| ^PF (Slew Given Number of Dot Rows) | Causes the printer to slew labels (move labels at a high speed without printing) a specified number of dot rows, at the bottom of the label. This allows faster printing when the bottom portion of a label is blank.                             |
| ~PH or ^PH (Slew to Home Position)  | Causes the printer to feed one blank label. • The ~PH command feeds one label after the format currently being printing is done or when the printer is placed in pause. • The ^PH command feeds one blank label after the format it is in prints. |

<!-- image -->

Table 5 • Printer Control Commands (Continued)

| Command                  | Function                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
|--------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| ~PP (Programmable Pause) | Stops printing after the current label is printed (if one is printing) and places the printer in the Pause mode. The operation is identical to pressing the PAUSE button on the front panel of the printer. The printer will remain paused until the PAUSE button is pressed or a ~PS command is sent to the printer.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| ^PP (Programmable Pause) | This command pauses the printer after the format it is in prints. Because this command is not executed immediately, several labels may be printed before the printer is paused. The operation is identical to pressing the PAUSE button on the front panel of the printer. The printer will remain paused until the PAUSE button is pressed or a ~PS command is sent to the printer.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| ^PQ (Print Quantity)     | This command gives control over several printing operations. It controls the number of labels to print, the number of labels printed before the printer pauses, and the number of replications of each serial number.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| ^PR (Print Rate)         | Determines the media speed during printing and the slew speed (feeding a blank label). The printer will operate with the selected speeds until the setting is resent in a subsequent format or the printer is turned off. Limitations of Higher Print Speeds Print speed is application specific. Because print quality is affected by media and ribbon, printing speeds, and printer operating modes, it is very important to run tests for your applications. • With high print speeds, use thermal transfer mode only. • Horizontal bar codes with a minimum x dimension of 5 mil may be printed at print speeds of 2 in. (51mm) per second. • Rotated bar codes are limited to a minimum x dimension of 10 mil (modulus 2) at higher print speeds. At x dimension of 5 mil (modulus 1), they may be printed at 2 in. per second. • At high print speeds, Font A at a magnification of 1 is not recommended; all other fonts are acceptable. |
| ~PS (Print Start)        | Causes a printer in the Pause mode to resume printing. The operation is identical to pressing the PAUSE button on the front panel of the printer when the printer is already in the Pause mode.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |

## Set Dots/Millimeter

| Command                   | Function                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
|---------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| ^JM (Set Dots/Millimeter) | Changes the number of dots printed per millimeter. Depending on the printhead, normal dots per millimeter on a Zebra printer are the following: • 24 dots/mm (609.6 dots/inch) • 12 dots/mm (304.8 dots/inch) • 8 dots/mm (203.2 dots/inch) • 6 dots/mm (152.4 dots/inch) In some applications, these high densities are not required. For these applications, a lower density of 4 dots/mm (102 dots/inch) or 3 dots/mm (77 dots/inch) can be selected. If used, this command must be entered before the first ^FS command. |

## Host Status Commands

Table 6 • Host Status Commands

| Command   | Command               | Function                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
|-----------|-----------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| ~HI       | (Host Identification) | This command is designed to be sent from the Host to the Zebra printer to find out the type of Zebra printer. Upon receipt, the Zebra printer will respond to the Host with a character string that gives information about the printer such as the version of firmware, dots per inch, memory, and printer options.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| ^SP       | (Start Print)         | This command allows a label to start printing at a specified point before the entire label has been completely formatted. On extremely complex labels, this command can increase the overall throughput of the printer. The command works as follows: you specify the dot row at which the ^SP command is to take affect. This then creates a label 'segment.' Once the ^SP command is processed, all information in that segment will be printed. During the printing process, all of the commands after the ^SP will continue to be received and processed by the printer. If the segment after the ^SP command (or the remainder of the label) is ready for printing, media motion does not stop. If the next segment is not ready, the printer will stop 'mid-label' and wait for the next segment to be completed. Precise positioning of the ^SP command is somewhat of a trial-and-error process as it depends primarily on print speed and label complexity. The ^SP command can be effectively used to determine the worst-case print quality. You can determine if using the ^SP command is appropriate for the particular application by using the following procedure. If you send the label format up to the first ^SP command and then wait for printing to stop before sending the next segment, the printed label will be a sample of the worst case print quality. It will also drop any field that is out of order. |

<!-- image -->

Table 6 • Host Status Commands (Continued)

<!-- image -->

## Changing Delimiters and Command Prefixes

For some applications, you may need to change the ZPL II delimiter (default: , ) the format command prefix (default: ^ ), and/or the control command prefix (default: ~ ). You may change these characters to any ASCII characters that you wish, using the appropriate commands.

You might change these characters if you are using a hand-held terminal that does not have a comma to enter the ZPL II commands, if you are working with a mainframe that has trouble processing the caret, or if you find some other character(s) easier to use.

## Communication Diagnostics Commands

Zebra printers support communication diagnostics through both hardware and software control. You can use these diagnostics to troubleshoot programs.

Table 7 • Communication Diagnostics Commands

| Command                                 | Function                                                                                                                                                                                                                                               |
|-----------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| ~JD (Enable Communications Diagnostics) | Initiates a diagnostic mode that produces an ASCII printout (using current label length and full width of printer) of all characters received by the printer. This printout includes the ASCII Characters, the HEX value and any communication errors. |
| ~JE (Disable Diagnostics)               | Cancels the diagnostic mode and returns the printer to normal label printing.                                                                                                                                                                          |

<!-- image -->

## Networking

You may choose to include your printer in a local area network (LAN).

## Assigning Network IDs/Chaining Multiple Printers

LCD Control Panel If your printer is equipped with an LCD control panel, you may set the network ID through the control panel.

<!-- image -->

Note · The default network ID for all printers is 0000 .

RS-485 Use this option if your printer does not have a front panel. To set up an RS-485 network, you need to initialize with a one-printer network configuration for each printer.

## To do this, complete these steps:

1. Send a ^NIXXX command where XXX is the new ID for the printer.
2. Issue a ^JUS command to save current settings.

## Connecting Printers into the Network

If the printer already has a network ID, use the ~NC (Network Connect) command to connect a particular printer into the network by calling up the printer's Network ID Number. You can then send data to the printer. You can then use the ~NT command to disconnect (set transparent) the printer, if desired, when data transmission has finished.

## Graphic Commands

In addition to text and bar codes, three types of graphics can be printed on a Zebra printer:

- boxes and lines
- ZPL II label formats saved as graphics images
- graphic images in Hexadecimal format

ZPL II has a format command that will create boxes and lines as part of any label format. These label formats can also be stored as graphic images and data can be merged with them at print time. Additionally, ZPL II will permit the printing of graphic images from other sources that have been created in (or converted to) hexadecimal (HEX) format. Such graphic images can come from a variety of sources, including CAD programs, draw and paint programs, and scanned images.

## Boxes and Lines

The ^GB (Graphic Box) command is used to draw boxes and/or lines as part of a label format. Boxes and lines can be use to highlight important information, divide labels into distinct areas, or just dress up the way the label looks.

## Working with Hex Graphic Images

ZPL II can be used to save graphic images in HEX format in DRAM, FLASH, or PCMCIA, depending on the type of memory installed in your printer. The image might be created using a CAD program, a draw or paint program, or a scanner. These images can then be printed on the label. Graphic images may be created using a program that creates files in the .PCX format. These files must then be converted to ZPL II graphic format .GRF (pure hexadecimal data without headers or other extraneous information) for use as part of a label format. You can use the ZTools™ for Windows program (available from Zebra) to convert the .PCX graphic format into the pure hexadecimal .GRF graphic format. Hexadecimal data may also be directly input as part of a ZPL II program. Manually preparing a string of HEX code is possible but usually impractical.

<!-- image -->

## Alternative Data Compression Scheme for ~DG and ~DB Commands

There is an alternative data compression scheme recognized by the Zebra printer. This scheme further reduces the actual number of data bytes and the amount of time required to download graphic images and bitmapped fonts with the ~DG and ~DB commands.

The following represent the repeat counts 1, 2, 3, 4, 5, ...., 19 on a subsequent Hexadecimal value. Values start with G because 0 through 9 and A through F are already used for HEX values.

<!-- image -->

G H I J K L M N O P Q R S T U V W X Y 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19

These numbers represent the repeat counts 20, 40, 60, 80,....400 on a subsequent hexadecimal value.

g

20

r

240

k v 100 320

- l w 120 340

o

180

z

400

h

40

s

260

I

60

t

280

j

80

u

300

m

140

x

360

n

160

y

380

Example 1 · Sending M6 to the printer is identical to sending the following hexadecimal data:

6666666

The M has the value of 7. Therefore M6 sends seven (7) hexadecimal 6's.

- Example 2 · Sending hB to the printer is identical to sending the following hexadecimal data:

BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB

The h has a value of 40. Therefore, hB sends 40 Hexadecimal B's.

- Example 3 · Sending MvB or vMB sends 327 hexadecimal B's to the printer. The M has a value of 7, and the v has a value of 320. Together, they specify 327 Hexadecimal B's.

Repeat Values Several repeat values can be used together to achieve any desired value.

- a comma (,) fills the line, to the right, with zeros (0) until the specified line byte is filled.
- an exclamation mark (!) fills the line, to the right, with ones (1) until the specified line byte is filled.
- a colon (:) denotes repetition of the previous line.

p

200

q

220

## Recalling a Hexadecimal Graphic Image

The ^XG (Recall Graphic) command is used to recall one or more graphic images for printing. This command is used in a label format to merge pictures such as company logos and piece parts, with text data to form a complete label.

An image may be recalled and resized as many times per format as needed. Other images and data may be added to the format.

## Image Move

The ^IM (Image Move) command performs a direct move of an image from a storage area into the bitmap. The command is identical to the Recall Graphic command except that there are no sizing parameters.

## Working with Label Formats as Graphics

The ^IS (Image Save) and ^IL (Image Load) commands are used to save a ZPL label format (including text and/or bar codes) in the printer's DRAM, FLASH, or PCMCIA as a special graphic image. This increases the throughput of a series of similar but not identical labels.

Instead of formatting each individual label completely, store the constant fields as an image (known as creating a template). Then, in subsequent label formats, commands are issued to recall that graphic image format and merge it with variable data.

## Reducing Download Time of Graphic Images

There is a method of reducing the actual number of data bytes sent to the printer when using the ~DG command.

If the HEX string ends in an even number of zeros (0's), a single comma (,) can be substituted for ALL of the zeros. If the HEX string ends in an odd number of zeros, one zero and a single comma is required. The exclamation mark (!) and the colon (:) described under Repeat Values on page 52 can also be used.

Note · The text rows in your editor may not be the same as the dot rows used by ZPL II. The editor may word wrap or truncate the dot rows. ZPL II ignores the end of a text line (carriage returns and line feed characters).

<!-- image -->

<!-- image -->

## Transferring Object Between Storage Devices

The ^TO (Transfer Object) command is used to copy an object or group of objects from one storage device to another. It is quite similar to the copy function used in personal computers.

Source and destination devices must be supplied and must be different and valid for the action specified. Invalid parameters will cause the command to be ignored.

There are no defaults associated with this command. However, the asterisk (*) may be used as a wild card for Object names and extensions. For instance, ZEBRA.* or *.GRF would be acceptable forms for use with ^TO command.

The Asterisk (*) can be used to transfer multiple object files (except *.FNT) from the DRAM to the Memory Card. For example, you have several object files that contain logos. These files are named LOGO1.GRF , LOGO2.GRF , and LOGO3.GRF .

Example · You want to transfer all of these files to the Memory Card using the name NEW instead of LOGO. By placing an Asterisk (*) after both LOGO and NEW in the transfer command, you can copy all of these files with one command. The format for this would be as follows:

```
^XA ^TOR:LOGO*.GRF,B:NEW*.GRF ^XZ
```

Note · If, during a multiple transfer, a file is too big to be stored on the Memory Card, it will be skipped. All remaining files will be checked to see if they can be stored. Those that can be stored, will be stored.

<!-- image -->

<!-- image -->

## Deleting Graphics from Memory

The ^ID (Item Delete) command deletes objects, images, fonts, and formats from storage areas selectively or in groups. This command can be used within a printing format to delete objects just prior to saving new ones or can be in a stand-alone type format simply to delete objects.

The object name and extension support the use of the asterisk (*) as a wildcard. This allows for easy deletion of selected groups of objects.

The following are various examples of using the ^ID command.

## To delete just stored formats from DRAM:

```
^XA^IDR:*.ZPL^XZ
```

## To delete formats and images named SAMPLE from DRAM regardless of the extension:

```
^XA^IDR:SAMPLE.*^XZ
```

## To delete the image SAMPLE1.GRF prior to storing SAMPLE2.GRF:

```
^XA ^FO25,25^AD,18,10^FDDelete^FS ^FO25,45^AD,18,10^FDthen Save^FS ^IDR:SAMPLE1.GRF^FS ^ISR:SAMPLE2.GRF^FS ^XZ
```

## To delete everything from DRAM:

```
^XA^IDR:*.*^XZ
```

## Defining and Using the AUTOEXEC.ZPL Function

An AUTOEXEC.ZPL file function is supported by the printer. It functions in much the same way as the AUTOEXEC.BAT file in MS-DOS. The AUTOEXEC.ZPL file function can be used for setting up various parameters at the time the printer is powered up (such as ^COY , ^LL , ^CWf ). The function can also be recalled at any time after power up.

This file must initially be in the extra EPROM, FLASH, or PCMCIA memory. When the printer is powered on, it looks to the extra memory site for the stored format called AUTOEXEC.ZPL . If found, the contents of the file are automatically executed as a stored format.

<!-- image -->

## Memory, Flash Cards, and Font Cards

Zebra printers come with a variety of memory device, including DRAM, EPROM, PCMCIA, Flash, socket Flash, and battery backed-up RAM.

<!-- image -->

Note · Not all memory options are available on all printers.

Most Zebra printers allow you to print a printer configuration label, which will show the letter designation assigned to your printer memory options. For printer models that do not support this feature, use Table 8 to see how the memory IDs are assigned. Memory IDs default to these values when the printer is reset to factory defaults.

Table 8 • Letter Designations for Different Memory Options

| Memory Option        | Default Letter Designation   |
|----------------------|------------------------------|
| EPROM                | E:                           |
| PCMCIA               | B:                           |
| Flash                | E:                           |
| DRAM                 | R:                           |
| Battery backed-upRAM | B:                           |
| Socket Flash         | B:                           |

A few ZPL II commands directly affect the types of memory available to Zebra printers. These commands are ~JB , ^JB and ~HM .

<!-- image -->

Table 9 • Commands that Affect Available Memory Types

| Command                       | Function                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
|-------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| ~JB (Reset Battery Dead)      | This command is sent to the printer if either of these conditions exist: • If the B: memory card is intentionally cleared (reinitialized). • If the battery supplying power to the Battery Powered Font Card fails and is replaced. (A bad battery would show a 'battery dead' condition on the printer configuration label.) Note • If you replace the battery but do not send this command to the printer, the Battery Powered Font Card will not function.                                                                                                                                                                                                                             |
| ^JB (Initialize Flash Memory) | This command is used to initialize the two types of Flash Memory available in the Zebra printers.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| ~HM (Host Memory Status)      | Sending this command to the printer immediately returns a memory status message to the host. Use this command whenever you need to know the status of the memory. When the Host Memory Status Command, ~HM , is sent to the Zebra printer, a line of data containing three numbers is sent back to the Host. The following is an example: 1024,0780,0780 • The first value is the total amount of RAM(Random Access Memory) installed in the printer. This number is in Kilobytes. • The second value is the maximum amount of RAMavailable to the user. This number is in Kilobytes. • The third value is the amount ofRAM currently available to the user. This number is in Kilobytes. |

<!-- image -->

<!-- image -->

Notes · \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

<!-- image -->

4

