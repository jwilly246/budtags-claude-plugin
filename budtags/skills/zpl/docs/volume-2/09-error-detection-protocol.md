<!-- Source: ZPL II Programming Guide Volume 2 -->
<!-- Section: Chapter 9: Error Detection Protocol -->
<!-- Generated: 2025-11-02 04:52:35 -->

The Zebra printer interprets this character as the beginning of the variable-length Data Format portion of the Request Packet. The ASCII Control Code character STX (02H) is used as the Start of Text Character.

## · DATA FORMAT (Label Information)

A variable-length portion of the Request Packet that contains the complete or partial ZPL II label format, or partial data string (such as a downloaded graphic).

This field can contain from 0 to 1024 characters. If the Format of a label is longer than 1024 characters, the Data Format fields from consecutive packets will be concatenated together in the printer's Receive Data Buffer as if they were sent as one long direct transmission.

Special consideration has been given to the possible requirement to include ASCII Control Characters (values less than 20H) in the Data Format portion of a Request Packet. Characters such as EOT (04H), STX (02H), SOH (01H), and ETX (03H), are part of the Error Detection Protocol and could interrupt normal communication procedures if received at the wrong time.

## · ETX (End of Text)

The Zebra printer interprets this character as the end of the variable length Data Format portion of the Request Packet. The ASCII Control Code character ETX (03H) is used as the End of Text Character.

## · CRC (Cyclic Redundancy Check)

The CRC is a 2 character field. A Cyclic Redundancy Check is a type of error checking used to maintain the validity and integrity of the information transmitted between the Host computer and the Zebra printer. This Protocol uses the 16-bit CCITT method of producing a CRC.

The CRC is a two-byte value derived from the contents of the packet between, but not including, the SOH character and the CRC code itself. The Zebra printer will calculate a CRC of the Request Packet received and compare the value with the CRC Value in this field. The CRC of the Request Packet must match the CRC calculated by the Zebra printer in order for the Request Packet to be valid.

## · EOT (End of Transmission)

The Zebra printer interprets this character as the end of the Request Packet. The ASCII Control Code character EOT (04H) is used as the End of Transmission Character.

## Response From the Zebra Printer

When the Zebra printer receives the EOT character, it will begin acting on the Request Packet received. The printer will compare certain characters and numeric values within the received Request Packet and send a response back to the Host computer.

## Zebra Packet Response

The Packet Response protocol provides the highest degree of error checking and is well suited to the Host-Multiple Printer application. The Response Packet from the Zebra printer will always use the following format.

The Request Packet Header Block is comprised of five fixed-length fields. The Request Packet Data Block is comprised of four fixed-length fields and one variable-length field. These fields are defined as follows.

| Header Block   | Header Block   | Header Block   | Header Block   | Header Block   | Data Block   | Data Block   | Data Block   | Data Block   | Data Block   |
|----------------|----------------|----------------|----------------|----------------|--------------|--------------|--------------|--------------|--------------|
| SOH            | DST. Z-ID      | SRC. Z-ID      | TYPE           | SEQ. #         | STX          | FORMAT       | EXT          | CRC          | EOT          |
| 1              | 3              | 3              | 1              | 1              | 1            | ≤ 1024       | 1            | 2            | 1            |

## Header Block Fields

- SOH (Start of Header Character)

The Zebra printer sends this character as the beginning of a new Response Packet. The ASCII Control Code character SOH (01H) is used as the Start of Header Character.

- DST. Z-ID (Destination Zebra-ID)

This is the same three-digit ASCII number used to identify the Host Computer that was contained in the SRC. Z-ID field of the Request Packet that initiated this Response Packet. The Host compares this number to its known value to insure it is the proper destination.

- SRC. Z-ID (Source Zebra-ID)

This is the three character ASCII Network I.D. of the Zebra printer that is sending the Response Packet.

- TYPE (Packet Type)

This block is used to define the type of Response Packet being sent to the Host. Only three characters are valid in this field.

- 'A' This is a Positive Acknowledgment to the Host computer. It indicates that the Request Packet was received without a CRC error. The Host computer may send the next Request Packet.
- 'N' This is the Negative Acknowledgment to the Host computer. It indicates that an error was detected in the packet sent from the Host computer. The Host computer must retransmit the same Request Packet again.
- 'S' This character indicates that the Response Packet contains the Zebra Printer Status requested by a ~HS (Host Status) command received from the Host.

<!-- image -->

- SEQ. # (Used to denote the current message sequence number)

This number is identical to the message sequence number in the Request Packet. It denotes the message sequence number to which the Response Packet is replying.

## Data Block Fields

- STX (Start of Text)

The Zebra printer sends this character as the beginning of the variable length Data Format portion of the Response Packet. The ASCII Control Code character STX (02H) is used as the Start of Text Character.

- DATA FORMAT (Label Information)

The 'variable length' portion of the Response Packet. If the Packet Type field in the Response Header contains an 'A' or an 'N', no data will appear in this field. If the Packet Type field contains an 'S', this field will contain the Printer Status Message.

- ETX (End of Text)

The Zebra printer sends this character as the end of the variable length Data Format portion of the Request Packet. The ASCII Control Code character ETX (03H) is used as the End of Text Character.

- CRC (Cyclic Redundancy Check)

This is the CRC of the Response Packet as calculated by the Zebra printer. This Cyclic Redundancy Check maintains the validity and integrity of the information transmitted between the Zebra printer and the Host computer.

This CRC is a two Byte value derived from the contents of the packet between, but not including, the SOH character and the CRC code itself. The Host computer will calculate a CRC of the received Response Packet and compare it to the CRC value in this field. The CRC of the Response Packet must match the CRC calculated by the Host computer in order for the Response Packet to be valid.

- EOT (End of Transmission)

The Zebra printer sends this character as the end of the Response Packet. The ASCII Control Code character EOT (04H) is used as the End of Transmission Character.

## Disguising Control Code Characters

There may be occasions when ASCII Control Codes (00H - 19H) must be included as part of the Data Format block of a Request Packet. To eliminate any problems, these characters must be disguised so that the communication protocol does not act on them.

## This procedure must be used to disguise each Control Code.

- A SUB (1AH) character must precede each Control Code placed in the Data Format block.
- The value of 40H must be added to the Hex value of the Control Code.
- The ASCII Character corresponding to the total value produced in step 2 must be entered in the Data Format right after the SUB character.

The Zebra printer automatically converts the modified control character back to its correct value by discarding the SUB (1AH) character and subtracting 40H from the next character.

Example •

- To include a DLE (10H) character in the Data Format block:
1. Enter a SUB (1AH) character into the Data Format.
2. Add 40H to the DLE value of 10H for a resulting value of 50H.
3. Enter the ASCII character 'P' (50H) in the Data Format after the SUB character.

Note · This technique is counted as two characters of the 1024 allowed in the Data Format block.

<!-- image -->

<!-- image -->

## Rules for Transactions

- Every Transaction is independent of every other Transaction and can only be initiated by the Host computer.
- A valid Response Packet must be received by the Host computer to complete a Transaction before the next Request Packet is sent.
- If an error is encountered during a Transaction, the entire Transaction (i.e., Request Packet and Response Packet) must be repeated.
- The Zebra printer does not provide for system time-outs and has no responsibility for insuring that its Response Packets are received by the Host computer.
- The Host computer must provide time-outs for all of the Transactions and insure that communication continues.
- If any part of a Transaction is lost or received incorrectly, it is the responsibility of the Host computer to retry the whole Transaction.

<!-- image -->

## Error Detection Protocol Application

The following are the basic requirements for setting up the Zebra printer to use the Error Detection Protocol.

Activating the Protocol Protocol is a front panel selection, or can be done with the ZPL command ^SC .

Setting Up Communications Insure that the Host computer and the Zebra printer are characterized with the same communication parameters; i.e., Parity, Baud Rate, etc. The communications must be set up for 8 data bits.

Setting the Printer ID Number The Protocol uses the printer's Network ID number to insure communication with the proper unit. The Network ID is programmed into the printer by sending the printer a ^NI (Network ID Number) command or done through the front panel.

If there is only one printer connected to the Host computer, the Network ID number should be set to all zeros (default).

If there is more than one printer, such as in a broadcast or multi-drop environment, each printer should be assigned its own unique ID number. Printers in this environment, with an ID of all zeros, will receive ALL label formats regardless of the actual printer ID number in the DST. ZID block of the Request Packet.

## Error Conditions and System Faults

Restarting a Transmission If a break in communication occurs, the Host must restart the transmission of the current label format with an Initialization Request Packet. The Zebra printer will not respond to Request Packets sent out of sequence. However, the Zebra printer will respond to an Initialization Request Packet and restart its internal counting with the sequence number of the Request Packet.

CRC Error Conditions and Responses A CRC error condition can be detected when the printer receives a Request Packet or when the Host computer receives a Response Packet. The following list defines these errors and how the Host computer should respond to them.

| Error                                                                                                   | Response                                                                                                                                                    |
|---------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------|
| The CRC calculated by the Zebra printer does not match the one received as part of the Request Packet.  | The Zebra printer will return a Negative Acknowledgment Response Packet. The Host computer should retry the same Transaction with the same Sequence Number. |
| The CRC calculated by the Host computer does not match the one received as part of the Response Packet. | The Host computer should retry the same Transaction with the same Sequence Number.                                                                          |

## Time-Out Error Conditions and Responses

There are certain conditions at the Zebra printer that might cause the Host computer to timeout while processing a Transaction. The following list illustrates these conditions and how the Host computer should respond to them.

| Error                                                                                | Response                                                                                                          |
|--------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------|
| A Request Packet from the Host computer is not received by the Zebra printer.        | The Host computer times out and resends the Request Packet of the same Transaction with the same Sequence Number. |
| A Request Packet from the Host computer is partially received by the Zebra printer.  | The Host computer times out and resends the Request Packet of the same Transaction with the same Sequence Number. |
| A Response Packet from the Zebra printer is not received by the Host computer.       | The Host computer times out and resends the Request Packet of the same Transaction with the same Sequence Number. |
| A Response Packet from the Zebra printer is partially received by the Host computer. | The Host computer times out and resends the Request Packet of the same Transaction with the same Sequence Number. |

## How the Zebra Printer Processes a Request Packet

The following describes the steps taken at the Zebra printer to process a Request Packet.

1. The Zebra printer looks for a SOH (Start of Header) character. As soon as it finds one, it places the SOH and all the data after it into its Receive Data Buffer. This process continues until the printer receives an EOT (End of Transmission) character.
2. Note · If a second SOH is received before an EOT is detected, the contents of the Receive Buffer will be discarded. All of the data after the second SOH will be placed in the Receive Data Buffer.
2. After detecting the EOT, the printer checks for the following:
* The DST. Z-ID matches the printer's Network I.D.

Note · If the Network ID at the printer is all zeros, the printer will accept all Request Packets regardless of the DST. Z-ID received. If a Request Packet is received with the DST. Z-ID all zeros, it is accepted by all printers regardless of their Network ID setting.

- *The Data Format begins with STX and ends with ETX.
- *The Sequence Number has not been used before.

If the check is satisfactory, proceed to Step 3 on the following page.

If any part of the check is unsatisfactory, the printer discards the data in its Receive Data Buffer and waits for another SOH. No response is sent to the computer.

<!-- image -->

<!-- image -->

<!-- image -->

## Exceptions

It is possible that the printer will send a response to the host that the host does not receive. Therefore, the host will send the same request packet to the printer again. If this happens, the printer will not use the data if it already used it before. However, the printer will send a response back to the host.

The printer calculates the CRC and compares it with the one received in the Request Packet. If the CRC is valid, the printer sends a Positive Response Packet to the Host computer. It then transfers the 'Variable Length' data from the Receive Buffer to its memory for processing. If the CRC does not match, and the printer is set up to return a Negative Response Packet, the following will take place:

1. The printer assumes that the DST. Z-ID, SRC. Z-ID, and Sequence Number are correct and that the error was in the variable data.
2. The same DST. Z-ID, printers SRC. Z-ID, and Sequence Number will be returned back to the host in the Negative Response Packet.
3. If the assumption in (a) is incorrect, the Host computer can time-out and retransmit the original Request Packet.

## How the Zebra Printer Responds to Host Status

If a ~HS (Host Status) command is received by the Zebra printer, the printer will send back an acknowledgment for the receipt of the packet. It then sends an additional packet that includes the Host Status information in the Variable Length portion of the packet.

<!-- image -->

10

