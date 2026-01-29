<!-- Source: ZPL II Programming Guide Volume 1 -->
<!-- Section: Introduction -->
<!-- Generated: 2025-11-02 04:52:35 -->

## Introduction

<!-- image -->

This guide is the unabridged, alphabetical reference of programming commands supported in the firmware.

Firmware You can get the printer's firmware version by printing out a configuration label.

Note · Firmware upgrades are available at: www.zebra.com .

If you are using a previous version of Zebra printer firmware, some of the commands are the same and function as they did before- but equally as many are new and are not recognized by firmware that is earlier than X.10. Other commands have been redesigned and significantly enhanced to support innovations like:

- ZebraNet® ALERT
- Real-Time Clock

Any word processor or text editor capable of creating ASCII-only files can be used to recreate the examples in this guide. Most of the examples are made up of a series of instruction lines. When you finish typing a line, press Enter . Continue this process for all of the lines in the example you are experimenting with.

To provide more information and convenient cross-referencing, commands that are directly related to features discussed in Volume Two have been noted under their Comments heading, pointing to the appendix or section that applies.

ZPL and ZPL II To see the difference between ZPL and ZPL II, see the ZPL II Programming Guide Volume Two .

<!-- image -->

Notes · \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

## ZPL Commands

<!-- image -->

This section contains the complete alphabetical listing of ZPL II commands.

Description This heading provides an explanation of how the command is used, what it is capable of, and any defining characteristics it has.

Format Format explains how the command is syntactically arranged and what parameters it contains.

For Example The ^B8 command prints a EAN-8 bar code. The format of the ^B8 command is: ^B8o,h,f,g . It is arranged with the caret symbol ( ^ ), the command code ( B8 ), and the parameters and are replaced with supported values.

Parameters If a command has values that can be defined to make its function more specific, these are outlined as parameters. Parameters typically have Accepted Values and Default Values .

Still using the ^B8 example, the h parameter is defined as:

```
h = bar code height (in dots) Accepted Values: 1 to 32000 Default Value: value set by ^BY
```

If the command has no parameters - for example ~JA (Cancel All) - the parameter heading is removed, indicating that the format of the command ( ~JA ) is acceptable ZPL II code.

<!-- image -->

4

<!-- image -->

<!-- image -->

Example · When the command is best clarified in context, an example of the ZPL II code is provided. Text indicating exact code entered is printed in an easily recognizable Courier font. An example of code using the ^B8 command looks like this:

```
^XA ^FO50,50 ^B8N,100,Y,N ^FD1234567^FS ^XZ
```

Notice that the ^B8 parameter letters have been replaced with real values that apply to the command. In this example N , 100 , Y , N have been entered.

Comment This section is reserved for notes that are of value to a programmer, warnings of potential command interactions, or command-specific information that should be taken into consideration.

Example · An example comment is: This command works only when the printer is idle, or This command is ignored if a value exceeds the parameter limits .

Comments are also included next to parameters if they apply directly to a particular setting.

