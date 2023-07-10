// This file is part of nand2tetris, as taught in The Hebrew University, and
// was written by Aviv Yaish. It is an extension to the specifications given
// [here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
// as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
// Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).

// The program should swap between the max. and min. elements of an array.
// Assumptions:
// - The array's start address is stored in R14, and R15 contains its length
// - Each array value x is between -16384 < x < 16384
// - The address in R14 is at least >= 2048
// - R14 + R15 <= 16383
//
// Requirements:
// - Changing R14, R15 is not allowed.

// Put your code here.
// goto end if length smaller than 1:
@R15
D=M-1
@END
D;JLE

// set min max:
@0
D=A
@max
M=D
@16383
D=A
@min
M=D
@max
M=M-D

@min_i
M=0
@max_i
M=0
@i
M=0
(LOOP)
// if finished to check the array goto swap:
@i
D=M
@R15
D=D-M
@SWAP
D;JEQ
// set min:
@R14
D=M
@i
A=D+M
D=M  // D=RAM[R14+i]
@min
D=D-M  // D=RAM[R14+i] - min
@UNSET_MIN
D;JGE
@min
M=D+M // M=RAM[R14+i] - min + M = RAM[R14+i] - min + min =RAM[R14+i]
@i
D=M
@min_i
M=D
//@UNSET_MAX
0;JMP  // if sets to min, no need to set to max
(UNSET_MIN)

// set max:
@R14
D=M
@i
A=D+M
D=M  // D=RAM[R14+i]
@max
D=D-M  // D=RAM[R14+i] - max
@UNSET_MAX
D;JLE
@max
M=D+M // M=RAM[R14+i] - max + M = RAM[R14+i] - max + max =RAM[R14+i]
@i
D=M
@max_i
M=D
(UNSET_MAX)
// i++
@i
M=M+1
@LOOP
0;JMP

(SWAP)
@R14
D=M
@min_i
M=M+D
@max_i
M=M+D

@max
D=M
@min_i
A=M
M=D
@min
D=M
@max_i
A=M
M=D


(END)
@END
0;JMP