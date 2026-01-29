<!-- Source: ZPL II Programming Guide Volume 1 -->
<!-- Section: Print Commands (^P*, ~P*) -->
<!-- Generated: 2025-11-02 04:52:35 -->

- *R:ARIALN.FNT 49140
- *R:ZEBRA.GRF 8420
- -794292 bytes free R:RAM
- -DIR

<!-- image -->

<!-- image -->

## ^HY

## Upload Graphics

Description The ^HY command is an extension of the ^HG command. ^HY is used to upload graphic objects from the printer in any supported format.

Format ^HYd:o.x

This table identifies the parameters for this format:

| Parameters             | Details                                                                                                                 |
|------------------------|-------------------------------------------------------------------------------------------------------------------------|
| d = location of object | Accepted Values: R: , E: , B: , and A: Default Value: search priority                                                   |
| o = object name        | Accepted Values: 1 to 8 alphanumeric characters Default Value: an object name must be specified                         |
| x = extension          | Accepted Values: G = .GRF (raw bitmap format) P = .PNG (compressed bitmap format) Default Value: format of stored image |

Comments The image is uploaded in the form of a ~DY command. The data field of the returned ~DY command is always encoded in the ZB64 format.

## ^HZ

## Display Description Information

Description The ^HZ command is used for returning printer description information in XML format. The printer returns information on format parameters, object directories, individual object data, and print status information. For more information, see ZPL II Programming Guide Volume Two .

Format ^HZb

This table identifies the parameters for this format:

<!-- image -->

Format

^HZO,d:o.x,l

This table identifies the parameters for this format:

Example · This example shows the object data information for the object SAMPLE.GRF located on R: .

^XA

^HZO,R:SAMPLE.GRF

^XZ

<!-- image -->

<!-- image -->

## ^ID

## Object Delete

Description The ^ID command deletes objects, graphics, fonts, and stored formats from storage areas. Objects can be deleted selectively or in groups. This command can be used within a printing format to delete objects before saving new ones, or in a stand-alone format to delete objects.

The image name and extension support the use of the asterisk ( * ) as a wild card. This allows you to easily delete a selected groups of objects.

Format

^IDd:o.x

This table identifies the parameters for this format:

| Parameters                    | Details                                                                                               |
|-------------------------------|-------------------------------------------------------------------------------------------------------|
| d = location of stored object | Accepted Values: R: , E: , B: , and A: Default Value: R:                                              |
| o = object name               | Accepted Values: any 1 to 8 character name Default Value: if a name is not specified, UNKNOWN is used |
| x = extension                 | Accepted Values: any extension conforming to Zebra conventions Default Value: .GRF                    |

- Example · To delete stored formats from DRAM:

```
^XA ^IDR:*.ZPL^FS ^XZ
```

Example · To delete formats and images named SAMPLE from DRAM, regardless of the extension:

XA

^IDR:SAMPLE.*^FS

^XZ

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

- Example · To delete the image SAMPLE1.GRF prior to storing SAMPLE2.GRF

^XA

- ^FO25,25^AD,18,10
- ^FDDelete^FS
- ^FO25,45^AD,18,10
- ^FDthen Save^FS
- ^IDR:SAMPLE1.GRF^FS
- ^ISR:SAMPLE2.GRF^FS^XZ
- Example · In this , the * is a wild card, indicating that all objects with the .GRF extension are deleted:

^XA

^IDR:*.GRF^FS

^XZ

Comments When an object is deleted from R: , the object can no longer be used and memory is available for storage. This applies only to R: memory.

The ^ID command also frees up the uncompressed version of the object in DRAM.

If the name is specified as *.ZOB , all downloaded bar code fonts (or other objects) are deleted.

If the named downloadable object cannot be found in the R: , E: , B: , and A: device, the ^ID command is ignored.

:

<!-- image -->

## ^IL

## Image Load

Description The ^IL command is used at the beginning of a label format to load a stored image of a format and merge it with additional data. The image is always positioned at ^FO0,0 .

<!-- image -->

Important · See ^IS on page 182.

Using this technique to overlay the image of constant information with variable data greatly increases the throughput of the label format.

Format ^ILd:o.x

This table identifies the parameters for this format:

| Parameters                    | Details                                                                                                    |
|-------------------------------|------------------------------------------------------------------------------------------------------------|
| d = location of stored object | Accepted Values: R: , E: , B: , and A: Default Value: R:                                                   |
| o = object name               | Accepted Values: 1 to 8 alphanumeric characters Default Value: if a name is not specified, UNKNOWN is used |
| x = extension                 | Fixed Value: .GRF                                                                                          |

<!-- image -->

Example · This example recalls the stored image SAMPLE2.GRF from DRAM and overlays it with the additional data. The graphic was stored using the ^IS command. For the stored label format, see the ^IS on page 182 command.

<!-- image -->

<!-- image -->

## ^IM

## Image Move

Description The ^IM command performs a direct move of an image from storage area into the bitmap. The command is identical to the ^XG command (Recall Graphic), except there are no sizing parameters.

Format ^IMd:o.x

This table identifies the parameters for this format:

| Parameters                    | Details                                                                                                    |
|-------------------------------|------------------------------------------------------------------------------------------------------------|
| d = location of stored object | Accepted Values: R: , E: , B: , and A: Default Value: search priority                                      |
| o = object name               | Accepted Values: 1 to 8 alphanumeric characters Default Value: if a name is not specified, UNKNOWN is used |
| x = extension                 | Fixed Value: .GRF                                                                                          |

Example · This example moves the image SAMPLE.GRF from DRAM and prints it in several locations in its original size.

^XA

- ^FO100,100^IMR:SAMPLE.GRF^FS
- ^FO100,200^IMR:SAMPLE.GRF^FS
- ^FO100,300^IMR:SAMPLE.GRF^FS
- ^FO100,400^IMR:SAMPLE.GRF^FS
- ^FO100,500^IMR:SAMPLE.GRF^FS

^XZ

Comments By using the ^FO command, the graphic image can be positioned anywhere on the label.

The difference between ^IM and ^XG : ^IM does not have magnification, and therefore might require less formatting time. However, to take advantage of this, the image must be at a 8-, 16, or 32-bit boundary.

## ^IS

## Image Save

Description The ^IS command is used within a label format to save that format as a graphic image, rather than as a ZPL II script. It is typically used toward the end of a script. The saved image can later be recalled with virtually no formatting time and overlaid with variable data to form a complete label.

Using this technique to overlay the image of constant information with the variable data greatly increases the throughput of the label format.

\

Important · See ^IL on page 179.

Format ^ISd:o.x,p

This table identifies the parameters for this format:

| Parameters                    | Details                                                                                                    |
|-------------------------------|------------------------------------------------------------------------------------------------------------|
| d = location of stored object | Accepted Values: R: , E: , B: , and A: Default Value: R:                                                   |
| o = object name               | Accepted Values: 1 to 8 alphanumeric characters Default Value: if a name is not specified, UNKNOWN is used |
| x = extension                 | Accepted Values: .GRF or .PNG Default Value: .GRF                                                          |
| p = print image after storing | Accepted Values: Y (yes) or N (no) Default Value: Y                                                        |

<!-- image -->

Example · This is an example of using the ^IS command to save a label format to DRAM. The name used to store the graphic is SAMPLE2.GRF .

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

~JA

## Cancel All

Description The ~JA command cancels all format commands in the buffer. It also cancels any batches that are printing.

The printer stops after the current label is finished printing. All internal buffers are cleared of data and the DATA LED turn off.

Submitting this command to the printer scans the buffer and deletes only the data before the ~JA in the input buffer - it does not scan the remainder of the buffer for additional ~JA commands.

Format ~JA

<!-- image -->

## ^JB

## Initialize Flash Memory

Description The ^JB command is used to initialize the two types of Flash memory available in the Zebra printers.

Format ^JBa

This table identifies the parameters for this format:

| Parameters               | Details                                                                                                        |
