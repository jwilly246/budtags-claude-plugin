<!-- Source: ZPL II Programming Guide Volume 1 -->
<!-- Section: Basic ZPL Exercises -->
<!-- Generated: 2025-11-02 04:52:35 -->

## Basic ZPL Exercises

The purpose of these exercises is to introduce basic ZPL commands to novice ZPL users.

## Make sure this checklist is complete:

-  Load the printer with labels that are big enough to give you ample space to work with.

-  Print a configuration label (CANCEL test).

-  Look at the configuration label and make sure that the LEFT POSITION is set to 000 and LABEL TOP is set to 000 .

-  Determine the printer's resolution. It is listed on the configuration label. 8/MM = 200 dpi, 12/MM = 300 dpi and 24/MM = 600 dpi.

## Tips

These are some tips when using ZPL:

- Use the DOS text editor to write ZPL files.
- Save the file as a . txt file and copy it to the printer from DOS command line.

## Before you begin

Some things that are important to understand before you begin are:

- 200 dpi means the resolution of the printhead is 200 dots per inch. If you program the printer to draw a line 100 dots long that equals a half inch. 100 dots on a 300 dpi printer prints a line 1/3 inch long.
- The home position that all your coordinates are referencing is at the left-hand trailing edge of the label as the label comes out of the printer. (There are some exceptions to this.)

## Exercises

The exercises start simple and gradually progress to give you an opportunity to try a variety of commonly used ZPL commands. Not all commands are covered, but this should be a good core of commands to learn. Some commands may not be supported due to the firmware version in your printer.

<!-- image -->

<!-- image -->

## Exercise 1 · This exercise shows you how to specify a location for an entered name.

1. Print your name on the label.
2. Start by printing just your name on the label using the following format as a model.

Important · Your name goes where you see xxxxxxxxxxx in the second line of code.

^XA

```
^FO50,50^ADN,36,20^FD xxxxxxxxxxx ^FS ^XZ Send the above format to the printer. ^XA every format must start with this command ^XZ every format must end with this command ^FD field data ^FS field separator ^FO field origin
```

3. When the label prints correctly, alter the first number after the ^FOx and see how that effects the print position. Alter the second number after the ^FO50,x and see how that effects the print position.

## Font instruction

^ADN

1. Alter the numbers after the ^ADN,x,x command.
- 18,10 is the smallest size you can make the D font.
- The first number is the height of the font in dots, and the second is the width in dots.
- You can use direct multiples up to ten times that size as a maximum.

Example · 180,100 is the largest you can make the D font.

- 25,18 would not be a valid size. The printer rounds to the next recognizable size.
2. To check the font matrices tables for other fonts to try, see ZPL II Programming Guide Volume Two .
3. Try the zero scalable font ^A0N,x,x .

This font is scalable and you can choose any height and width.

## Rotation commands

1. Change ^ADN to ^ADR , then ^ADI , then ^ADB . See how the print position changes.
2. Add more fields.

<!-- image -->

<!-- image -->

<!-- image -->

3. Add two more fields to print directly under your name using the ^ADN,36,20 font and size:

Your street address

Your city, state, zip

4. You must add two more lines of code that start off with:

```
^XA ^FO50,50^ADN,36,20^FDxxxxxxxxxxx^FS ^FO    (fill in the rest) ^FO    (fill in the rest) ^XZ
```

Make sure all these fields print in the same font and size and left side of fields has same vertical alignment.

```
Your name 1200 W Main Street Anytown, Il 60061
```

## Exercise 2 · Boxes and lines

1. Use the address format from Exercise 1 .
2. Add this new line to your existing format:

```
^FO50,200^GB200,200,2^FS
```

This prints a box one wide by one inch long and the thickness of the line is 2 dots.

3. Reposition and resize the square so that it goes around the name and address uniformly.
4. Print a line by adding:

```
^FO50,300^GB400,0,4,^FS
```

This prints a horizontal line two inches wide by 4 dots thick.

5. Print a vertical line using this code:

```
^F0100,50^GBO,400,4^FS
```

<!-- image -->

## Exercise 3 · Bar codes ^B3 code 39 bar code

1. Write the following format and send to the printer:
2. Try changing each of the parameters in the ^B3 string so you can see the effects.

```
^XA ^FO50,50^B3N,N,100,Y,N^FD123456^FS ^XZ
```

Important · For valid parameter choices, see ^B3 on page 21.

<!-- formula-not-decoded -->

3. Insert the ^BY command just before the ^B3 to see how the narrow bar width can be altered.

^FO50,50^BY2^B3..etc ^BYx, acceptable values for x are 1 through 10

4. Alter the ratio of the narrow to wide bar.
5. Print out a ^B3 bar code with the interpretation line on top of the bar code and the bar code rotated 90 degrees.
6. Add a ^PQ just before the ^XZ to print several labels.

```
^FO50,50^BY2,3^B3..etc ^BY2,x acceptable values for x are 2.1 through 3 in .1 increments
```

^PQ4

^ XZ

- ^PR Print rate (in inches per second)
7. Add a ^PR command after the ^XA at the beginning of the format to change the print rate (print speed).

^XA

^PR4 then try ^PR6 ^PRx acceptable values for x are 2 through 12 (check printer specs)

See how the print speed affects the print quality of the bar code. You may need to increase the printer darkness setting at higher print speeds.

<!-- image -->

## Exercise 4 · ^SN - Serial Number command

1. Send this format to the printer:

```
^XA ^FO100,100^ADN,36,20^SN001,1,Y^FS ^PQ3 ^XZ
```

To vary the ^SNv,n,z to exercise the increment/decrement and leading zeros functions, consult this guide.

If your serial number contains alpha and numeric characters, you can increment or decrement a specific segment of the data even if it is in the middle, as this sample sequence shows:

ABCD1000EFGH, ABCD1001EFGH, ABCD1002EFGH

2. Send this file to the printer and to see how it increments the serial number. The ^SF command can also work with alpha characters.

```
^XA ^FO100,100^ADN,36,20^FDABCD1000EFGH^SF%%%%dddd%%%%,10000^FS ^PQ15 ^XZ
```

Notice how the field data character position aligns with ^SF data string:

| ^   | F   | D   | A   | B   | C   | D   | 1   | 0   | 0   | 0   | E   | F   | G   | H   |
|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|
| ^   | S   | F   | %   | %   | %   | %   | d   | d   | d   | d   | %   | %   | %   | %   |
|     |     |     |     |     |     |     |     |     |     | 1   | 0   | 0   | 0   | 0   |
|     |     |     |     |     |     |     |     |     |     | 2   | 0   | 0   | 0   | 0   |
|     |     |     |     |     |     |     |     |     |     | 3   | 0   | 0   | 0   | 0   |

And on through…

<!-- image -->

The last label prints ABCD1014EFGH .

The % is placed in positions that you do not want to increment/decrement, d = decimal, 10000=increment value.

For more details on ^SF , see ^SF on page 250.

<!-- image -->

## Exercise 5 · Saving a template to memory. ^IS and image save and image load.

<!-- image -->

Note · This exercise requires you to type a lot of data, and a single typing error will cause problems. It also serves as an exercise to troubleshoot your code against the errors you see on your labels.

## 1. Send this format to the printer:

## 2.

```
^XA ^FO20,30^GB750,1100,4^FS ^FO20,30^GB750,200,4^FS ^FO20,30^GB750,400,4^FS ^FO20,30^GB750,700,4^FS ^FO20,226^GB325,204,4^FS ^FO30,40^ADN,36,20^FDShip to:^FS ^FO30,260^ADN,18,10^FDPart number #^FS ^FO360,260^ADN,18,10^FDDescription:^FS ^FO30,750^ADN,36,20^FDFrom:^FS ^ISR:SAMPLE.GRF^FS ^XZ Send this format: ^XA ^ILR:SAMPLE.GRF^FS ^FO150,125^ADN,36,20^FDAcme Printing^FS ^FO60,330^ADN,36,20^FD14042^FS ^FO400,330^ADN,36,20^FDScrew^FS ^FO70,480^BY4^B3N,,200^FD12345678^FS ^FO150,800^ADN,36,20^FDMacks Fabricating^FS ^XZ
```

In this way the template only needs to be sent one time to the printer's memory. Subsequent formats can be sent recalling the template and merging variable data into the template. In this exercise, the file was saved in the printers R: memory, which is volatile.

## DF and ^XF - Download format and recall format

Similar concept to ^IS and ^IL command. ^IS and ^IL in general processes faster in the printer then ^DF and ^XF .

This is the way the ^DF and ^XF format structure produces a label similar to the ^IS / ^IL sample you just tried.

- ^XA
- ^XZ

```
^DFR:SAMPLE.GRF^FS ^FO20,30^GB750,1100,4^FS ^FO20,30^GB750,200,4^FS ^FO20,30^GB750,400,4^FS ^FO20,30^GB750,700,4^FS ^FO20,226^GB325,204,4^FS ^FO30,40^ADN,36,20^FDShip to:^FS ^FO30,260^ADN,18,10^FDPart number #^FS ^FO360,260^ADN,18,10^FDDescription:^FS ^FO30,750^ADN,36,20^FDFrom:^FS ^FO150,125^ADN,36,20^FN1^FS (ship to) ^FO60,330^ADN,36,20^FN2^FS(part num) ^FO400,330^ADN,36,20^FN3^FS(description) ^FO70,480^BY4^B3N,,200^FN4^FS(barcode) ^FO150,800^ADN,36,20^FN5^FS (from) ^XZ ^XA ^XFR:SAMPLE.GRF ^FN1^FDAcme Printing^FS ^FN2^FD14042^FS ^FN3^FDScrew^FS ^FN4^FD12345678^FS ^FN5^FDMacks Fabricating^FS
```

<!-- image -->

<!-- image -->

^A

