<!-- Source: ZPL II Programming Guide Volume 2 -->
<!-- Section: Chapter 4: Fonts and Bar Codes -->
<!-- Generated: 2025-11-02 04:52:35 -->

## Printer Configuration Using ZPL II

This section discusses how to use the ZPL II printer configuration commands.

## Contents

| Printer Configuration Commands. . . . .             |   72 |
|-----------------------------------------------------|------|
| Print Mode . . . . . . . . . . . . . . . . . . . .  |   73 |
| Media Tracking. . . . . . . . . . . . . . . . .     |   73 |
| Media Type . . . . . . . . . . . . . . . . . . .    |   73 |
| Media Darkness. . . . . . . . . . . . . . . .       |   74 |
| Label Top Position . . . . . . . . . . . . . .      |   74 |
| Set Media Sensors. . . . . . . . . . . . . .        |   74 |
| Mode Protection. . . . . . . . . . . . . . . .      |   75 |
| Reprint After Error . . . . . . . . . . . . . .     |   75 |
| Configuration Update. . . . . . . . . . . .         |   75 |
| Set ZPL . . . . . . . . . . . . . . . . . . . . . . |   75 |
| Setting Up Customized Label Formats                 |   76 |

<!-- image -->

<!-- image -->

## Printer Configuration Commands

In most cases, the printer can be configured either from the front panel or through various ZPL II commands (Table 16). When the printer receives a configuration command, the change usually affects the current label format and any future label formats until the configuration command is reissued with a different set of parameters, the printer is reset, or the printer power is turned off. The next label printed will reflect the new command. To save changes made using the ZPL II commands, use the ^JU command (see Configuration Update on page 75).

Printer configuration commands must specify a parameter to be valid. Commands with missing or invalid parameters are ignored. For more information regarding these commands and their particular parameters, see ZPL II Programming Guide Volume One .

Table 16 • Printer Configuration Commands

| Command                      | Function                                                                                                                        |
|------------------------------|---------------------------------------------------------------------------------------------------------------------------------|
| ^MM (Print Mode)             | Sets the printer to one of its four basic printing modes; Tear-Off, Rewind, Peel-Off, and Cutter.                               |
| ^MN (Media Tracking)         | Sets the printer for either Non-Continuous or Continuous media.                                                                 |
| ^MT (Media Type)             | Sets the printer for either Direct Thermal media or Thermal Transfer media.                                                     |
| ^MD (Media Darkness)         | Adjusts the print darkness by increasing or decreasing the burn temperature of the printhead.                                   |
| ^LT (Label Top)              | Shifts printing up to 64 dot rows (or ±120 dot rows based on printer platform) up or down from the current Label Home position. |
| ^SS (Set Media Sensors)      | Allows the user to override all of the internal values established after running a media profile.                               |
| ^MP (Disable ModeProtection) | Disables the front panel Darkness, Position, and Calibrate modes.                                                               |
| ^JZ (Reprint After Error)    | Reprints a label if it was partially or incorrectly printed due to an error condition.                                          |
| ^JU (Configuration Update)   | Allows the user to save the current settings.                                                                                   |
| ^SZ (Set ZPL)                | Allows the user to select either the ZPL or ZPL II Programming Language.                                                        |

To determine how your printer is currently configured, print a printer configuration label (see Figure 8 on page 48 for a sample). Consult your printer's User Guide for instructions. The label provides valuable information about your printer's configuration, memory, and options.

## Print Mode

The ^MM (Print Mode) command determines the action the printer takes after a label or group of labels has been printed. These are the different modes of operation.

Tear Off - After printing, the label is advanced so that the web is over the tear bar. Label, with backing attached, can then be torn off manually.

Rewind - Label and backing are rewound on an (optional) internal rewind device. The next label is positioned under the printhead (no backfeed motion).

Peel Off - After printing, the label is partially separated from the backing. Printing stops until the label is completely removed. Backing is rewound using an internal backing only rewind spindle. (NOTE: Select only if printer is equipped with internal rewind spindle.)

Cutter - The web separating the printed label and the next blank label to be printed is extended into the cutter mechanism. The label is cut. The blank label is then pulled back into the printer so it can be printed.

## Media Tracking

The ^MN (Media Tracking) command tells the printer what type of media is being used (continuous or non-continuous) for purposes of tracking. These are the choices for this command:

Continuous Media - This media has no physical characteristic (web, notch, perforation, etc.) to separate labels. Label Length is determined by the ^LL command.

Non-Continuous Media - This media has some type of physical characteristic (web, notch, perforation, etc.) that can be detected by the printer to separate the labels.

## Media Type

The ^MT (Media Type) command selects the type of media being used in the printer. There are the choices for this command:

Thermal Transfer Media - This media uses a high-carbon black or colored ribbon. The ink on the ribbon is bonded to the media.

Direct Thermal Media - The media is heat sensitive and requires no ribbon.

<!-- image -->

## Media Darkness

The ^MD (Media Darkness) command adjusts the darkness relative to the current darkness setting. The minimum value is -30 and the maximum value is 30.

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

Example · These are some example for using the ^MD Instruction:

- If the current value (value on configuration label) is 16, entering the command ^MD -9 would decrease the value to 7.
- If the current value (value on configuration label) is 1, entering the command ^MD 15 would increase the value to 16.
- If the current value (value on configuration label) is 25, entering the command ^MD 10 would only increase the value to 30 since that is the maximum value allowed.

Note · Each ^MD command is treated separately with respect to the current value (value on configuration label).

Example · This is an example of what would happen if two ^MD

- commands were received:
- Assume the current value is 15. An ^MD -6 command is received that changes the current value to 9. Another command, ^MD 2, is received. The current value is changed 17. The two ^MD commands were treated individually with respect to the current value of 15.
- The ~SD command is the ZPL equivalent of the darkness setting parameter on the front panel and can also be used to adjust the print darkness.

Note · The ^MD command value, if used, is added to the ~SD command.

## Label Top Position

The ^LT (Label Top) command moves the entire label format a maximum of 64 dot rows (or 120 dot rows on certain printer platforms) up or down from its current position with respect to the top edge of the label. A negative value moves the format towards the top of the label; a positive number moves the format away from the top of the label.

This command can be used to fine-tune the position of the finished label without having to change any of the existing parameters.

Note · This command does not change the Media Rest position.

<!-- image -->

## Set Media Sensors

The ^SS (Set Media Sensors) command is used to change the sensor values for media, web, ribbon and label length that were set during the 'media calibration' process (consult the 'Media Calibration' process as described in your printer's User Guide).

## Mode Protection

The ^MP (Mode Protection) command is used to disable the various Mode functions on the front panel. Once disabled, the settings for the particular mode function can no longer be changed and the LED associated with the function will not light up.

Since this command has only one parameter, each mode will have to be disabled with an individual ^MP command.

## Reprint After Error

The ^JZ (Reprint After Error) command is used to reprint a partially printed label caused by a Ribbon Out , Media Out , or Head Open error condition. The label will be reprinted as soon as the error condition is corrected.

This command will remain active until another ^JZ command is sent to the printer or the printer is turned off.

The ^JZ command sets the error mode for the printer. If ^JZ is changed, only labels after the change will be affected.

## Configuration Update

The ^JU (Configuration Update) command sets the active configuration for the printer. There are three choices for this command (Table 17).

Table 17 · ^JU Command Parameters

| Parameter                           | Function                                                                                                                            |
|-------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------|
| S = save current settings           | The current configuration is saved. This is the configuration that will be used at Power-On.                                        |
| F = reload factory values (default) | The factory values (default values) are loaded. These values will be lost at Power Off if they are not saved with the ^JUS command. |
| R = recall last saved values        | The last values saved using this ( ^JU ) command or the Mode Sequencing from the front panel are loaded.                            |

## Set ZPL

The ^SZ (Set ZPL) command is used to select the programming language used by the printer. This command gives you the ability to print labels formatted in both ZPL or ZPL II.

This command remains active until another ^SZ command is sent to the printer or the printer is turned off.

## Setting Up Customized Label Formats

You can save a great deal of time by setting up your own configuration formats. If most of your printing is done on one or two types of media, you can easily create label formats specifically for those media.

If you need to print a special label, you change the various commands and then you only need to change the media and load the new, specific configuration format.

Depending on your needs and specific application, the following is a list of the commands you might want to put into a configuration format.

- ^XB Suppress Backfeed
- ^PR Print Rate
- ^LL Label Length
- ^LT Label Top
- ^MM Print Mode
- ^MT Media Type
- ^JZ Reprint After Error
- ^SS Set Media Sensors
- ^MD Media Darkness
- ^MN Media Tracking
- ^JU Configuration Update
- ^SZ Set ZPL

Note · You can have as many of these format configurations as needed. Supply them with different names and send them to the printer as they are called for.

<!-- image -->

<!-- image -->

6

