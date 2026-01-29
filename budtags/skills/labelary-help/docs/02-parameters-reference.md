<!-- Source: Labelary API Documentation -->
<!-- Section: API Parameters Reference -->
<!-- Generated: 2025-11-02 19:43:59 -->

# 2. Parameters

## dpmm
**The desired print density, in dots per millimeter.**

Valid values are `6dpmm`, `8dpmm`, `12dpmm`, and `24dpmm`. See your printer's documentation for more information.

## width
**The label width, in inches.**

Any numeric value may be used.

## height
**The label height, in inches.**

Any numeric value may be used.

## index
**The label index (base 0).**

Some ZPL code will generate multiple labels, and this parameter can be used to access these different labels. In general though, the value of this parameter will be `0` (zero).

Note that this parameter is optional when requesting PDF documents. If not specified, the resultant PDF document will contain all labels (one label per page).

## zpl
**The ZPL code to render.**

Note that if you are using the GET HTTP method and the ZPL contains any hashes (#), they should be encoded (%23) in order to avoid parts of the ZPL being incorrectly interpreted as URL fragments.