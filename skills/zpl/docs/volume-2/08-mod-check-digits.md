<!-- Source: ZPL II Programming Guide Volume 2 -->
<!-- Section: Chapter 8: Mod 10 and Mod 43 Check Digits -->
<!-- Generated: 2025-11-02 04:52:35 -->

## Error Detection Protocol

<!-- image -->

This section explains the Zebra protocol that has been supplanted in TCP/IP based applications because of the error detection compatibility inherent in the TCP/IP protocol.

## Contents

| Introduction . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .   |   100 |
|------------------------------------------------------------------------------------|-------|
| What is a Protocol? . . . . . . . . . . . . . . . . . . . . . . . . . .            |   100 |
| How Protocols Work . . . . . . . . . . . . . . . . . . . . . . . . .               |   100 |
| Request Packet Formats from the Host Computer . . . .                              |   101 |
| Header Block Fields. . . . . . . . . . . . . . . . . . . . . . . . . .             |   101 |
| Data Block Fields . . . . . . . . . . . . . . . . . . . . . . . . . . . .          |   102 |
| Response From the Zebra Printer . . . . . . . . . . . . . . . . .                  |   103 |
| Zebra Packet Response . . . . . . . . . . . . . . . . . . . . . .                  |   103 |
| Header Block Fields. . . . . . . . . . . . . . . . . . . . . . . . . .             |   103 |
| Data Block Fields . . . . . . . . . . . . . . . . . . . . . . . . . . . .          |   104 |
| Disguising Control Code Characters . . . . . . . . . . . . .                       |   105 |
| Error Detection Protocol Application . . . . . . . . . . . . .                     |   106 |
| Error Conditions and System Faults . . . . . . . . . . . . .                       |   106 |
| How the Zebra Printer Processes a Request Packet.                                  |   107 |
| How the Zebra Printer Responds to Host Status . . . .                              |   108 |

<!-- image -->

## Introduction

There are many instances when it is vitally important that the information sent to the Zebra printer is received completely Error-Free. ZPL II supports an error detection protocol called Zebra Packet Response Protocol to meet this need.

<!-- image -->

Note · This protocol only works when using serial interface. It does not function when using parallel interface.

## What is a Protocol?

A protocol is a precisely defined set of rules. In the case of data communications, a Protocol defines how data is transmitted, received, and acknowledged between two devices.

The sole purpose of the Packet Response Protocol is to ensure that the information sent from a Host computer to the Zebra printer is received accurately. Remember, the protocol cannot insure the accuracy of the data that is actually sent from the Host computer. The commands and data needed to make a label (ZPL II Format) are encapsulated within the information sent from the Host computer.

## How Protocols Work

The basic unit of data transfer in the Packet Response Protocol is called a 'Transaction.' A Transaction is a two-way communication procedure that consists of information being sent from the Host computer to the Zebra printer, and the printer sending back a response to the Host computer. This response is an indication that the Zebra printer has either accepted or rejected the information sent from the Host computer.

Information is sent in the form of 'Packets.' Packets sent from the Host computer are called Request Packets.

When a Request Packet is received, the Zebra printer analyzes the information in the Packet. If the Request Packet is accepted, the Zebra printer will send a positive response back to the Host computer. The Host computer can then send the next Request Packet. If the information is rejected, the Zebra printer will send a negative response back to the Host computer. The Host computer then sends the same Request Packet again.

The Zebra Packet Response Protocol can be used in both single-printer applications, where there is only one Zebra printer connected to the Host computer, and multi-drop systems in which several Zebra printers are connected to the same Host computer.

## Request Packet Formats from the Host Computer

The first part of each data transfer Transaction is the sending of a Request Packet by the Host computer. The Request Packet contains a fixed length 'Header' block and a variable length 'Data' block. Each Packet sent from the Host computer to the Zebra printer must always use the following format.

The Request Packet Header Block is comprised of five fixed-length fields. The Request Packet Data Block is comprised of four fixed-length fields and one variable-length field. These fields are defined as follows.

| Header Block   | Header Block   | Header Block   | Header Block   | Header Block   | Data Block   | Data Block   | Data Block   | Data Block   | Data Block   |
|----------------|----------------|----------------|----------------|----------------|--------------|--------------|--------------|--------------|--------------|
| SOH            | DST. Z-ID      | SRC. Z-ID      | TYPE           | SEQ. #         | STX          | FORMAT       | EXT          | CRC          | EOT          |
| 1              | 3              | 3              | 1              | 1              | 1            | ≤ 1024       | 1            | 2            | 1            |

## Header Block Fields

- SOH (start of header character)

The Zebra printer interprets this character as the beginning of a new Request Packet. The ASCII Control Code character SOH (01H) is used as the Start of Header Character.

- DST. Z-ID (destination Zebra-ID)

This is the three-digit ASCII I.D. number used to identify which Zebra printer is to receive the Request Packet. The Zebra printer compares this number to the Network ID number assigned to it during Printer Configuration. The Zebra printer will act on the Request Packet only if these numbers match.

- SRC. Z-ID (source Zebra-ID)

This is a three-digit ASCII number used to identify the Host computer. This number is determined by the user.

- TYPE (packet type)

This field is used to define the type of Request Packet being sent by the Host. Only two characters are valid in this field:

- 'P' indicates a Print Request Packet
- 'I' indicates an Initialize Request Packet

Most of the Packets sent by the Host to the Zebra printer will be of the 'P' variety, requesting a label to be printed.

The 'I' character tells the Zebra printer to initialize the packet sequence numbering. It is required in the first packet of a new printing session, after starting up the Host computer or the Zebra printer.

- SEQ. # (the sequence number of the request packet)

This block contains a single digit number used to denote the current Transaction Number. The Host computer must increment this number by '1" for each new Request/Response Transaction pair, i.e. 0, 1, 2,..., 9. The numbers repeat after every 10 Transactions.

## Data Block Fields

## · STX (Start of Text)

