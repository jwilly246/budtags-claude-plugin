<!-- Source: ZPL II Programming Guide Volume 1 -->
<!-- Section: Basic Field Commands (^FO, ^FD, ^FS, ^FT) -->
<!-- Generated: 2025-11-02 04:52:35 -->

| <parity data>             | M '    | (0x8F)                              |
| <error correction level>  | L      | (high-density level)                |
| <input mode>              | M '    | (manual input)                      |
| <character mode>          | N      | (numeric data)                      |
| <data character string>   | '      | 0123456789                          |
| <character mode>          | A      | (alphanumeric data)                 |
| <data character string>   | '      | 12AABB                              |
| <character mode>          | B 0006 | (8-bit byte data) (number of bytes) |
| <data character string>   |        | qrcode                              |

<!-- image -->

^BR

## RSS (Reduced Space Symbology) Bar Code

Description The ^BR command is bar code types for space-constrained identification from EAN International and the Uniform Code Council, Inc.

Format ^BRa,b,c,d,e,f

This table identifies the parameters for this format:

| Parameters                              | Details                                                                                                                                                                                                                                        |
|-----------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| a = orientation                         | Accepted Values: N = Normal R = Rotated I = Inverted B = Bottom-up Default Value: R                                                                                                                                                            |
| b = symbology type in the RSS-14 family | Accepted Values: 1 = RSS14 2 = RSS14 Truncated 3 = RSS14 Stacked 4 = RSS14 Stacked Omnidirectional 5 = RSS Limited 6 = RSS Expanded 7 = UPC-A 8 = UPC-E 9 = EAN-13 10 = EAN-8 11 = UCC/EAN-128 &CC-A/B 12 = UCC/EAN-128 &CC-C Default Value: 1 |
| c = magnification factor                | Accepted Values: 1 to 10 Default Values: 24 dot = 6 , 12 dot is 3 , 8 dot and lower is 2 12 dot = 6 , > 8 dot is 3 , 8 dot and less is 2 )                                                                                                     |
| d = separator height                    | Accepted Values: 1 or 2 Default Value: 1                                                                                                                                                                                                       |

| Parameters                                | Details                                                                                                                                         |
|-------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------|
| e = bar code height                       | The bar code height only affects the linear portion of the bar code. Only UCC/EAN &CC-A/B/C. Accepted Values: 1 to 32000 dots Default Value: 25 |
| f = the segment width (RSS expanded only) | Accepted Values: 2 to 22 , even numbers only, in segments per line Default Value: 22                                                            |

## Example · This is an example of Symbology Type 7 - UPC-A:

^XA

^FO10,10^BRN,7,5,2,100^FD12345678901|this is composite info^FS

^XZ

## Example · This is an example of Symbology Type 1 - RSS14:

^XA

^FO10,10^BRN,1,5,2,100^FD12345678901|this is composite info^FS

^XZ

<!-- image -->

<!-- image -->

## ^BS

## UPC/EAN Extensions

Description The ^BS command is the two-digit and five-digit add-on used primarily by publishers to create bar codes for ISBNs (International Standard Book Numbers). These extensions are handled as separate bar codes.

The ^BS command is designed to be used with the UPC-A bar code ( ^BU ) and the UPC-E bar code ( ^B9 ).

- ^BS supports a fixed print ratio.
- Field data ( ^FD ) is limited to exactly two or five characters. ZPL II automatically truncates or pads on the left with zeros to achieve the required number of characters.

Format ^BSo,h,f,g

Important · If additional information about the UPC/EAN bar code is required, go to www.aimglobal.org .

This table identifies the parameters for this format:

| Parameters                               | Details                                                                                                                                                       |
|------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------|
| o = orientation                          | Accepted Values: N = normal R = rotated 90 degrees (clockwise) I = inverted 180 degrees B = read from bottom up, 270 degrees Default Value: current ^FW value |
| h = bar code height (in dots)            | Accepted Values: 1 to 32000 Default Value: value set by ^BY                                                                                                   |
| f = print interpretation line            | Accepted Values: Y (yes) or N (no) Default Value: Y                                                                                                           |
| g = print interpretation line above code | Accepted Values: Y (yes) or N (no) Default Value: Y                                                                                                           |

<!-- image -->

<!-- image -->

Example · This is an example of a UPC/EAN Two-digit bar code:

<!-- image -->

<!-- image -->

- Example · This is an example of a UPC/EAN Five-digit bar code:

<!-- image -->

<!-- image -->

Care should be taken in positioning the UPC/EAN extension with respect to the UPC-A or UPC-E code to ensure the resulting composite code is within the UPC specification.

<!-- image -->

<!-- image -->

For UPC codes, with a module width of 2 (default), the field origin offsets for the extension are:

## Example · This is an example of a UPC-A:

| Supplement Origin X - Offset   | Adjustment Y - Offset   |
|--------------------------------|-------------------------|
| 209 Dots Normal                | 21 Dots                 |
| 0 Rotated                      | 209 Dots                |

This is an example of a UPC-E:

| Supplement Origin X - Offset   | Adjustment Y - Offset   |
|--------------------------------|-------------------------|
| 122 Dots                       | 21 Dots                 |
| 0                              | 122 Dots                |

Additionally, the bar code height for the extension should be 27 dots (0.135 inches) shorter than that of the primary code. A primary UPC code height of 183 dots (0.900 inches) requires an extension height of 155 dots (0.765 inches).

Example · This example illustrates how to create a normal UPC-A bar code for the value 7000002198 with an extension equal to 04414:

<!-- image -->

## ^BT

## TLC39 bar code

Description The ^BT bar code is the standard for the TCIF can tag telecommunications equipment.

The TCIF CLEI code, which is the Micro-PDF417 bar code, is always four columns. The firmware must determine what mode to use based on the number of characters to be encoded.

Format ^BTo,w1,r1,h1,w2,h2

This table identifies the parameters for this format:

| Parameters                                               | Details                                                                                                                                           |
|----------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------|
| o = orientation                                          | Accepted Values: N = normal R = rotated I = inverted B = bottom up                                                                                |
| w1 = width of the Code 39 bar code                       | Accepted Value (in dots): 1 to 10 Default Value (600 dpi printers): 4 Default Value (200- and 300 dpi printer): 2                                 |
| r1 = wide to narrow bar width ratio the Code 39 bar code | Accepted Values: 2.0 to 3.0(increments of 0.1) Default Value: 2.0                                                                                 |
| h1 = height of the Code 39 bar code                      | Accepted Values (in dots): 1 to 9999 Default Value (600 dpi printer): 120 Default Value (300 dpi printer): 60 Default Value (200 dpi printer): 40 |
| h2 = row height of the Micro- PDF417 bar ode             | Accepted Values (in dots): 1 to 255 Default Value (600 dpi printer): 8 Default Value (200- and 300 dpi printers): 4                               |
| w2 = narrow bar width of the Micro-PDF417 bar code       | Accepted Values (in dots): 1 to 10 Default Value (600 dpi printer): 4 Default Value (200- and 300 dpi printers): 2                                |

<!-- image -->

## Example · TLC39 Bar Code

This is an example on how to print TLC39 bar code. The callouts identify the key components and are followed by a detailed description below:

Use the command defaults to get results that are in compliance with TCIF industry standards; regardless of printhead density.

<!-- image -->

- 1 ECI Number. If the seventh character is not a comma, only Code 39 prints. This means if more than 6 digits are present, Code 39 prints for the first six digits (and no Micro-PDF symbol is printed).
- Must be 6 digits.
- Firmware generates invalid character error if the firmware sees anything but 6 digits.
- This number is not padded.
- 2 Serial number. The serial number can contain up to 25 characters and is variable length. The serial number is stored in the Micro-PDF symbol. If a comma follows the serial number, then additional data is used below.
- •
- If present, must be alphanumeric (letters and numbers, no punctuation).

This value is used if a comma follows the ECI number.

- 3 Additional data. If present, it is used for things such as a country code. Data cannot exceed 150 bytes. This includes serial number commas.
- Additional data is stored in the Micro-PDF symbol and appended after the serial number. A comma must exist between each maximum of 25 characters in the additional fields.
- Additional data fields can contain up to 25 alphanumeric characters per field. The result is:

## ZPL II CODE

^XA^FO100, 100^BT^FD123456, AB C d12345678901234, 5551212, 88899

^FS^XZ

<!-- image -->

<!-- image -->

## ^BU

## UPC-A Bar Code

Description The ^BU command produces a fixed length, numeric symbology. It is primarily used in the retail industry for labeling packages. The UPC-A bar code has

11 data characters. The 6 dot/mm, 12 dot/mm, and 24 dot/mm printheads produce the UPC-A

bar code (UPC/EAN symbologies) at 100 percent size. However, an 8 dot/mm printhead produces the UPC/EAN symbologies at a magnification factor of 77 percent.

- ^BU supports a fixed print ratio.
- Field data ( ^FD ) is limited to exactly 11 characters. ZPL II automatically truncates or pads on the left with zeros to achieve required number of characters.

Format ^BUo,h,f,g,e

Important · If additional information about the UPC-A bar code is required, go to www.aimglobal.org .

This table identifies the parameters for this format:

| Parameters                               | Details                                                                                                                                                       |
|------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------|
| o = orientation                          | Accepted Values: N = normal R = rotated 90 degrees (clockwise) I = inverted 180 degrees B = read from bottom up, 270 degrees Default Value: current ^FW value |
| h = bar code height (in dots)            | Accepted Values: 1 to 9999 Default Value: value set by ^BY                                                                                                    |
| f = print interpretation line            | Accepted Values: Y (yes) or N (no) Default Value: Y                                                                                                           |
| g = print interpretation line above code | Accepted Values: Y (yes) or N (no) Default Value: N                                                                                                           |
| e = print check digit                    | Accepted Values: Y (yes) and N (no) Default Value: Y                                                                                                          |

<!-- image -->

The font style of the interpretation line depends on the modulus (width of narrow bar) selected in ^BY :

- 6 dot/mm printer: a modulus of 2 dots or greater prints with an OCR-B interpretation line; a modulus of 1 dot prints font A.
- 8 dot/mm printer: a modulus of 3 dots or greater prints with an OCR-B interpretation line; a modulus of 1 or 2 dots prints font A.
- 12 dot/mm printer: a modulus of 5 dots or greater prints with an OCR-B interpretation line; a modulus of 1, 2, or 3 dots prints font A.
- 24 dot/mm printer: a modulus of 9 dots or greater prints with an OCR-B interpretation line; a modulus of 1 to 8 dots prints font A.
- Example · This is an example of a UPC-A bar code with extension:

<!-- image -->

<!-- image -->

Comments The UPC-A bar code uses the Mod 10 check digit scheme for error checking. For further information on Mod 10, see ZPL II Programming Guide Volume Two .

## ^BX

## Data Matrix Bar Code

Description The ^BX command creates a two-dimensional matrix symbology made up of square modules arranged within a perimeter finder pattern.

The ability to create a rectangular Datamatrix bar code is not available as a ZPL coding option.

Format ^BXo,h,s,c,r,f

This table identifies the parameters for this format:

| Parameters                                           | Details                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
|------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| o = orientation                                      | Accepted Values: N = normal R = rotated 90 degrees (clockwise) I = inverted 180 degrees B = read from bottom up, 270 degrees Default Value: current ^FW value                                                                                                                                                                                                                                                                                                                                                                                       |
| h = dimensional height of individual symbol elements | Accepted Values: 1 to the width of the label The individual elements are square -this parameter specifies both module and row height. If this parameter is zero (or not given), the h parameter (bar height) in ^BY is used as the approximate symbol height.                                                                                                                                                                                                                                                                                       |
| s = quality level                                    | Accepted Values: 0 , 50 , 80 , 100 , 140 , 200 Default Value: 0 Quality refers to the amount of data that is added to the symbol for error correction. The AIM specification refers to it as the ECC value. ECC 50, ECC 80, ECC 100, and ECC 140 use convolution encoding; ECC 200 uses Reed-Solomon encoding. For new applications, ECC 200 is recommended. ECC 000-140 should be used only in closed applications where a single party controls both the production and reading of the symbols and is responsible for overall system performance. |
| c = columns to encode                                | Accepted Values: 9 to 49 Odd values only for quality 0 to 140 (10 to 144); even values only for quality 200.                                                                                                                                                                                                                                                                                                                                                                                                                                        |

| Parameters                                               | Details                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
|----------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| r = rows to encode                                       | Accepted Values: 9 to 49 Odd values only for quality 0 to 140 (10 to 144); even values only for quality 200. The number of rows and columns in the symbol is automatically determined. You might want to force the number of rows and columns to a larger value to achieve uniform symbol size. In the current implementation, quality 0 to 140 symbols are square, so the larger of the rows or columns supplied are used to force a symbol to that size. If you attempt to force the data into too small of a symbol, no symbol is printed. If a value greater than 49 is entered, the rows or columns value is set to zero and the size is determined normally. If an even value is entered, it generates INVALID-P (invalid parameter). If a value less than 9 but not 0, or if the data is too large for the forced size, no symbol prints; if ^CV is active, INVALID-L prints. |
| f = format ID (0 to 6) -not used with quality set at 200 | Accepted Values: 1 = field data is numeric + space (0..9,') - No \&'' 2 = field data is uppercase alphanumeric + space (A..Z,'') - No \&'' 3 = field data is uppercase alphanumeric + space, period, comma, dash, and slash (0..9,A..Z,'.-/') 4 = field data is upper-case alphanumeric + space (0..9,A..Z,'') - no \&'' 5 = field data is full 128 ASCII 7-bit set 6 = field data is full 256 ISO 8-bit set Default Value: 6                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| g = escape sequence controlcharacter                     | Accepted Values: any character Default Value: ~ (tilde) This parameter is used only if quality 200 is specified. It is the escape character for embedding special control sequences within the field data. For ^BX usage, see ^FD on page 135. * The default value of g will continue to be underscore ( _ ) for anyone with firmware versions: V60.13.0.12, V60.13.0.12Z, V60.13.0.12B, or V60.13.0.12ZB. For these firmware versions, the g parameter can continue to be modified as needed.                                                                                                                                                                                                                                                                                                                                                                                       |

<!-- image -->

Table 10 • Maximum Field Sizes

| ECC LEVEL   | ID = 1   |   ID = 2 |   ID = 3 |   ID = 4 |   ID = 5 |   ID = 6 |
|-------------|----------|----------|----------|----------|----------|----------|
| 0           | 596      |      452 |      394 |      413 |      310 |      271 |
| 50          | 457      |      333 |      291 |      305 |      228 |      200 |
