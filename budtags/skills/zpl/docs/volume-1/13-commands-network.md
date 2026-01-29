<!-- Source: ZPL II Programming Guide Volume 1 -->
<!-- Section: Network Commands (^N*, ~N*) -->
<!-- Generated: 2025-11-02 04:52:35 -->

## ^HG

## Host Graphic

Description The ^HG command is used to upload graphics to the host. The graphic image can be stored for future use, or it can be downloaded to any Zebra printer.

Format ^HGd:o.x

This table identifies the parameters for this format:

| Parameters                    | Details                                                                                                    |
|-------------------------------|------------------------------------------------------------------------------------------------------------|
| d = device location of object | Accepted Values: R: , E: , B: , and A: Default Value: search priority                                      |
| o = object name               | Accepted Values: 1 to 8 alphanumeric characters Default Value: if a name is not specified, UNKNOWN is used |
| x = extension                 | Fixed Value: .GRF                                                                                          |

Comments For more information on uploading graphics, see ^HY on page 174.

<!-- image -->

<!-- image -->

^HH

## Configuration Label Return

Description The ^HH command echoes printer configuration back to the host, using a terminal emulator.

Format ^HH

Example · This is an example of the ^HH command:

```
+10 DARKNESS +000 TEAR_OFF TEAROFF PRINT MODE NON-CONTINUOUS MEDIA TYPE WEB SENSOR TYPE DIRECT-THERMAL PRINT METHOD 050_6/8MM PRINT WIDTH 0622 LABEL LENGTH 22.0IN 557MM MAXIMUM LENGTH 9600 BAUD 8BITS DATA_BITS NONE PARITY XON/XOFF HOST HANDSHAKE NONE PROTOCOL 000 NETWORK ID NORMAL MODE COMMUNI CATIONS <> 7EH CONTROL PREFIX <> 5EH FORMAT PREFIX <> 2CH DELIMITER CHAR ZPL 11 ZPL MODE NO MOTION MEDIA POWER UP NO MOTION HEAD CLOSE DEFAULT BACKFEED +000 LABEL TOP +0000 LEFT POSITION 026 WEB_S. 068 MEDIA_S. 050 MARK S. 001 MARK MED S. CS MODES ENABLED MODES DISABLED 8648/MM FULL RESOLUTION U32.10.2 FIRMWARE U2.2.6.98.A HARDWARE ID CUSTOMIZED CONFIGURATION 1024.. .R: RAM 8192 .B:MEMORY CARD 0768 E： ONBOARD FLASH NONE FORMAT CONUERT NONE OPTION 05/14/03 RTC DATE 02:23 RTC_TIME DYNAMIC IP RESOLUTION ALL IP PROTOCOL 010.003.005.090 IP ADDRESS 255.255.255.000 SUBNET MASK 010.003.005.001 DEFAULT GATEWAY
```

<!-- image -->

<!-- image -->

## ~HI

## Host Identification

Description The ~HI command is designed to be sent from the host to the Zebra printer to retrieve information. Upon receipt, the printer responds with information on the model, software version, dots-per-millimeter setting, memory size, and any detected objects.

## Format ~HI

When the printer receives this command, it returns:

```
XXXXXX,V1.0.0,dpm,000KB,X XXXXXX = model of Zebra printer V1.0.0 = version of software dpm = dots/mm 6, 8, 12, or 24 dots/mm printheads 000KB = memory 512KB = 1/2 MB 1024KB = 1 MB 2048KB = 2 MB 4096KB = 4 MB 8192KB = 8 MB
```

## x = recognizable objects

only options specific to printer are shown (cutter, options, et cetera.)

<!-- image -->

<!-- image -->

~HM

## Host RAM Status

Description Sending ~HM to the printer immediately returns a memory status message to the host. Use this command whenever you need to know the printer's RAM status.

When ~HM is sent to the Zebra printer, a line of data containing information on the total amount, maximum amount, and available amount of memory is sent back to the host.

Format ~HM

- Example · This example shows when the ~HM is sent to the printer, a line of data containing three numbers are sent back to the host. Each set of numbers is identified and explained in the table that follows:

2

<!-- image -->

|   1 | The total amount of RAM(in kilobytes) installed in the printer. In this example, the printer has 1024K RAMinstalled.                                  |
|-----|-------------------------------------------------------------------------------------------------------------------------------------------------------|
|   2 | The maximum amount ofRAM (in kilobytes) available to the user. In this example, the printer has a maximum of 780KRAM available.                       |
|   3 | The amount of RAM(in kilobytes) currently available to the user. In this example, there is 780K ofRAM in the printer currently available to the user. |

Comments Memory taken up by bitmaps is included in the currently available memory value (due to ^MCN ).

Downloading a graphic image, fonts, or saving a bitmap affects only the amount of RAM. The total amount of RAM and maximum amount of RAM does not change after the printer is turned on.

## Host Status Return

Description When the host sends ~HS to the printer, the printer sends three data strings back. Each string starts with an &lt; STX &gt; control code and is terminated by an &lt; ETX &gt;&lt; CR &gt;&lt; LF &gt; control code sequence. To avoid confusion, the host prints each string on a separate line.

## String 1

```
<STX>aaa,b,c,dddd,eee,f,g,h,iii,j,k,l<ETX><CR><LF>
```

```
aaa = communication (interface) settings* b = paper out flag (1 = paper out) c = pause flag (1 = pause active) dddd = label length (value in number of dots) eee = number of formats in receive buffer f = buffer full flag (1 = receive buffer full) g = communications diagnostic mode flag (1 = diagnostic mode active) h = partial format flag (1 = partial format in progress) iii = unused (always 000) j = corrupt RAM flag (1 = configuration data lost) k = temperature range (1 = under temperature) l = temperature range (1 = over temperature)
```

* This string specifies the printer's baud rate, number of data bits, number of stop bits, parity setting, and type of handshaking. This value is a three-digit decimal representation of an eightbit binary number. To evaluate this parameter, first convert the decimal number to a binary number.

The nine-digit binary number is read according to this table:

<!-- image -->

| aaa = a a a a a a a a a 8 7 6 5 4 3 2 1 0   | aaa = a a a a a a a a a 8 7 6 5 4 3 2 1 0                                                                                                                                                                                                                                                                             |
|---------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| a = Handshake 0 = Xon/Xoff 1 = DTR 7        | a a a a = Baud 0 000 = 110 0 001 = 300 0 010 = 600 0 011 = 1200 0 100 = 2400 0 101 = 4800 0 110 = 9600 0 111 = 19200 1 000 = 28800 1 001 = 38400 1 010 = 57600 1 011 = 14400 (available only on certain printer models) 8 2 1 0 (available only on certain printer models) (available only on certain printer models) |
| a = Parity Odd/Even 0 = Odd 1 = Even 6      | a a a a = Baud 0 000 = 110 0 001 = 300 0 010 = 600 0 011 = 1200 0 100 = 2400 0 101 = 4800 0 110 = 9600 0 111 = 19200 1 000 = 28800 1 001 = 38400 1 010 = 57600 1 011 = 14400 (available only on certain printer models) 8 2 1 0 (available only on certain printer models) (available only on certain printer models) |
| a = Disable/Enable 0 = Disable 1 = Enable 5 | a a a a = Baud 0 000 = 110 0 001 = 300 0 010 = 600 0 011 = 1200 0 100 = 2400 0 101 = 4800 0 110 = 9600 0 111 = 19200 1 000 = 28800 1 001 = 38400 1 010 = 57600 1 011 = 14400 (available only on certain printer models) 8 2 1 0 (available only on certain printer models) (available only on certain printer models) |
| a = Sto p Bits 0 = 2 Bits 1 = 1 Bit 4       | a a a a = Baud 0 000 = 110 0 001 = 300 0 010 = 600 0 011 = 1200 0 100 = 2400 0 101 = 4800 0 110 = 9600 0 111 = 19200 1 000 = 28800 1 001 = 38400 1 010 = 57600 1 011 = 14400 (available only on certain printer models) 8 2 1 0 (available only on certain printer models) (available only on certain printer models) |
| a = Data Bits 0 = 7 Bits 1 = 8 Bits 3       | a a a a = Baud 0 000 = 110 0 001 = 300 0 010 = 600 0 011 = 1200 0 100 = 2400 0 101 = 4800 0 110 = 9600 0 111 = 19200 1 000 = 28800 1 001 = 38400 1 010 = 57600 1 011 = 14400 (available only on certain printer models) 8 2 1 0 (available only on certain printer models) (available only on certain printer models) |

## String 2

&lt;STX&gt;mmm,n,o,p,q,r,s,t,uuuuuuuu,v,www&lt;ETX&gt;&lt;CR&gt;&lt;LF&gt;

| mmm       | =   | function settings*                                              |
|-----------|-----|-----------------------------------------------------------------|
| n         | =   | unused                                                          |
| o         | =   | head up flag (1 = head in up position)                          |
| p         | =   | ribbon out flag (1 = ribbon out)                                |
| q         | =   | thermal transfer mode flag (1 = Thermal Transfer Mode selected) |
| r         | =   | Print Mode                                                      |
|           |     | 0 = Rewind                                                      |
|           |     | 1 = Peel-Off                                                    |
|           |     | 2 = Tear-Off                                                    |
|           |     | 3 = Cutter                                                      |
|           |     | 4 = Applicator                                                  |
| s         | =   | print width mode                                                |
| t         | =   | label waiting flag (1 = label waiting in Peel-off Mode)         |
| uuuuuu uu | =   | labels remaining in batch                                       |
| v         | =   | format while printing flag (always 1)                           |
| www       | =   | number of graphic images stored in memory                       |

* This string specifies the printer's media type, sensor profile status, and communication diagnostics status. As in String 1, this is a three-digit decimal representation of an eight-bit binary number. First, convert the decimal number to a binary number.

The eight-digit binary number is read according to this table:

| mmm=m7 m6                                      | m5 m4                                          | m3 m2                                          | m1                                             | m0                                             |                                                |                                                |                                                |
|------------------------------------------------|------------------------------------------------|------------------------------------------------|------------------------------------------------|------------------------------------------------|------------------------------------------------|------------------------------------------------|------------------------------------------------|
| m7 = Media Ty p e 0 = Die-Cut 1 = Continuous   | m4 m3 m2 m1 0 = Off 1                          |                                                | = On                                           | Unused =                                       |                                                |                                                |                                                |
| m6 0                                           | = Sensor Profile = Off                         | m0 = 0 1                                       | Print = Direct                                 | Mode Thermal = Thermal Transfer                |                                                |                                                |                                                |
| m5 = Communications Diagnostics 0 = Off 1 = On | m5 = Communications Diagnostics 0 = Off 1 = On | m5 = Communications Diagnostics 0 = Off 1 = On | m5 = Communications Diagnostics 0 = Off 1 = On | m5 = Communications Diagnostics 0 = Off 1 = On | m5 = Communications Diagnostics 0 = Off 1 = On | m5 = Communications Diagnostics 0 = Off 1 = On | m5 = Communications Diagnostics 0 = Off 1 = On |

## String 3

&lt;STX&gt;xxxx,y&lt;ETX&gt;&lt;CR&gt;&lt;LF&gt;

| xxxx   | =   | password                    |
|--------|-----|-----------------------------|
| y      | =   | 0 (staticRAM not installed) |
|        |     | 1 (staticRAM installed)     |

<!-- image -->

<!-- image -->

~HU

## Return ZebraNet Alert Configuration

Description This command returns the table of configured ZebraNet Alert settings to the host.

Format ~HU

Example · If the ~HU command is sent to the printer with existing Alert messages set to go to e-mail and SNMP traps, the data returned would look something like the information below. See ^SX on page 263 for complete information on the individual parameter settings.

```
B,C,Y,Y,ADMIN@COMPANY.COM,0 J,F,Y,Y,,0 C,F,Y,Y,,0 D,F,Y,Y,,0 E,F,Y,N,,0 F,F,Y,N,,0 H,C,Y,N,ADMIN@COMPANY.COM,0 N,C,Y,Y,ADMIN@COMPANY.COM,0 O,C,Y,Y,ADMIN@COMPANY.COM,0 P,C,Y,Y,ADMIN@COMPANY.COM,0
```

The first line indicates that condition B (ribbon out) is routed to destination C (e-mail address).

The next two characters, Y and Y, indicate that the condition set and condition clear options have been set to yes .

The following entry is the destination that the Alert e-mail should be sent to; in this example it is admin@company.com .

The last figure seen in the first line is 0, which is the port number.

Each line shows the settings for a different Alert condition as defined in the ^SX command.

<!-- image -->

<!-- image -->

## ^HV

## Host Verification

Description This command is used to return data from specified fields, along with an optional ASCII header, to the host computer. The command can be used with any field that has been assigned a number with the ^RT command or the ^FN and ^RF commands.

Format

^HV#,n,h

This table identifies the parameters for this format:

| Parameters                                      | Details                                                                                                                                 |
|-------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------|
| # = field number specified with another command | The value assigned to this parameter should be the same as the one used in another command. Accepted values: 0 to 9999 Default value: 0 |
| n = number of bytes to be returned              | Accepted values: 1 to 256 Default value: 64                                                                                             |
| h = header                                      | Header (in uppercase ASCII characters) to be returned with the data. Acceptable values: 0 to 3072 characters Default value: no header   |

<!-- image -->

<!-- image -->

^HW

## Host Directory List

Description ^HW is used to transmit a directory listing of objects in a specific memory area (storage device) back to the host device. This command returns a formatted ASCII string of object names to the host.

Each object is listed on a line and has a fixed length. The total length of a line is also fixed. Each line listing an object begins with the asterisk (*) followed by a blank space. There are eight spaces for the object name, followed by a period and three spaces for the extension. The extension is followed by two blank spaces, six spaces for the object size, two blank spaces, and three spaces for option flags (reserved for future use). The format looks like this:

```
<STX><CR><LF> DIR R: <CR><LF> *Name.ext(2sp.)(6 obj. sz.)(2sp.)(3 option flags) *Name.ext(2sp.)(6 obj. sz.)(2sp.)(3 option flags) <CR><LF> -xxxxxxx bytes free <CR><LF> <ETX> <STX> = start of text <CR><LR> = carriage return/line feed <ETX> = end on text
```

The command might be used in a stand-alone file to be issued to the printer at any time. The printer returns the directory listing as soon as possible, based on other tasks it might be performing when the command is received.

This command, like all ^ (caret) commands, is processed in the order that it is received by the printer.

Format ^HWd:o.x

This table identifies the parameters for this format:

| Parameters                              | Details                                                                                                                               |
|-----------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------|
| d = location to retrieve object listing | Accepted Values: R: , E: , B: , and A: Default Value: R:                                                                              |
| o = object name                         | Accepted Values: 1 to 8 alphanumeric characters Default Value: asterisk ( * ). A question mark ( ? ) can also be used.                |
| x = extension                           | Accepted Values: any extension conforming to Zebra conventions Default Value: asterisk ( * ). A question mark ( ? ) can also be used. |

<!-- image -->

<!-- image -->

- Example · Listed is an example of the ^HW command to retrieve from information R:

```
^XA ^HWR:*.*
```

^XZ

- Example · The printer returned this information as the Host Directory Listing: R:*.*
- *R:ARIALN1.FNT 49140
- *R:ARIALN2.FNT 49140
- *R:ARIALN3.FNT 49140
- *R:ARIALN4.FNT 49140
