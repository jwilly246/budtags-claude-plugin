<!-- Source: Labelary API Documentation -->
<!-- Section: Image and Font Conversion -->
<!-- Generated: 2025-11-02 19:43:59 -->

# 7. Other Functionality

In addition to conversion from ZPL to other file formats, the Labelary API also provides a few other useful endpoints:

## 7.1. Converting images to ZPL graphics

You can convert images to ZPL graphics by using the following API endpoint:

```
POST http://api.labelary.com/v1/graphics
```

The submitted Content-Type must be `multipart/form-data`, with a `file` parameter containing the image to be converted.

By default, this endpoint returns ZPL, but the following output formats are available:

- **ZPL** (requested by sending an `Accept: application/zpl` request header, or by omitting the Accept request header entirely)
- **JSON** (requested by sending an `Accept: application/json` request header)
- **EPL** (requested by sending an `Accept: application/epl` request header)
- **IPL** (requested by sending an `Accept: application/ipl` request header)
- **DPL** (requested by sending an `Accept: application/dpl` request header)
- **SBPL** (requested by sending an `Accept: application/sbpl` request header)
- **PCL 5** (requested by sending an `Accept: application/pcl5` request header)
- **PCL 6** (requested by sending an `Accept: application/pcl6` request header)

### Examples

**Convert a local file named image.png to ZPL graphics:**
```bash
curl --request POST http://api.labelary.com/v1/graphics --form file=@image.png > image.zpl
```

**Convert a local file named image.png to EPL format:**
```bash
curl --request POST http://api.labelary.com/v1/graphics --form file=@image.png --header "Accept: application/epl" > image.epl
```

## 7.2. Converting TTF fonts to ZPL fonts

You can convert TrueType font files to ZPL font commands by using the following API endpoint:

```
POST http://api.labelary.com/v1/fonts
```

The submitted Content-Type must be `multipart/form-data`, with the following parameters:

- **file**: the TrueType font file to convert to ZPL (required)
- **path**: the printer path to use for the converted font file (optional, must match the regular expression `[REBA]:[A-Z0-9]{1,16}.TTF`)
- **name**: the single-letter shorthand font name to use (optional, must match the regular expression `[IKMOWXYZ]`)
- **chars**: if provided, the font will be subset to contain only the specified characters (optional, see additional information below)

If no path is provided, a printer path is chosen for you automatically. If no name is provided, a shorthand font name is not associated with the font.

### Font Subsetting

The `chars` parameter allows you to subset the font. Subsetting is the process of limiting the number of characters that the font is able to render in order to reduce its size. For example, if you plan to use your custom font to print only numbers, then setting `chars` to `0123456789` will subset the font accordingly, yielding a much smaller ZPL snippet. Note that some fonts do not allow subsetting. If you try to subset a font which does not allow it, you will receive an error.

**IMPORTANT:** Always check your font license to make sure that your intended use falls within the terms of the license.

### Examples

**Convert a local font file named Montserrat-Bold.ttf to ZPL font format:**
```bash
curl --request POST http://api.labelary.com/v1/fonts --form file=@Montserrat-Bold.ttf > font.zpl
```

**Convert with shorthand font name and subset to uppercase letters:**
```bash
curl --request POST http://api.labelary.com/v1/fonts \
  --form file=@Montserrat-Bold.ttf \
  --form name=Z \
  --form chars=ABCDEFGHIJKLMNOPQRSTUVWXYZ > font.zpl
```