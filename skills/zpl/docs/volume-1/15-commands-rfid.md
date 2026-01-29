<!-- Source: ZPL II Programming Guide Volume 1 -->
<!-- Section: RFID Commands (^R*) -->
<!-- Generated: 2025-11-02 04:52:35 -->

|--------------------------|----------------------------------------------------------------------------------------------------------------|
| a = device to initialize | Acceptable Values: B = Flash card (PCMCIA) E = internal Flash memory Default Value: a device must be specified |

- Example · This is an example of initializing the different types of flash memory:

^JBB initializes the optional Flash card when installed in the printer.

^JBE initializes the optional Flash memory when installed in the printer.

^JBA initializes initial Compact Flash memory when installed in the printer.

<!-- image -->

<!-- image -->

<!-- image -->

~JB

## Reset Optional Memory

Description The ~JB command is used for these conditions:

- The ~JB command must be sent to the printer if the battery supplying power to the battery powered memory card fails and is replaced. A bad battery shows a battery dead condition on the Printer Configuration Label.
- The ~JB command can also be used to intentionally clear (reinitialize) the B: memory card. The card must not be write protected.

Format ~JB

Comments If the battery is replaced and this command is not sent to the printer, the memory card cannot function.

<!-- image -->

## ~JC

## Set Media Sensor Calibration

Description The ~JC command is used to force a label length measurement and adjust the media and ribbon sensor values.

Format ~JC

Comments In Continuous Mode, only the media and ribbon sensors are calibrated.

<!-- image -->

<!-- image -->

<!-- image -->

~JD

## Enable Communications Diagnostics

Description The ~JD command initiates Diagnostic Mode, which produces an ASCII printout (using current label length and full width of printer) of all characters received by the printer. This printout includes the ASCII characters, the hexadecimal value, and any communication errors.

Format ~JD

<!-- image -->

~JE

## Disable Diagnostics

Description The ~JE command cancels Diagnostic Mode and returns the printer to normal label printing.

Format ~JE

<!-- image -->

<!-- image -->

~JF

## Set Battery Condition

Description There are two low battery voltage levels sensed by the PA / PT400 ™ printers. When battery voltage goes below the first level, the green LED begins flashing as a warning but printing continues. When this warning occurs, it is recommended to recharge the battery.

As printing continues, a second low voltage level is reached. At this point, both green and orange LEDs flash as a warning, and printing automatically pauses.

When pause on low voltage is active ( ~JFY ) and the battery voltage level falls below the second low voltage level, printing pauses and an error condition is displayed as an indication that the printer should be plugged into the battery charger. By pressing FEED , printing continues on a label-by-label basis, but there is a high risk of losing label format information due to the continued decrease of battery voltage.

When pause on low voltage is not active ( ~JFN ), and the battery voltage level falls below the second low voltage level, printing continues and the orange LED remains off. If the battery voltage continues to decrease, label information could be lost and cause the printer to stop operating. This option should be selected only when the printer is connected to the Car Battery Adapter. From time to time the printer might sense that battery voltage is below the first low voltage level, but due to the continuous recharging of the car battery, further loss of battery voltage is not a concern and printing continues.

If this option is not selected when using the Car Battery Adapter, you might need to press FEED to take the printer out of Pause Mode and print each label.

Format ~JFp

This table identifies the parameters for this format:

| Parameters               | Details                                                                                                                                               |
|--------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------|
| p = pause on low voltage | Accepted Values: Y (pause on low voltage) or N (do not pause) N is suggested when the printer is powered by the Car Battery Adapter. Default Value: Y |

<!-- image -->

~JG

## Graphing Sensor Calibration

Description The ~JG command is used to force a label length measurement, recalibrate the media and ribbon sensors, and print a graph (media sensor profile) of the sensor values.

Format ~JG

Example · Sending the ~JG this image:

- command to the printer produces a series of labels resembling

<!-- image -->

<!-- image -->

<!-- image -->

## ^JJ

## Set Auxiliary Port

Description The ^JJ command allows you to control an online verifier or applicator device.

Format ^JJa,b,c,d,e,f

This table identifies the parameters for this format:

| Parameters                              | Details                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
|-----------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| a = Operational Mode for auxiliary port | Accepted Values: 0 = off 1 = reprint on error-the printer stops on a label with a verification error. When PAUSE is pressed, the label reprints (if ^JZ is set to reprint). If a bar code is near the upper edge of a label, the label feeds out far enough for the bar code to be verified and then backfeeds to allow the next label to be printed and verified. 2 = maximum throughput-the printer stops when a verification error is detected. The printer starts printing the next label while the verifier is still checking the previous label. This mode provides maximum throughput, but does not allow the printer to stop immediately on a label with a verification error. Default Value: 0 |
| b = Application Mode                    | Accepted Values: 0 = off 1 = End Print signal normally high, and low only when the printer is moving the label forward. 2 = End Print signal normally low, and high only when the printer is moving the label forward. 3 = End Print signal normally high, and low for 20 ms when a label has been printed and positioned. 4 = End Print signal normally low, and high for 20 ms when a label has been printed and positioned. Default Value: 0                                                                                                                                                                                                                                                         |
| c = Application Mode start signal print | Accepted Values: p = Pulse Mode - Start Print signal must be de-asserted before it can be asserted for the next label. l = Level Mode - Start Print signal does not need to be de- asserted to print the next label. As long as the Start Print signal is low and a label is formatted, a label prints. Default Value: 0                                                                                                                                                                                                                                                                                                                                                                                |

| Parameters                       | Details                                                                                                                                                                                                                                                                                                                       |
|----------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| d = Application Label Error Mode | Accepted Values: e = error mode-the printer asserts the Service Required signal (svce_req - pin 10) on the application port, enters into Pause Mode, and displays an error message on the LCD. f = Feed Mode-a blank label prints when the web is not found where expected to sync the printer to the media. Default Value: f |
| e = Reprint Mode                 | Accepted Values: e = enabled-printer ignores the Reprint signal. d = disabled-the last label reprints after the signal is asserted. If a label is canceled, the label to be reprinted is also canceled. This mode consumes more memory because the last printed label is not released until it reprints. Default Value: d     |
| f = Ribbon Low Mode              | Accepted Values: e = enabled - printer warning issued when ribbon low. d = disabled - printer warning not issued when ribbon low. Default Value: e                                                                                                                                                                            |

<!-- image -->

<!-- image -->

~JL

## Set Label Length

Description The ~JL command is used to set the label length. Depending on the size of the label, the printer feeds one or more blank labels.

Format ~JL

<!-- image -->

## ^JM

## Set Dots per Millimeter

Description The ^JM command lowers the density of the print-24 dots/mm becomes 12, 12 dots/mm becomes 6, 8 dots/mm becomes 4, and 6 dots/mm becomes 3. ^JM also affects the field origin ( ^FO ) placement on the label (see example below).

When sent to the printer, the ^JM command doubles the format size of the label. Depending on the printhead, normal dot-per-millimeter capabilities for a Zebra printer are 12 dots/mm (304 dots/inch), 8 dots/mm (203 dots/inch) or 6 dots/mm (153 dots/inch).

This command must be entered before the first ^FS command in a format. The effects of ^JM are persistent.

## Format ^JMn

This table identifies the parameters for this format:

| Parameters                  | Details                                                                                                                                |
|-----------------------------|----------------------------------------------------------------------------------------------------------------------------------------|
| n = set dots per millimeter | Accepted Values: A = 24 dots/mm, 12 dots/mm, 8 dots/mm or 6 dots/mm B = 12 dots/mm, 6 dots/mm, 4 dots/mm or 3 dots/mm Default Value: A |

Example · This example of the affects of alternating the dots per millimeter:

<!-- image -->

<!-- image -->

Comments If ^JMB is used, the UPS Maxicode bar code becomes out of specification.

<!-- image -->

<!-- image -->

<!-- image -->

~JN

## Head Test Fatal

Description The ~JN command turns on the head test option. When activated, ~JN causes the printer to halt when a head test failure is encountered.

Once an error is encountered the printer remains in error mode until the head test is turned off ( ~JO ) or power is cycled.

Format ~JN

Comments If the communications buffer is full, the printer is not able to receive data. In this condition, the ~JO command is not received by the printer.

<!-- image -->

~JO

## Head Test Non fatal

Description The ~JO command turns off the head test option. ~JO is the default printhead test condition and overrides a failure of printhead element status check. This state is changed when the printer receives a ~JN (Head Test Fatal) command. The printhead test does not produce an error when ~JO is active.

Format ~JO

<!-- image -->

<!-- image -->

<!-- image -->

~JP

## Pause and Cancel Format

Description The ~JP command clears the format currently being processed and places the printer into Pause Mode.

The command clears the next format that would print, or the oldest format from the buffer. Each subsequent ~JP command clears the next buffered format until the buffer is empty. The DATA indicator turns off when the buffer is empty and no data is being transmitted.

Issuing the ~JP command is identical to using CANCEL on the printer, but the printer does not have to be in Pause Mode first.

Format ~JP

<!-- image -->

~JR

## Power On Reset

Description The ~JR command resets all of the printer's internal software, performs a power-on self-test (POST), clears the buffer and DRAM, and resets communication parameters and default values. Issuing a ~JR command performs the same function as a manual power-on reset.

Format ~JR

<!-- image -->

<!-- image -->

## ^JS

## Sensor Select

Format ~JSb

This table identifies the parameters for this format:

| Parameters                                 | Details                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
|--------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| b = backfeed order in relation to printing | Accepted Values: A = 100 percent backfeed after printing and cutting B = 0 percent backfeed after printing and cutting, and 100 percent before printing the next label N = normal -90 percent backfeed after label is printed O = off -turn backfeed off completely 10 to 90 = percentage value The value entered must be a multiple of 10. Values not divisible by 10 are rounded to the nearest acceptable value. For example, ~JS55 is accepted as 50 percent backfeed. Default Value: N |

Comments When using a specific value, the difference between the value entered and 100 percent is calculated before the next label is printed. For example, a value of 40 means 40 percent of the backfeed takes place after the label is cut or removed. The remaining 60 percent takes place before the next label is printed.

The value for this command is also reflected in the Backfeed parameter on the printer configuration label.

For ~JSN - the Backfeed parameter is listed as DEFAULT

For ~JSA - or 100 the Backfeed parameter is listed as AFTER
