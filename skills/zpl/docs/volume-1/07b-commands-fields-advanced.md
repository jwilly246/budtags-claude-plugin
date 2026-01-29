<!-- Source: ZPL II Programming Guide Volume 1 -->
<!-- Section: Advanced Field Commands (^FB, ^FC, ^FH, ^FM, ^FN, ^FP, ^FR, ^FV, ^FW, ^FX) -->
<!-- Generated: 2025-11-02 04:52:35 -->

| 80 402      |          |      293 |      256 |      268 |      201 |      176 |
| 100 300     |          |      218 |      190 |      200 |      150 |      131 |
| 140         | 144      |      105 |       91 |       96 |       72 |       63 |

Maximum Field Sizes

Example · This is an example of a Data Matrix bar code:

<!-- image -->

## Effects of ^BY on ^BX

w = module width (no effect)

r = ratio (no effect)

## h = height of symbol

If the dimensions of individual symbol elements are not specified in the ^BD command, the height of symbol value is divided by the required rows/columns, rounded, limited to a minimum value of one, and used as the dimensions of individual symbol elements.

<!-- image -->

## Field Data ( ^FD ) for ^BX

## Quality 000 to 140

- The \&amp; and || can be used to insert carriage returns, line feeds, and the backslash, similar to the PDF417. Other characters in the control character range can be inserted only by using ^FH . Field data is limited to 596 characters for quality 0 to 140 . Excess field data causes no symbol to print; if ^CV is active, INV ALID-L prints. The field data must correspond to a user-specified format ID or no symbol prints; if ^CV is active, INVALID-C prints.
- The maximum field sizes for quality 0 to 140 symbols are shown in the table in the g parameter.

## Quality 200

- If more than 3072 characters are supplied as field data, it is truncated to 3072 characters. This limits the maximum size of a numeric Data Matrix symbol to less than the 3116 numeric characters that the specification would allow. The maximum alphanumeric capacity is 2335 and the maximum 8-bit byte capacity is 1556.
- If ^FH is used, field hexadecimal processing takes place before the escape sequence processing described below.
- The underscore is the default escape sequence control character for quality 200 field data. A different escape sequence control character can be selected by using parameter g in the ^BX command.

The input string escape sequences can be embedded in quality 200 field data using the ASCII 95 underscore character ( \_ ) or the character entered in parameter g:

- \_X is the shift character for control characters (e.g., \_@=NUL,\_G=BEL,\_0 is PAD)
- \_1 to \_3 for FNC characters 1 to 3 (explicit FNC4, upper shift, is not allowed)
- FNC2 (Structured Append) must be followed by nine digits, composed of three-digit numbers with values between 1 and 254, that represent the symbol sequence and file identifier (for example, symbol 3 of 7 with file ID 1001 is represented by 2214001001)
- 5NNN is code page NNN where NNN is a three-digit code page value (for example, Code Page 9 is represented by \_5009)
- \_dNNN creates ASCII decimal value NNN for a code word (must be three digits)
- \_ in data is encoded by \_\_ (two underscores)

## ^BY

## Bar Code Field Default

Description The ^BY command is used to change the default values for the module width (in dots), the wide bar to narrow bar width ratio and the bar code height (in dots). It can be used as often as necessary within a label format.

Format ^BYw,r,h

This table identifies the parameters for this format:

| Parameters                             | Details                                                                                                                   |
|----------------------------------------|---------------------------------------------------------------------------------------------------------------------------|
| w = module width (in dots)             | Accepted Values: 1 to 10 Initial Value at power-up: 2                                                                     |
| r = wide bar to narrow bar width ratio | Accepted Values: 2.0 to 3.0 , in 0.1 increments This parameter has no effect on fixed-ratio bar codes. Default Value: 3.0 |
| h = bar code height (in dots)          | Initial Value at power-up: 10                                                                                             |

For parameter r , the actual ratio generated is a function of the number of dots in parameter w , module width. See Table 11 on page 102.

Example · Set module width ( w ) to 9 and the ratio ( r ) to 2.4. The width of the narrow bar is 9 dots wide and the wide bar is 9 by 2.4, or 21.6 dots. However, since the printer rounds out to the nearest dot, the wide bar is actually printed at 22 dots.

This produces a bar code with a ratio of 2.44 (22 divided by 9). This ratio is as close to 2.4 as possible, since only full dots are printed.

<!-- image -->

Module width and height ( w and h ) can be changed at anytime with the ^BY command, regardless of the symbology selected.

Table 11 • Shows module width ratios in dots

| Ratio Selected (r)   | Module Width in Dots (w)   | Module Width in Dots (w)   | Module Width in Dots (w)   | Module Width in Dots (w)   | Module Width in Dots (w)   | Module Width in Dots (w)   | Module Width in Dots (w)   | Module Width in Dots (w)   | Module Width in Dots (w)   | Module Width in Dots (w)   |
|----------------------|----------------------------|----------------------------|----------------------------|----------------------------|----------------------------|----------------------------|----------------------------|----------------------------|----------------------------|----------------------------|
|                      | 1                          | 2                          | 3                          | 4                          | 5                          | 6                          | 7                          | 8                          | 9                          | 10                         |
| 2.0                  | 2:1                        | 2:1                        | 2:1                        | 2:1                        | 2:1                        | 2:1                        | 2:1                        | 2:1                        | 2:1                        | 2:1                        |
| 2.1                  | 2:1                        | 2:1                        | 2:1                        | 2:1                        | 2:1                        | 2:1                        | 2:1                        | 2:1                        | 2:1                        | 2.1:1                      |
| 2.2                  | 2:1                        | 2:1                        | 2:1                        | 2:1                        | 2.2:1                      | 2.16:1                     | 2.1:1                      | 2.12:1                     | 2.1:1                      | 2.2:1                      |
| 2.3                  | 2:1                        | 2:1                        | 2.3:1                      | 2.25:1                     | 2.2:1                      | 2.16:1                     | 2.28:1                     | 2.25:1                     | 2.2:1                      | 2.3:1                      |
| 2.4                  | 2:1                        | 2:1                        | 2.3:1                      | 2.25:1                     | 2.4:1                      | 2.3:1                      | 2.28:1                     | 2.37:1                     | 2.3:1                      | 2.4:1                      |
| 2.5                  | 2:1                        | 2.5:1                      | 2.3:1                      | 2.5:1                      | 2.4:1                      | 2.5:1                      | 2.4:1                      | 2.5:1                      | 2.4:1                      | 2.5:1                      |
| 2.6                  | 2:1                        | 2.5:1                      | 2.3:1                      | 2.5:1                      | 2.6:1                      | 2.5:1                      | 2.57:1                     | 2.5:1                      | 2.5:1                      | 2.6:1                      |
| 2.7                  | 2:1                        | 2.5:1                      | 2.6:1                      | 2.5:1                      | 2.6:1                      | 2.6:1                      | 2.57:1                     | 2.65:1                     | 2.6:1                      | 2.7:1                      |
| 2.8                  | 2:1                        | 2.5:1                      | 2.6:1                      | 2.75:1                     | 2.8:1                      | 2.6:1                      | 2.7:1                      | 2.75:1                     | 2.7:1                      | 2.8:1                      |
| 2.9                  | 2:1                        | 2.5:1                      | 2.6:1                      | 2.75:1                     | 2.8:1                      | 2.8:1                      | 2.85:1                     | 2.87:1                     | 2.8:1                      | 2.9:1                      |
| 3.0                  | 3:1                        | 3:1                        | 3:1                        | 3:1                        | 3:1                        | 3:1                        | 3:1                        | 3:1                        | 3:1                        | 3:1                        |

Comments Once a ^BY command is entered into a label format, it stays in effect until another ^BY command is encountered.

## ^BZ

## POSTNET Bar Code

Description The POSTNET bar code is used to automate the handling of mail. POSTNET uses a series of five bars, two tall and three short, to represent the digits 0 to 9.

- ^BZ supports a print ratio of 2.0:1 to 3.0:1.
- Field data ( ^FD ) is limited to the width (or length, if rotated) of the label.

Format ^BZo,h,f,g

Important · If additional information about the POSTNET bar code is required, go to www.aimglobal.org , or contact the United States Postal Service and ask for Publication 25 Designing Letter Mail, which includes a full specification for POSTNET. You can also download Publication 25 from:

http://pe.usps.gov/cpim/ftp/pubs/pub25/pub25.pdf

This table identifies the parameters for this format:

| Parameters                               | Details                                                                                                                                                       |
|------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------|
| o = orientation                          | Accepted Values: N = normal R = rotated 90 degrees (clockwise) I = inverted 180 degrees B = read from bottom up, 270 degrees Default Value: current ^FW value |
| h = bar code height (in dots)            | Accepted Values: 1 to 32000 Default Value: value set by ^BY                                                                                                   |
| f = print interpretation line            | Accepted Values: Y (yes) or N (no) Default Value: N                                                                                                           |
| g = print interpretation line above code | Accepted Values: Y (yes) or N (no) Default Value: N                                                                                                           |

<!-- image -->

Example · This is an example of a POSTNET bar code:

<!-- image -->

## ^CC ~CC

## Change Carets

Description The ^CC command is used to change the format command prefix. The default prefix is the caret ( ^ ).

Format ^CCx

This table identifies the parameters for this format:

| Parameters                 | Details                                                                                                                                                              |
|----------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| x = caret character change | Accepted Values: any ASCII character Default Value: a parameter is required. If a parameter is not entered, the next character received is the new prefix character. |

Example · This is an example of how to change the ^CC format prefix to from a ^ to a / :

^XA

^CC/

/XZ

The forward slash (/) is set at the new prefix. Note the /XZ ending tag uses the new designated prefix character (/).

Example · This is an example of how to change the ~CC command prefix from ~ to a / :

~CC/

/XA/JUS/XZ

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

## ^CD ~CD

## Change Delimiter

Description The ^CD and ~CD commands are used to change the delimiter character. This character is used to separate parameter values associated with several ZPL II commands. The default delimiter is a comma (,).

Format

^CDa or ~CDa

This table identifies the parameters for this format:

| Parameters                     | Details                                                                                                                                                              |
|--------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| a = delimiter character change | Accepted Values: any ASCII character Default Value: a parameter is required. If a parameter is not entered, the next character received is the new prefix character. |

Example · This shows how to change the character delimiter to a period ( .) :

^XA

^CD;

^XZ

- To save, the JUS command is required. Here is an example using JUS :

~CD;

^XA^JUS^XZ

<!-- image -->

<!-- image -->

## ^CF

## Change Alphanumeric Default Font

Description The ^CF command sets the default font used in your printer. You can use the ^CF command to simplify your programs.

Format ^CFf,h,w

This table identifies the parameters for this format:

| Parameters                                | Details                                                                                |
|-------------------------------------------|----------------------------------------------------------------------------------------|
| f = specified default font                | Accepted Values: A through Z and 0 to 9 Initial Value at power-up: A                   |
| h = individual character height (in dots) | Accepted Values: 0 to 32000 Initial Value at power-up: 9                               |
| w = individual character width (in dots)  | Accepted Values: 0 to 32000 Initial Value at power-up: 5 or last permanent saved value |

Parameter f specifies the default font for every alphanumeric field. Parameter h is the default height for every alphanumeric field, and parameter w is the default width value for every alphanumeric field.

The default alphanumeric font is A. If you do not change the alphanumeric default font and do not use any alphanumeric field command ( ^AF ) or enter an invalid font value, any data you specify prints in font A.

Defining only the height or width forces the magnification to be proportional to the parameter defined. If neither value is defined, the last ^CF values given or the default ^CF values for height and width are used.

<!-- image -->

Example · This is an example of ^CF code and the result of the code:

Comments Any font in the printer, including downloaded fonts, EPROM stored fonts, and fonts A through Z and 0 to 9, can also be selected with ^CW .

## ^CI

## Change International Font

Description Zebra printers can print fonts using international character sets: U.S.A.1, U.S.A.2, UK, Holland, Denmark/Norway, Sweden/Finland, Germany, France 1, France 2, Italy, Spain, and several other sets.

The ^CI command enables you to call up the international character set you want to use for printing. You can mix character sets on a label.

This command allows character remapping. Any character within a font can be remapped to a different numerical position.

Format ^CIa,s1,d1,s2,d2,...

This table identifies the parameters for this format:

| Parameters                             | Details                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
|----------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| a = desired character set              | Accepted Values: 0 = U.S.A. 1 1 = U.S.A. 2 2 = U.K. 3 = Holland 4 = Denmark/Norway 5 = Sweden/Finland 6 = Germany 7 = France 1 8 = France 2 9 = Italy 10 = Spain 11 = Miscellaneous 12 = Japan (ASCII with Yen symbol) 13 = IBM Code Page 850 (see page 34) 14 = 16-bit (Unicode) encoded scalable fonts * 15 = Shift-JIS for scalable Japanese fonts ** 16 = EUC-Kanji for scalable fonts 17 = Unicode (for Unicode-encoded fonts) 18 to 23 = Reserved 24 = 8-bit access to Unicode-encoded fonts 25 = Reserved 26 = Asian fonts with ASCII Transparency *** |
| s1 = source 1 (character output image) | Accepted Values: decimals 0 to 255                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |

<!-- image -->

| Parameters                             | Details                                                                |
|----------------------------------------|------------------------------------------------------------------------|
| d1 = destination 1 (character input)   | Accepted Values: decimals 0 to 255                                     |
| s2 = source 2 (character output image) | Accepted Values: decimals 0 to 255                                     |
| d2 = destination 2 (character input)   | Accepted Values: decimals 0 to 255                                     |
| … = continuation of pattern            | Up to 256 source and destination pairs can be entered in this command. |

- *The encoding is controlled by the conversion table ( *.DAT ). The table generated by ZTools™ is the TrueType font's internal encoding (Unicode).
- **Shift-JIS encoding converts Shift-JIS to JIS and then looks up the JIS conversion in JIS.DAT . This table must be present for Shift-JIS to function.
- ***Now supports ASCII transparency for Asian fonts. 7F and less are treated as single byte characters. 80 to FE is treated as the first byte of a 2 byte character 8000 to FEFF in the encoding table for Unicode. Entire range is available for double byte characters.
- Example · This example remaps the Euro symbol (36) decimal to the dollar sign value (21) decimal. When the dollar sign character is sent to the printer, the Euro symbol prints.

^CI0,36,21
