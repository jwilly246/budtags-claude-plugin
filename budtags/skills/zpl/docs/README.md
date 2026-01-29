# ZPL II Programming Guide Documentation

This directory contains the ZPL II Programming Guide split into organized, easily-digestible markdown files optimized for AI consumption and quick reference.

## 📚 Documentation Structure

### Volume 1: Command Reference (~8,348 lines → 23 files)
Complete command reference with detailed syntax, parameters, and examples.

**Navigation:**
- `00-front-matter.md` - Copyright, TOC, proprietary information
- `01-introduction.md` - Getting started with ZPL II
- `02-basic-exercises.md` - 5 hands-on exercises for beginners

**Commands (organized alphabetically):**
- `03-commands-fonts.md` - Font commands (^A, ^A@)
- `04a-commands-barcodes-basic.md` - Basic 1D barcodes (Code 11, Code 39, etc.)
- `04b-commands-barcodes-upc-ean.md` - UPC/EAN family barcodes
- `04c-commands-barcodes-advanced.md` - Advanced 1D barcodes (Code 93, Code 128, etc.)
- `04d-commands-barcodes-2d.md` - 2D barcodes (QR Code, Data Matrix, Aztec, PDF417)
- `04e-commands-barcodes-specialty.md` - Specialty barcodes (MaxiCode, RSS, POSTNET)
- `05-commands-config.md` - Configuration commands (^C*)
- `06-commands-downloads.md` - Download commands for fonts, graphics (^D*, ~D*)
- `07a-commands-fields-basic.md` - Basic field commands (^FO, ^FD, ^FS, ^FT)
- `07b-commands-fields-advanced.md` - Advanced field operations (^FB, ^FM, etc.)
- `08-commands-graphics.md` - Graphic primitives (boxes, circles, lines)
- `09-commands-host-status.md` - Host communication and status queries
- `10-commands-images.md` - Image management commands
- `11-commands-system.md` - System configuration and job control
- `12-commands-labels-media.md` - Label layout and media handling
- `13-commands-network.md` - Network printer commands
- `14-commands-print.md` - Print control and parameters
- `15-commands-rfid.md` - RFID tag programming
- `16-commands-serial-misc.md` - Serial communication and miscellaneous commands
- `17-back-matter.md` - Index and contact information

### Volume 2: Programming Guide (~2,978 lines → 14 files)
Programming concepts, techniques, and advanced topics.

**Files:**
- `00-front-matter.md` - Document conventions and organization
- `01-zpl-basics.md` - ZPL II fundamentals and format structure
- `02-programming-exercises.md` - 6 progressive programming exercises
- `03a-advanced-stored-formats.md` - Stored formats, serialization, variable data
- `03b-advanced-control-commands.md` - Advanced control techniques
- `03c-advanced-graphics-networking.md` - Graphics handling and networking
- `04-fonts-barcodes.md` - Font types, matrices, barcode implementation
- `05-printer-configuration.md` - Printer setup via ZPL II
- `06-xml-super-host-status.md` - XML status reporting
- `07-real-time-clock.md` - RTC commands and date/time handling
- `08-mod-check-digits.md` - Check digit calculation (Mod 10/43)
- `09-error-detection-protocol.md` - Communication protocol and error handling
- `10-zb64-encoding.md` - Base64 encoding for ZPL
- `11-appendices.md` - Character sets and reference tables

## 🔍 Quick Reference

### Find a Command
**By function:**
- Fonts: `03-commands-fonts.md`
- Barcodes: `04a-` through `04e-` files
- Label layout: `07a-commands-fields-basic.md`, `12-commands-labels-media.md`
- Graphics: `08-commands-graphics.md`, `10-commands-images.md`
- Printing: `14-commands-print.md`
- RFID: `15-commands-rfid.md`

**By command prefix:**
- ^A* (fonts) → volume-1/03
- ^B* (barcodes) → volume-1/04a-04e
- ^C* (config) → volume-1/05
- ^D*, ~D* (downloads) → volume-1/06
- ^F* (fields) → volume-1/07a-07b
- ^G* (graphics) → volume-1/08
- ^H*, ~H* (host) → volume-1/09
- ^I* (images) → volume-1/10
- ^J*, ~J* (system) → volume-1/11
- ^L*, ^M* (labels/media) → volume-1/12
- ^N*, ~N* (network) → volume-1/13
- ^P*, ~P* (print) → volume-1/14
- ^R* (RFID) → volume-1/15
- ^S*, ^T*, ^W*, ^X*, ^Z* → volume-1/16

### Learn ZPL II Programming
1. Start with `volume-2/01-zpl-basics.md` (fundamentals)
2. Try `volume-2/02-programming-exercises.md` (hands-on)
3. Reference `volume-1/02-basic-exercises.md` (more practice)
4. Explore `volume-2/03a-advanced-stored-formats.md` (advanced techniques)

## 📊 File Size Information
- **Average file size:** ~300-400 lines
- **Total files:** 37 markdown files
- **Original Volume 1:** 8,348 lines → 23 files
- **Original Volume 2:** 2,978 lines → 14 files

## 📦 Original Files
Original unprocessed files are preserved in `originals/` directory.

## 🤖 AI-Friendly Features
- Each file is 200-600 lines (optimal for AI context windows)
- Metadata headers on every file (source, section, timestamp)
- Logical grouping by function and command prefix
- Clear file naming with sequential numbering
- Quick reference navigation in this README

## 📅 Generated
This documentation split was generated on: 2025-11-02 04:52:35

---
*Source: ZPL II Programming Guide (Zebra Technologies)*
*Part Numbers: 45541L-002 Rev. A (Vol 1), 45542L-002 Rev. A (Vol 2)*
