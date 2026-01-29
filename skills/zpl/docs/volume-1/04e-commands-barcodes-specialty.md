<!-- Source: ZPL II Programming Guide Volume 1 -->
<!-- Section: Specialty Barcodes (^BD, ^BF, ^BR, ^BS, ^BT, ^BZ, ^BY) -->
<!-- Generated: 2025-11-02 04:52:35 -->

## Using N for the mode (m) parameter

<!-- image -->

Example · This example shows with application identifier 00 structure

<!-- image -->

- &gt;;&gt;8' sets it to subset C, function 1
- '00' is the application identifier followed by '17 characters', the check digit is selected using the 'Y' for the (e) parameter to automatically print the 20th character.
- you are not limited to 19 characters with mode set to N

## Using U for the mode (m) parameter

<!-- image -->

Example · The example shows the application identifier 00 format:

<!-- image -->

## UCC Case Mode

- Choosing U selects UCC Case mode. You will have exactly 19 characters available in ^FD .
- Subset C using FNC1 values are automatically selected.
- Check digit is automatically inserted.

<!-- image -->

## ZPL II CODE

^XA

^FO90,200^BY4

^B C N,256,Y,N,Y,N

^FD&gt;;&gt;80012345123451234512^FS ^XZ

## Using D for the mode (m) parameter

<!-- image -->

Example · This example shows application identifier 00 format ((x.11.x and above):

<!-- image -->

<!-- image -->

(0 at end of field data is a bogus character that is inserted as a place holder for the check digit the printer will automatically insert.

- Subset C using FNC1 values are automatically selected.
- Parentheses and spaces can be in the field data. '00' application identifier, followed by 17 characters, followed by bogus check digit place holder.
- Check digit is automatically inserted. The printer will automatically calculate the check digit and put it into the bar code and interpretation line.
- The interpretation line will also show the parentheses and spaces but will strip them out from the actual bar code.

## Printing the Interpretation Line

<!-- image -->

Example · This example shows printing the interpretation in a different font with firmware x.11.x and above:

<!-- image -->

<!-- image -->

The font command ( ^A0N,40,30 ) can be added and changed to alter the font and size of the interpretation line.

## With firmware version older than x.10.x

- A separate text field needs to be written.
- The interpretation line needs to be turned off.
- ^A0N,50,40 is the font and size selection for the separate text field.
- You have to make sure you enter the correct check digit in the text field.
- Creating a separate text field allows you to format the interpretation line with parentheses and spaces.

<!-- image -->

## Application Identifiers - UCC/EAN APPLICATION IDENTIFIER

An Application Identifier is a prefix code used to identify the meaning and the format of the data that follows it (data field).

There are AIs for identification, traceability, dates, quantity, measurements, locations, and many other types of information.

For example, the AI for batch number is 10, and the batch number AI is always followed by an alphanumeric batch code not to exceed 20-characters.

The UCC/EAN Application Identifiers provide an open standard that can be used and understood by all companies in the trading chain, regardless of the company that originally issued the codes.

Table 8 • UCC Application Identifier Table

| Data Content                                                                      | AI    | Plus The Following Data Structure    |
|-----------------------------------------------------------------------------------|-------|--------------------------------------|
| Serial Shipping Container Code (SSCC)                                             | 00    | exactly 18 digits                    |
| Shipping Container Code                                                           | 01    | exactly 14 digits                    |
| Batch Numbers                                                                     | 10    | up to 20 alpha numerics              |
| Production Date (YYMMDD)                                                          | 11    | exactly 6 digits                     |
| Packaging Date (YYMMDD)                                                           | 13    | exactly 6 digits                     |
| Sell By Date (YYMMDD)                                                             | 15    | exactly 6 digits                     |
| Expiration Date (YYMMDD)                                                          | 17    | exactly 6 digits                     |
| Product Variant                                                                   | 20    | exactly 2 digits                     |
| Serial Number                                                                     | 21    | up to 20 alpha numerics              |
| HIBCC Quantity, Date, Batch and Link                                              | 22    | up to 29 alpha numerics              |
| Lot Number                                                                        | 23*   | up to 19 alpha numerics              |
| Quantity Each                                                                     | 30    |                                      |
| Net Weight (Kilograms)                                                            | 310** | exactly 6 digits                     |
| Length, Meters                                                                    | 311** | exactly 6 digits                     |
| Width or Diameter (Meters)                                                        | 312** | exactly 6 digits                     |
| Depths ( Meters)                                                                  | 313** | exactly 6 digits                     |
| Area (Sq. Meters)                                                                 | 314** | exactly 6 digits                     |
| Volume (Liters)                                                                   | 315** | exactly 6 digits                     |
| Volume (Cubic Meters)                                                             | 316** | exactly 6 digits                     |
| Net Weight (Pounds)                                                               | 320** | exactly 6 digits                     |
| Customer PO Number                                                                | 400   | up to 29 alpha numerics              |
| Ship To (Deliver To) Location Code using EAN 13 or DUNS Number with leading zeros | 410   | exactly 13 digits                    |
| Bill To (Invoice To) Location Code using EAN 13 or DUNS Number with leading zeros | 411   | exactly 13 digits                    |
| Purchase from                                                                     | 412   | exactly 13 digits                    |
| Ship To (Deliver To) Postal Code within single postal authority                   | 420   | up to 9 alpha numerics               |
| Ship To (Deliver To) Postal Code with 3-digit ISO Country Code Prefix             | 421   | 3 digits plus up to 9 alpha numerics |
| Roll Products - width, length, core diameter, direction and splices               | 8001  | exactly 14 digits                    |
| Electronic Serial number for cellular mobile phone                                | 8002  | up to 20 alpha numerics              |

<!-- image -->

Note · Table 8 is a partial table showing the application identifiers. For more current and complete information, search the Internet for UCC Application Identifier .

<!-- image -->

For date fields that only need to indicate a year and month, the day field is set to "00".

* Plus one digit for length indication.
- ** Plus one digit for decimal point indication.

## Chaining several application identifiers (firmware x.11.x and later)

The FNC1, which is invoked by &gt;8 , is inserted just before the AI's so that the scanners reading the code sees the FNC1 and knows that an AI follows.

<!-- image -->

- Example · This is an example with the mode parameter set to A (automatic):
- ^XA
- ^BY2,2.5,193
- ^FO33,400
- ^BCN,,N,N,N,A
- ^FD&gt;;&gt;80204017773003486100008535&gt;8910001&gt;837252^FS

^FT33,625^AEN,0,0^FD(02)04017773003486(10)0008535(91) 0001(37)252^FS

^XZ

## Example · This is an example with the mode parameter set to U :

```
^XA ^BY3,2.5,193 ^FO33,200 ^BCN,,N,N,N,U ^FD>;>80204017773003486>8100008535>8910001>837252^FS ^FT33,455^A0N,30,30^FD(02)04017773003486(10)0008535(9 1)0001(37)252^FS ^XZ
```

<!-- image -->

Example · This is an example with the mode parameter set to D*:

```
^XA ^PON ^LH0,0 ^BY2,2.5,145 ^FO218,343 ^BCB,,Y,N,N,D ^FD(91)0005886>8(10)0000410549>8(99)05^FS ^XZ
```

D* - When trying to print the last Application Identifier with an odd number of characters, a problem existed when printing EAN128 bar codes using Mode D. The problem was fixed in firmware 60.13.0.6.

<!-- image -->

<!-- image -->

^BD

## UPS MaxiCode Bar Code

Description The ^BD command creates a two-dimensional, optically read (not scanned) code. This symbology was developed by UPS (United Parcel Service).

Notice that there are no additional parameters for this code and it does not generate an interpretation line. The ^BY command has no effect on the UPS MaxiCode bar code. However, the ^CV command can be activated.

Format ^BDm,n,t

This table identifies the parameters for this format:

| Parameters                  | Details                                                                                                                                                                                                                                    |
|-----------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| m = mode                    | Accepted Values: 2 = structured carrier message: numeric postal code (U.S.) 3 = structured carrier message: alphanumeric postal code (non-U.S.) 4 = standard symbol, secretary 5 = full EEC 6 = reader program, secretary Default Value: 2 |
| n = symbol number           | Accepted Values: 1 to 8 can be added in a structured document Default Value: 1                                                                                                                                                             |
| t = total number of symbols | Accepted Values: 1 to 8 , representing the total number of symbols in this sequence Default Value: 1                                                                                                                                       |

Example · This is an example of UPS MAXICODE - MODE 2 bar code:

<!-- image -->

```
ZPL II CODE ^XA ^FO50,50 ^CVY ^BD^FH^FD001840152382802 [)>_1E01_1D961Z00004951_1DUPSN_ 1D_06X610_1D159_1D1234567_1D1/1_ 1D_1DY_1D634 ALPHA DR_ 1DPITTSBURGH_1DPA_1E_04^FS ^FO30,300^A0,30,30^FDMode2^FS ^XZ
```

<!-- image -->

## Special Considerations for ^FD when Using ^BD

The ^FD statement is divided into two parts: a high priority message ( hpm ) and a low priority message ( lpm ). There are two types of high priority messages. One is for a U.S. Style Postal Code; the other is for a non-U.S. Style Postal Code. The syntax for either of these high priority messages must be exactly as shown or an error message is generated.

<!-- formula-not-decoded -->

This table identifies the parameters for this format:

| Parameters                                                       | Details                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
|------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| <hpm> = high priority message (applicable only in Modes 2 and 3) | Accepted Values: 0 to 9 , except where noted U.S. Style Postal Code (Mode 2) <hpm> = aaabbbcccccdddd aaa = three-digit class of service bbb = three-digit country zip code ccccc = five-digit zip code dddd = four-digit zip code extension (if none exists, four zeros (0000) must be entered) non-U.S. Style Postal Code (Mode 3) <hpm> = aaabbbcccccc aaa = three-digit class of service bbb = three-digit country zip code ccccc = six-digit zip code ( A through Z or 0 to 9 )                                                                                                                           |
| <lpm> = low priority message (only applicable in Modes 2 and 3)  | GS is used to separate fields in a message (0x1D). RS is used to separate format types (0x1E). EOT is the end of transmission characters. Message Header [)>RS Transportation Data Format Header 01GS96 Tracking Number* <tracking number> SCAC* GS<SCAC> UPS Shipper Number GS<shipper number> Julian Day of Pickup GS<day of pickup> Shipment ID Number GS<shipment ID number> Package n/x GS<n/x> Package Weight GS<weight> Address Validation GS<validation> Ship to Street Address GS<street address> Ship to City GS<city> Ship to State GS<state> RS RS End of Message EOT ( * Mandatory Data for UPS) |

<!-- image -->

## Comments

- The formatting of &lt;hpm&gt; and &lt;lpm&gt; apply only when using Modes 2 and 3. Mode 4, for example, takes whatever data is defined in the ^FD command and places it in the symbol.
- UPS requires that certain data be present in a defined manner. When formatting MaxiCode data for UPS, always use uppercase characters. When filling in the fields in the &lt;lpm&gt; for UPS, follow the data size and types specified in Guide to Bar Coding with UPS .
- If you do not choose a mode, the default is Mode 2. If you use non-U.S. Postal Codes, you probably get an error message (invalid character or message too short). When using nonU.S. codes, use Mode 3.
- ZPL II doesn't automatically change your mode based on the zip code format.
- When using special characters, such as GS, RS, or EOT, use the ^FH command to tell ZPL II to use the hexadecimal value following the underscore character ( \_ ).

<!-- image -->

## ^BE

## EAN-13 Bar Code

Description The ^BE command is similar to the UPC-A bar code. It is widely used throughout Europe and Japan in the retail marketplace.

The EAN-13 bar code has 12 data characters, one more data character than the UPC-A code. An EAN-13 symbol contains the same number of bars as the UPC-A, but encodes a 13th digit into a parity pattern of the left-hand six digits. This 13th digit, in combination with the 12th digit, represents a country code.

- ^BE supports fixed print ratios.
- Field data ( ^FD ) is limited to exactly 12 characters. ZPL II automatically truncates or pads on the left with zeros to achieve the required number of characters.
- When using JAN-13 (Japanese Article Numbering), a specialized application of EAN-13, the first two non-zero digits sent to the printer must be 49.

Format ^BEo,h,f,g

Important · If additional information about the EAN-13 bar code is required, go to www.aimglobal.org .

This table identifies the parameters for this format:

| Parameters                               | Details                                                                                                                                                       |
|------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------|
| o = orientation                          | Accepted Values: N = normal R = rotated 90 degrees (clockwise) I = inverted 180 degrees B = read from bottom up, 270 degrees Default Value: current ^FW value |
| h = bar code height (in dots)            | Accepted Values: 1 to 32000 Default Value: value set by ^BY                                                                                                   |
| f = print interpretation line            | Accepted Values: Y (yes) or N (no) Default Value: Y                                                                                                           |
| g = print interpretation line above code | Accepted Values: Y (yes) or N (no) Default Value: N                                                                                                           |

<!-- image -->

<!-- image -->

Example · This is an example of an EAN-13 bar code:

<!-- image -->
