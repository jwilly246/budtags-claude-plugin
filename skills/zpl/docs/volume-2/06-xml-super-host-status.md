<!-- Source: ZPL II Programming Guide Volume 2 -->
<!-- Section: Chapter 6: XML-Super Host Status -->
<!-- Generated: 2025-11-02 04:52:35 -->

## Real Time Clock

<!-- image -->

This section discusses the ZPL II commands related to the Real-Time Clock (RTC).

The RTC hardware option is currently available for several Zebra printers. The ZPL II commands for the RTC are only applicable if the option is installed in the printer. For those printers with an LCD front panel display, additional front panel configuration parameters are also included.

The Field Clock ( ^FC) command is used to specify the clock-indicator character for the primary, secondary, and tertiary clocks. This command must be included within each label field command string whenever the date or time clock values are required within the field. No date or time clock information can be printed in a label field unless this command is included.

A clock-indicator can be any printable character except the ZPL II Format Prefix, Control Prefix, or Delimiter characters. The default value for the primary clock- indicator is the percent sign (%). The secondary and tertiary clock-indicators have no defaults and must be specified in order for that clock to be used.

The ZPL II Field Data ( ^FD ) command has been expanded to recognize the clock-indicators and associated command characters, and to replace them during the printing process with the corresponding time or date parameter. For example, if the primary clock-indicator is the percent sign (%), then during printing, the character sequence %H in the ^FD statement would be replaced by the 2-digit current hour.

Note · If the Real Time Clock hardware is not installed, or the ^FC command has not preceded the ^FD statement, no replacement would occur. In this case, the characters '%H' would print as text on the label.

The name of the day of the week, the name of the month, and the AM or PM designation can also be inserted in place of a specific clock-indicator/command character sequence.

Table 22 shows the data and time command characters.

<!-- image -->

Table 22 • Data and Time Command Characters

| Command Character   | Replaced with                                       |
|---------------------|-----------------------------------------------------|
| %a                  | abbreviated weekday name                            |
| %A                  | weekday name                                        |
| %b                  | abbreviated month name                              |
| %B                  | month name                                          |
| %d                  | day of the month: 01 to 31                          |
| %H                  | hour of the day (military time): 00 to 23           |
| %I                  | hour of the day (civilian time): 01 to 12           |
| %j                  | day number: 001 to 366                              |
| %m                  | month number: 01 to 12                              |
| %M                  | minute number: 00 to 59                             |
| %p                  | AMor PM designation                                 |
| %S                  | second number: 00 to 59                             |
| %U                  | week number: 00 to 53, with Sunday as the first day |
| %W                  | week number: 00 to 53, with Monday as the first day |
| %w                  | day number: 00 (Sunday) to 06 (Saturday)            |
| %y                  | abbreviated 2-digit year number: 00 to 99           |
| %Y                  | full 4-digit year number                            |

The Set Offset ( ^SO ) command permits the printing of specific times and dates relative to the primary clock. The secondary (or tertiary) clock is enabled when secondary (or tertiary) offsets are entered using this command. The secondary (or tertiary) clock time and date are determined by adding the offsets to the current clock reading.

One ^SO command is required to set the secondary offset and an additional ^SO command is required for a tertiary offset. The offsets remain until changed or until the printer is either powered down or reset.

Note · Only dates from January 1, 1998 to December 31, 2097 are supported. Setting the offsets to values that result in dates outside this range is not encouraged or guaranteed.

The Set Mode/Language ( ^SL ) command is used to select the language in which to print the names of the days of the week, the names of the months. This command also sets the printing mode, which can be 'S' for START TIME or 'T' for TIME NOW. In START TIME mode, the time printed on the label is the time that is read from the Real Time Clock when the label formatting begins (when the ^XA command is received by the printer). In TIME NOW mode, the time printed on the label is the time that is read from the Real Time Clock when the label is placed in the queue to be printed.

<!-- image -->

8

