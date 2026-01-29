<!-- Source: ZPL II Programming Guide Volume 2 -->
<!-- Section: Chapter 7: Real Time Clock -->
<!-- Generated: 2025-11-02 04:52:35 -->

## Mod 10 and Mod 43 Check Digits

This section provides information about Mod 10 and Mod 43 check digits.

## Contents

| Mod 10 Check Digit   |   96 |
|----------------------|------|
| Mod 43 Check Digit   |   97 |

<!-- image -->

## Mod 10 Check Digit

The calculations for determining the Mod 10 Check Digit character are as follows:

1. Start at the first position and add the value of every other position together.

<!-- formula-not-decoded -->

2. The result of Step 1 is multiplied by 3.

<!-- formula-not-decoded -->

3. Start at the second position and add the value of every other position together.

<!-- formula-not-decoded -->

4. The results of steps 1 and 3 are added together.

<!-- formula-not-decoded -->

5. The check character (12th character) is the smallest number which, when added to the result in step 4, produces a multiple of 10.

85 + X = 90 (next higher multiple of 10)

X = 5 Check Character

This bar code illustrates the above example. The digit on the right (5) is the check digit.

<!-- image -->

## Mod 43 Check Digit

The calculations for determining the Mod 43 check Digit character are as follows:

Each character in the Code 39 character set has a specific value. These are shown in the chart below.

| 0=0   | B=11   | M=22   | X=33     |
|-------|--------|--------|----------|
| 1=1   | C=12   | N=23   | Y=34     |
| 2=2   | D=13   | O=24   | Z=35     |
| 3=3   | E=14   | P=25   | - =36    |
| 4=4   | F=15   | Q=26   | . = 37   |
| 5=5   | G=16   | R=27   | Space=38 |
| 6=6   | H=17   | S=28   | $=39     |
| 7=7   | I=18   | T=29   | /=40     |
| 8=8   | J=19   | U=30   | +=41     |
| 9=9   | K=20   | V=31   | %=42     |
| A=10  | L=21   | W=32   |          |

## Example · Data string 2345ABCDE/

1. Add the sum of all the character values in the data string. Using the chart above, the sum of the character values is as follows:

<!-- formula-not-decoded -->

2. Divide the total by 43. Keep track of the remainder.

115/43 = 2 Remainder is 29

3. The 'check digit' is the character that corresponds to the value of the remainder.

Remainder = 29

29 is the value for the letter T.

T is the check digit.

Below is a bar code that illustrates the example. The character on the right, T, is the check digit.

12345ABCDET

<!-- image -->

AF0125,100AB3N,Y,150,Y,NAFD12345ABCDE/AFS

<!-- image -->

Notes · \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

<!-- image -->

9

