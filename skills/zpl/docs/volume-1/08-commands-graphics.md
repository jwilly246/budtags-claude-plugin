<!-- Source: ZPL II Programming Guide Volume 1 -->
<!-- Section: Graphics Commands (^G*, ~G*) -->
<!-- Generated: 2025-11-02 04:52:35 -->


The font selected determines the shape and resolution of the printed symbol.

<!-- image -->

## International Character Sets

```
Hex 23 4 5 5 5 5 6 7 7 7 7 30 0 B C D E 0 B C D E CI0 # 0 ? 中 A ? { CI1 # 0 ? 23 A ? %4 % %4 N E ? L 7 A ? { 了 f 0 } 5 L A ? { 2 CI4 # 0 ? E A N O C15 U E i O U a a. u C16 # 0 9 A o U V u C17 0 a 一 一 e = Q = # 0 S e 一 6 e e Q C19 0 g 一 e n a 一 CI10 # 0 9 1 A ? S CI11 0 E A A a e L CI12 # 0 ? 一 A V ? N CI13 # 0 ? 1
```

Note · ^CI 13 = US keyboard

Comments The space character cannot be remapped for any font.

<!-- image -->

<!-- image -->

^CM

## Change Memory Letter Designation

Description The ^CM command allows you to reassign a letter designation to the printer's memory devices. If a format already exists, you can reassign the memory device to the corresponding letter without forcing, altering, or recreating the format itself.

Using this command affects every subsequent command that refers to specific memory locations.

Format ^CMa,b,c,d

This table identifies the parameters for this format:

| Parameters                          | Details                                                         |
|-------------------------------------|-----------------------------------------------------------------|
| a = memory alias letter designation | Accepted Values: B: , E: , R: , A: , and NONE Default Value: B: |
| b = memory alias letter designation | Accepted Values: B: , E: , R: , A: , and NONE Default Value: E: |
| c = memory alias letter designation | Accepted Values: B: , E: , R: , A: , and NONE Default Value: R: |
| d = memory alias letter designation | Accepted Values: B: , E: , R: , A: , and NONE Default Value: A: |

Comments If two or more parameters specify the same letter designator, all letter designators are set to their default values.

If any of the parameters are out of specification, the command is ignored.

Example · This example designates letter E: to point to the B: memory device, and the letter B: to point to the E: memory device.

```
^XA ^CME,B,R,A ^JUS ^XA
```

Comments It is recommended that after entering the ^CM command, ^JUS is entered to save changes to EEPROM. Any duplicate parameters entered reset the letter designations back to the default.

<!-- image -->

<!-- image -->

## ^CO

## Cache On

Description The ^CO command is used to change the size of the character cache. By definition, a character cache (referred to as cache) is a portion of the DRAM reserved for storing scalable characters. All printers have a default 40K cache that is always turned on. The maximum single character size that can be stored, without changing the size of the cache, is 450 dots by 450 dots.

There are two types of fonts used in Zebra printers: bitmapped and scalable. Letters, numbers, and symbols in a bitmapped font have a fixed size (for example: 10 points, 12 points, 14 points). By comparison, scalable fonts are not fixed in size.

Because their size is fixed, bitmapped fonts can be moved quickly to the label. In contrast, scalable fonts are much slower because each character is built on an as-needed basis before it is moved to the label. By storing scaled characters in a cache, they can be recalled at a much faster speed.

The number of characters that can be stored in the cache depends on two factors: the size of the cache (memory) and the size of the character (in points) being saved. The larger the point size, the more space in the cache it uses. The default cache stores every scalable character that is requested for use on a label. If the same character, with the same rotation and size is used again, it is quickly retrieved from cache.

It is possible that after a while the print cache could become full. Once the cache is full, space for new characters is obtained by eliminating an existing character from the print cache. Existing characters are eliminated by determining how often they have been used. This is done automatically. For example, a 28-point Q that was used only once would be a good candidate for elimination from the cache.

Maximum size of a single print cache character is 1500 dots by 1500 dots. This would require a cache of 274K.

When the cache is too small for the desired style, smaller characters might appear but larger characters do not. If possible, increase the size of the cache.

Format ^COa,b,c

This table identifies the parameters for this format:

| Parameters   | Details                                             |
|--------------|-----------------------------------------------------|
| a = cache on | Accepted Values: Y (yes) or N (no) Default Value: Y |

<!-- image -->

| Parameters                                                  | Details                                                                                                             |
|-------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------|
| b = amount of additional memory to be added to cache (in K) | Accepted Values: any size up to total memory available Default Value: 40                                            |
| c = cache type                                              | Accepted Values: 0 = cache buffer (normal fonts) 1 = internal buffer (recommended for Asian fonts) Default Value: 0 |

Example · To resize the print cache to 62K, assuming a 22K existing cache:

^COY,40

To resize the print cache to 100K, assuming a 22K existing cache:

<!-- formula-not-decoded -->

## Print Cache Performance

For printing large characters, memory added to the cache by the ^CO command is not physically added to the 22K cache already in the printer. In the second example above, the resulting 100K cache is actually two separate blocks of memory, 22K and 78K.

Because large characters need contiguous blocks of memory, a character requiring a cache of 90K would not be completely stored because neither portion of the 100K cache is big enough. Therefore, if large characters are needed, the ^CO command should reflect the actual size of the cache you need.

Increasing the size of the cache improves the performance in printing scalable fonts. However, the performance decreases if the size of the cache becomes large and contains too many characters. The performance gained is lost because of the time involved searching cache for each character.

Comments The cache can be resized as often as needed. Any characters in the cache when it is resized are lost. Memory used for the cache reduces the space available for label bitmaps, graphic, downloaded fonts, et cetera.

Some Asian fonts require an internal working buffer that is much larger than the normal cache. Since most fonts do not require this larger buffer, it is now a selectable configuration option. Printing with the Asian fonts greatly reduces the printer memory available for labels, graphics, fonts, and formats.

<!-- image -->

<!-- image -->

## ^CT ~CT

## Change Tilde

Description The ^CT and ~CT commands are used to change the control command prefix. The default prefix is the tilde (~).

Format ^CTa or ~CTa

This table identifies the parameters for this format:

| Parameters                           | Details                                                                                                                                                                       |
|--------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| a = change control command character | Accepted Values: any ASCII character Default Value: a parameter is required. If a parameter is not entered, the next character received is the new control command character. |

Example •

This is an example of how to change the control command prefix from a

a

~

:

^XA

^CT+

^XZ

+DGR:GRAPHIC.GRF,04412,010

^, to

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

^CV

## Code Validation

Description The ^CV command acts as a switch to turn the code validation function on and off. When this command is turned on, all bar code data is checked for these error conditions:

- character not in character set
- check-digit incorrect
- data field too long (too many characters)
- data field too short (too few characters)
- parameter string contains incorrect data or missing parameter

When invalid data is detected, an error message and code is printed in reverse image in place of the bar code. The message reads INVALID - X where X is one of these error codes:

P = parameter string contains incorrect data

C = character not in character set E = check-digit incorrect L = data field too long S = data field too short (occurs only on select bar codes)

Once turned on, the ^CV command remains active from format to format until turned off by another ^CV command or the printer is turned off. The command is not permanently saved.

Format ^CVa

This table identifies the parameters for this format:

| Parameters          | Details                                             |
|---------------------|-----------------------------------------------------|
| a = code validation | Accepted Values: Y (yes) or N (no) Default Value: N |

<!-- image -->

<!-- image -->

Example · The examples below show the error labels ^CVY generates when incorrect field data is entered. Compare the letter following INVALID to the listing on the previous page.

<!-- image -->

Comments If more than one error exists, the first error detected is the one displayed.

The ^CV command tests the integrity of the data encoded into the bar code. It is not used for (or to be confused with) testing the scan-integrity of an image or bar code.

<!-- image -->

<!-- image -->

^CW

## Font Identifier

Description All built-in fonts are referenced using a one-character identifier. The ^CW command assigns a single alphanumeric character to a font stored in DRAM, memory card, EPROM, or Flash.

If the assigned character is the same as that of a built-in font, the downloaded font is used in place of the built-in font. The new font is printed on the label wherever the format calls for the built-in font. If used in place of a built-in font, the change is in effect only until power is turned off.

If the assigned character is different, the downloaded font is used as an additional font. The assignment remains in effect until a new command is issued or the printer is turned off.

Format ^CWa,d:o.x

This table identifies the parameters for this format:

| Parameters                                                                                   | Details                                                                                                 |
|----------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------|
| a = letter of existing font to be substituted, or new font to be added                       | Accepted Values: A through Z and 0 to 9 Default Value: a one-character entry is required                |
| d = device to store font in (optional)                                                       | Accepted Values: R: , E: , B: , and A: Default Value: R:                                                |
| o = name of the downloaded font to be substituted for the built-in, or as an additional font | Accepted Values: any name up to 8 characters Default Value: if a name is not specified, UNKNOWN is used |
| x = extension                                                                                | Fixed Value: .FNT                                                                                       |

<!-- image -->

- Example •

## These examples show how to use:

- MYFONT.FNT stored in DRAM whenever a format calls for Font A:

^XA

^CWA,R:MYFONT.FNT

^XZ

- MYFONT.FNT stored in DRAM as additional Font Q:

^XA

^CWQ,R:MYFONT.FNT

^XZ

- NEWFONT.FNT stored in DRAM whenever a format calls for font F:

^XA

^CWF,R:NEWFONT.FNT

^XZ

Label Listing Before Assignment     Label Listing After Assignment

<!-- image -->

<!-- image -->
