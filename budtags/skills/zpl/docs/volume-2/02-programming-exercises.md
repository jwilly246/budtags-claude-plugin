<!-- Source: ZPL II Programming Guide Volume 2 -->
<!-- Section: Chapter 2: Programming Exercises -->
<!-- Generated: 2025-11-02 04:52:35 -->

## Programming Exercises

<!-- image -->

This section provides exercises that show you how to use ZPL II.

| Contents                                                                                                                                                                                                     |    |
|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----|
| Introduction to Exercises . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .                                                                                  | 20 |
| Computer and Software Requirements . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .                                                                                                   | 20 |
| Performing the Exercises. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .                                                                                        | 20 |
| Exercise 1: Saving Label Formats as Graphic Images . . . . . . . . . . . . . . . . . . . . . . . . . .                                                                                                       | 21 |
| Exercise 2: Downloading and Printing Graphic Images. . . . . . . . . . . . . . . . . . . . . . . . . .                                                                                                       | 23 |
| Exercise 3: Setting Print Rate, Printing Quantities of Labels in an Inverted Orientation, and Suppressing Backfeed . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . | 26 |
| Exercise 4: Slew Command, Form Feed, and Printing Entire Formats in Reverse . . . . .                                                                                                                        | 29 |
| Exercise 5: Using Serialized Fields . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .                                                                                        | 33 |
| Exercise 6: Stored Formats . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .                                                                                     | 35 |

<!-- image -->

## Introduction to Exercises

These programming exercises are included to assist and instruct both the new and more experienced user in the proper use of ZPL II commands. The exercises are simple by design, so they can be completed quickly. New users may find it helpful to complete all of the exercises. More experienced users may want to refer only to exercises detailing the use of specific commands or features. Most exercises are 'stand-alone' and can be completed individually. However, some exercises assume that you have completed a previous exercise (such as exercises that erase a previously saved graphic image).

<!-- image -->

Note · Note the following as you do the exercises

- Factory default printer settings were used for the examples in this guide, and the printer is set up for tear-off operation.
- The actual size of your printed examples may be different than those shown in this guide. The important thing is that the information displayed is the same.

## Computer and Software Requirements

The exercises are designed for a Zebra printer controlled by a 'stand-alone' (not part of a network) IBM ® -compatible personal computer because of its relative familiarity among users. However, a Zebra printer also may be controlled by mainframes or minicomputers.

The ZPL II language uses only printable ASCII characters. Any word processor or text editor capable of creating ASCII-only files (files without formatting codes and other extraneous information) can be used to create the scripts in these examples. For instance, if you are using Microsoft Word ® , save your scripts as text files (.txt).

## Performing the Exercises

Before beginning the exercises, load the printer with media and ribbon (if used) and make sure that the printer is properly adjusted for the media. If you are unfamiliar with these procedures, refer to the printer's User Guide for assistance.

The examples shown in this guide assume a media size of at least 80 mm wide and 60 mm long. Media of different sizes can be used; however, parameters affecting size or location of printed data may need to be modified. If you use continuous media for the examples, set the label length by adding the command sequence ^LL480^FS after the ^XA command line. Both of these commands are covered in detail in ZPL II Programming Guide Volume One .

Each exercise has two parts: the actual commands sent to the printer and the results (usually in the form of a printed label) of those commands. Type the commands exactly as you see them. When you finish typing a line, press the RETURN or ENTER key, and then type the next line. Continue this process for all of the lines in the example.

If a script is in two or more portions, save the two parts as separate .txt files. Send the first portion to the printer, and wait to see the results. Then send the next potion, and wait again to see the results. Depending on the exercise, a result may be data uploading to the printer indicated by a flashing LED (if available on your printer) or a sample label printing.

## Exercise 1 · Saving Label Formats as Graphic Images

This exercise illustrates how to save a label format as a graphic image in printer RAM and then recall (load) for printing a label format that has been previously saved. The exercise consists of two scripts. The first contains a label format and the commands necessary to save the format as a graphic image. The second recalls and prints the label format that was saved as the graphic image.

While this exercise utilizes the ^IL command to load a graphic image, the ^IM command may also be used. These two commands differ in that images loaded using the ^IL command are always positioned relative to the ^FO0,0 (Field Origin) command. The ^IM command places the image anywhere on the label as specified by an ^FO command preceding it.

The ZPL II commands sent to the printer are:

```
^XA ^LH30,30 ^FO20,10^AFN,56,30^FDZEBRA^FS ^FO20,80^B3N,Y,20,N,N^FDAAA001^FS ^FO10,160^GB150,100,4^FS ^ISR:EXERPROG.GRF,N ^XZ ^XA^ILR:EXERPROG.GRF^XZ
```

## Programming Commands

Type the commands (shown in bold) in the order given. An explanation of what each command does is in brackets ( [ ] ).

^XA [ ^XA - Indicates start of label format.] ^LH30,30 [ ^LH - Sets label home position 30 dots to right and 30 dots down from top edge of label.] ^FO20,10^AFN,56,30^FDZEBRA^FS - Select font 'F' and sets character size to 56 dots high and 30 dots wide.]

```
[ ^FO - Set field origin relative to label home.] [ ^AF [ ^FD - Start of field data.] [ ZEBRA - Actual field data.] [ ^FS - End of field data.]
```

## ^FO20,80,^B3N,Y,20,N,N^FDAAA001^FS

```
[ ^FO - Set field origin relative to label home.] [ ^B3N,Y,20,N,N - Select Code 39 bar code. Calculate check digit, do not print interpretation line.] [ ^FD - Start of field data for bar code.] [AAA001 - Actual field data.] [ ^FS - End of field data.] ^ISR:EXERPROG.GRF,N [ ^IS - Save format as a graphic image named 'EXERPROG.GRF,' do not print after saving.] ^XZ [ ^XZ - Indicates end of label format.] (Data is uploaded to printer RAM.) ^XA^ILR:EXERPROG.GRF,N^XZ [ ^XA - Start of label format.] [ ^ILR:EXERPROG.GRF - Load and print the graphic image saved as EXERPROG.GRF] [ ^XZ - End of label format.]
```

## Review

Save the file on your computer's hard drive, and name it EXER1.ZPL . Copy the file to the printer. Compare your results with those shown below. If your label does not look like the one shown, confirm that the file you created is identical to the listing at the beginning of this exercise and repeat the printing procedure.

Figure 2 • Exercise 1 Results

<!-- image -->

## Exercise 2 · Downloading and Printing Graphic Images

This exercise illustrates how to create a hexadecimal graphic image and print it as part of your label.

To store graphic images, sufficient memory must be allocated (reserved) for them. Memory for storing graphic images is allocated as needed. The graphic images can then be recalled and integrated with additional label data without downloading the entire image each time a label is printed. Graphic images are downloaded using the ~DG (Download Graphic) command along with appropriate parameters to indicate the size of the graphic being downloaded.

Graphic images may be created using a drawing or painting program that creates files in the .PCX format, such as PC Paintbrush. These files must then be converted to ZPL II graphic format .GRF (pure hexadecimal data without headers or other extraneous information) for use as part of a label format. You can use the ZTools™ for Windows program (available from Zebra) to convert the .PCX graphic format into the pure hexadecimal .GRF graphic format. Hexadecimal data may also be directly input as part of a ZPL II program.

The ~DG command requires parameters indicating the size of the graphic image.

Format dds~DGd,o,x,t,w,data

This table identifies the parameters for this format:

Table 1 • ~DG Format Parameters

| Parameters                                    | Details                                                                                                                                                |
|-----------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------|
| d = destination device to store image         | Accepted Values: a non-volatileRAM device Default Value: R: (DRAM)                                                                                     |
| o = name of image                             | Accepted Value: 1 to 8 alphanumeric characters Default Value: UNKNOWN.GRF                                                                              |
| x = filename extension                        | Fixed: .GRF                                                                                                                                            |
| t = total number of bytes in graphic          | Accepted Values: a non-volatileRAM device Default Value: R: (DRAM)                                                                                     |
| w = number of bytes per row                   | Accepted Values: any integer Default Value: None                                                                                                       |
| data = ASCII hexadecimal sting defining image | The data string defines the image and is an ASCII hexadecimal representation of the image. Each character represents a horizontal nibble of four dots. |

Refer to the ~DG command in ZPL II Programming Guide Volume One for complete information on calculating the total number of bytes and the number of bytes per row.

For this exercise, create a 'smile' graphic (such as the one shown below) in a drawing or paint program so that the graphic is 1.5 inches by 1.5 inches at 200 dpi.

<!-- image -->

Save the graphic in .PCX format and name it: SMILE.PCX . Convert this file to the .GRF format using ZTools™ for Windows.

The ZPL II commands you will use in this exercise are:

^XA and ^XZ : label format start/stop commands

^FO and ^FS : label field definition commands

^XG : recall graphic command

The ZPL II commands sent to the printer are:

```
~DGR:SMILE.GRF,12012,39
```

Depending on the image size and how the graphic was created, there will be many lines of ASCII hexadecimal data describing your image following the ~DG command line.

```
^XA ^FO50,50^XGR:SMILE.GRF,1,1^FS ^XZ
```

## Programming Commands

Type the commands shown in bold in the order they are presented. Command explanations are provided in brackets ([explanation]).

^XA

[ ^XA - Indicates start of label format.]

## ^FO50,50^XGR:SMILE.GRF,1,1^FS

[ ^FO - Set field origin relative to label home.]

[ ^XG - Recall graphic named 'SMILE' from memory with a magnification of 1:1 along X and Y axis.]

[ ^FS - End of field data.]

^XZ

[ ^XZ - Indicates end of label format.]

## Review

Save this file on your computer's hard drive, name it EXER2.ZPL . Copy the file to the printer. Compare your results with those shown below. If your label does not look like the one shown, confirm that the file you created is identical to the listing at the beginning of this exercise and repeat the printing procedure.

Figure 3 • Exercise 2 Results

<!-- image -->

## Exercise 3 · Setting Print Rate, Printing Quantities of Labels in an Inverted Orientation, and Suppressing Backfeed

This exercise illustrates how to set the print speed, print a predetermined quantity of labels, suppress backfeed for tear-off, and print entire labels in an inverted orientation.

The ZPL II commands sent to the printer are:

```
^XA^PR3^XZ ^XA ^LH360,30 ^FO20,10^AF^FDZEBRA^FS ^FO20,60^B3^FDAAA001^FS ^POI ^PQ2 ^XB ^XZ
```

## Programming Commands

Type the commands (shown in bold) in the order given. An explanation of what each command does is in brackets.

## ^XA^PR3^XZ

```
[ ^XA - Indicates start of label format.] [ ^PR3 - Set print rate to 3 inches/second] [ ^XZ - End of ZPL program.]
```

## ^XA

[ ^XA - Indicates start of label format.]

## ^LH360,30

[ ^LH - Set label home position 360 dots to right and 30 dots down from top edge of label.]

## ^FO20,10^AF^FDZEBRA^FS

```
[ ^FO - Set field origin relative to label home.] [ ^AF - Select font 'F'] [ ^FD - Start of field data.] [ZEBRA- Actual field data.] [ ^FS - End of field data.]
```

```
^FO20,20,^B3^FDAAA001^FS [ ^FO - Set field origin relative to label home.] [ ^B3 - Select Code 39 bar code.] [ ^FD - Start of field data for bar code.] [ AAA001 - Actual field data.] [ ^FS - End of field data.] ^POI [ ^POI - Set print orientation to invert the entire label.] ^PQ2 [ ^PQ2 - Set print quantity to 2 labels.] ^XB [ ^XB - Suppress Backfeed for tear-off modes.] ^XZ [ ^XZ - Indicates end of label format.]
```

## Review

Save the file on your hard drive, and name it EXER3.ZPL . Copy the file to the printer. Compare your results with those shown below. If your labels are not similar, confirm that your file matches the code at the beginning of this exercise.

<!-- image -->

## Exercise 4 · Slew Command, Form Feed, and Printing Entire Formats in Reverse

This exercise illustrates the slew and form feed (slew to home) commands and the commands required for printing the entire label in reverse.

The ZPL II commands that are sent to the printer are:

```
^XA ^PR2 ^LRY ^LH30,30 ^FO0,0^GB400,300,300^FS ^FO20,10^AF^FDZEBRA^FS ^FO20,60^B3,,40^FDAAA001^FS ^PF50 ^FO20,160^AF^FDSLEW EXAMPLE^FS ^XZ ^XA^PH^XZ ^XA ^PR2,6 ^FO20,10^AF^FDZEBRA^FS ^FO20,60^B3,,40^FDAAA001^FS ^PF250 ^FO20,160^AF^FDSLEW EXAMPLE^FS
```

^XZ

## Programming Commands

Type the commands (shown in bold) in the order given. An explanation of what each command does is in brackets.

## ^XA

[ ^XA - Indicates start of label format.]

## ^PR2

[ ^PR2 - Set print rate to speed of 2 inches/second]

## ^LRY

[ ^LRY - Reverse print entire label.]

## ^LH30,30

[ ^LH - Set label home position 30 dots to right and 30 dots down from top edge of label.]

```
^FO0,0^GB400,300,300^FS [ ^FO - Set field origin relative to label home.] [ ^GB - Create a filled graphic box to be used as background for reverse printed label. (May need to adjust parameters for different media size.] ^FO20,10^AF^FDZEBRA^FS [ ^FO - Set field origin relative to label home.] [ ^AF - Select font 'F.'] [ ^FD - Start of field data.] [ ZEBRA - Actual field data.] [ ^FS - End of field data.] ^FO20,60^B3,,40^FDAAA001^FS [ ^FO - Set field origin relative to label home.] [ ^B3 - Select Code 39 bar code.] [ ^FD - Start of field data for bar code.] [AAA001 - Actual field data.] [ ^FS - End of field data.] ^PF50 [Slew 50 dot rows at bottom of label.] ^FO20,160^AF^FDSLEW EXAMPLE^FS [ ^FO - Set field origin relative to label home.] [ ^AF - Select font 'F.'] [ ^FD - Start of field data.] [ SLEW EXAMPLE - Actual field data.] [ ^FS - End of field data.] ^XZ [ ^XZ - Indicates end of format.] ^XA^PH^XZ [Commands to feed to next home position.] ^XA [ ^XA - Indicates start of format.] ^PR2,6 [ ^PR2 - Set print rate to speed of 2 inches/second, set slew rate to speed of 6 inches/second] ^FO20,10^AF^FDZEBRA^FS [ ^FO - Set field origin relative to label home.] [ ^AF - Select font 'F.'] [ ^FD - Start of field data.][ZEBRA- Actual field data.][ ^FS - End of field data.]
```

```
^FO20,60^B3,,40^FDAAA001^FS [ ^FO - Set field origin relative to label home.] [ ^B3 - Select Code 39 bar code.] [ ^FD - Start of field data for bar code.] [ AAA001 - Actual field data.] [ ^FS - End of field data.] ^PF250 [ ^PF250 - Slew 250 dot rows.] ^FO20,160^AF^FDSLEW EXAMPLE^FS [ ^FO - Set field origin relative to label home.] [^AF - Select font 'F.'] [ ^FD - Start of field data.] [ SLEW EXAMPLE - Actual field data.] [ ^FS - End of field data.] ^XZ [ ^XZ - Indicates end of format.]
```

Programming Exercises

Introduction to Exercises

## Review

Save the file on your hard drive, and name it EXER4.ZPL . Copy the file to the printer. Compare your results with those below. If your labels are not similar, confirm that your file matches the code at the beginning of this exercise.

Figure 5 • Exercise 4 Results

<!-- image -->

## Exercise 5 · Using Serialized Fields

This exercise discusses the commands and parameters required to produce serialized fields as part of a label format. The ZPL II commands sent to the printer are:

```
^XA ^LH30,30 ^FO20,10^AF^FDZEBRA^FS ^FO20,60^B3,,40,,^FDAA001^FS ^PQ10
```

## ^FO20,180^AF^SNSERIAL NUMBER 00000000111,1,Y^FS ^XZ Programming Commands Type the commands (shown in bold) in the order given. An explanation of what each command does is in brackets. ^XA [ ^XA - Indicates start of label format.] ^LH30,30 [ ^LH - Sets label home position 30 dots to right and 30 dots down from top edge of label.] ^FO20,10^AF^FDZEBRA^FS [ ^FO - Set field origin relative to label home.] [ ^AF - Select font 'F.'] [ ^FD - Start of field data.] [ZEBRA- Actual field data.] [ ^FS - End of field data.] ^FO20,60^B3,,40,,^FDAA001^FS [ ^FO - Set field origin relative to label home.] [ ^B3 - Select Code 39 bar code.] [ ^FD - Start of field data for bar code.] [AA001 - Actual field data.] [ ^FS - End of field data.] ^FO20,180^AF^SNSERIAL NUMBER 00000000111,1,Y^FS [ ^FO - Set field origin relative to label home.] [ ^AF^SNSERIAL NUMBER 00000000111,1,Y - Define serialized field, starting value of 111, increment by 1, insert leading zeros.] [ ^FS - End of field data.] ^PQ10 [ ^PQ10 - Set print quantity to 10.]

<!-- image -->

^XZ

[ ^XZ - Indicates end of format.]

## Review

Save the file to your computer's hard drive, and name it EXER5.ZPL . Copy the file to the printer. Compare your results with those shown below.

Figure 6 • Exercise 5 Results

<!-- image -->

A total of 10 labels should be printed. The first and last labels are shown here. If your labels do not look like the ones shown, confirm that the file you created is identical to the listing at the beginning of this exercise and repeat the printing procedure.

## Exercise 6 · Stored Formats

This exercise illustrates the commands and parameters required to use stored formats. The ZPL II commands sent to the printer are:

```
^XA ^DFFORMAT^FS ^LH30,30 ^FO20,10^AF^FN1^FS ^FO20,60^B3,,40,,^FN2^FS ^XZ ^XA ^XFFORMAT^FS ^FN1^FDZEBRA^FS ^FN2^FDAAA001^FS ^XZ ^XA ^XFFORMAT^FS ^FN1^FDBEARS^FS ^FN2^FDZZZ999^FS ^XZ
```

## Programming Commands

Type the commands (shown in bold) in the order given. An explanation of what each command does is in brackets.

## ^XA

[ ^XA - Indicates start of label format.]

## ^DFFORMAT^FS

```
[ ^DF - Download and store format.] [ FORMAT - Name of format.] [ ^FS - End of field data.]
```

## ^LH30,30

[ ^LH - Sets label home position 30 dots to right and 30 dots down from top edge of label.]

## ^FO20,10^AF^FN1^FS

- Set field origin relative to label home.]

```
[ ^FO [ ^AF - Select font 'F.'] [ ^FN1 - Assign field number 1.] [ ^FS - End of field data.]
```

<!-- image -->

```
^FO20,60^B3,,40,,^FN2^FS [ ^FO - Set field origin relative to label home.] [ ^B3 - Select Code 39 bar code.] [ ^FN2 - Assign field number 2.] [ ^FS - End of field data.] ^XZ [ ^XZ - Indicates end of format.] ^XA [ ^XA - Indicates start of label format.] ^XFFORMAT^FS [ ^XF - Recall stored format.] [ FORMAT - Name of format to be recalled.] [ ^FS - End of field data.] ^FN1^FDZEBRA^FS [ ^FN1 - Indicate following data should be inserted in area for field number 1.] [ ^FD - Indicate start of field data.] [ ZEBRA - Field data.] [ ^FS - End of field data.] ^FN2^FDAAA001^FS [ ^FN2 - Indicate following data should be inserted in area allocated for field number 2.] [ ^FD - Indicates start of field data.] [AAA001 - Field data.] [ ^FS - End of field data.] ^XZ [ ^XZ - Indicates end of format.] ^XA [ ^XA - Indicates start of label format.] ^XFFORMAT^FS [ ^XF - Recall stored format.] [ FORMAT - Name of format to be recalled.] [ ^FS - End of field data.] ^FN1^FDBEARS^FS [ ^FN1 - Indicates following data should be inserted in area allocated for field number 1.] [ ^FD - Indicates start of field data.] [ BEARS - Field data.] [ ^FS - End of field data.]
```

## ^FN2^FDZZZ999^FS

[ ^FN2

[ ^FD

[ ZZZ999

[ ^FS

^XZ

[ ^XZ

```
- Indicates following data should be inserted in area allocated for field number 2.] - Indicates start of field data.] - Field data.] - End of field data.] - Indicates end of format.]
```

## Review

Save this file to your computer's hard drive, and name it EXER6.ZPL . Copy the file to the printer. Compare your results with those shown below. If your labels do not look like the ones shown, confirm that the file you created is identical to the listing at the beginning of this exercise and repeat the printing procedure.

Figure 7 • Exercise 6 Results

<!-- image -->

<!-- image -->

<!-- image -->

Notes · \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

<!-- image -->

3

