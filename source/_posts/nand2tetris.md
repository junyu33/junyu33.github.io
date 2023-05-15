layout: post

title: nand2tetris

author: junyu33

categories: 

- develop

tags:

- python

date: 2023-4-17 21:00:00

---

nand2tetris 各 module 的评价以及本人的 workout.

43 hours (approximately) for part1 (module1-6) in December 28, 2022, grade 100%.

89 hours (approximately) for part2 (module7-12) in April 17, 2023, grade 96.8%.

<!-- more -->

# modules 

## module1(boolean logic)

- aim: Build some basic logic chip like AND, OR, MUX, DMUX.
- difficulty: 1
- status: finished
- remark: Just need to get accustomed to HDL language.

## module2(boolean arithmetic)

- aim: Build some more advanced chip like Add, FullAdder and ALU.
- difficulty: 2
- status: finished
- remark: Students who learnt digital circuit can figure it out easily, maybe you need some debugging skills when implementing the ALU.

## module3(sequential logic)

- aim: Build registers and different size of RAMs.
- difficulty: 2
- status: finished
- remark: Building a bit which can store data is kind of challenging, but building the register, RAM and pile them up is just repetition.

## module4(machine language)

- aim: Write hack assembly by hand.
- difficulty: 2
- status: finished
- remark: Commenting what you have done using the high-level language saves time when debugging.

## module5(computer architecture)

- aim: Build the CPU, memory and then the whole computer.
- difficulty: 3
- status: finished
- remark: Building the CPU needs some patience, while others are quite easy. (ps: ALWAYS REMEMBER THE BITS ARE ARRANGED IN SMALL ENDIAN !!!)

## module6(assembler)

- aim: Build the translater between hack assembly and hack machine language(0's and 1's).
- difficulty: 3
- status: finished
- remark: The first project needs serious programming (although you can choose write by hand, but you'll not be able to handle following projects), I implemented using about 100 lines of python code.

## module7(VM1: stack arithmetic)

- aim: Transalte basic VM code like push, pop, add, sub, gt, lt.
- difficulty: 3
- status: finished
- remark: I implemented using about 350 lines of python code, but most of them are repetition of some patterns. 

## module8(VM2: program control)

- aim: Transalte rest of VM code like goto, function, call and return.
- difficulty: 4
- status: finished after deadline (makes no difference on my grade)
- remark: You need some deeper understanding of stack call & return routines or you'll be painful. I implemented using 500+ lines of python code.

## module9(high-level language)

- aim: Invent a program/game using jack language.
- difficulty: It varies, my project difficulty is about 3 and get 80pts.
- status: finished
- remark: Involution is everywhere.

## module10(compiler1: syntax analysis)

- aim: The first step of build a compiler: tokenize the jack program and parse it to become a xml file.
- difficulty: 3
- status: finished
- remark: A little challenge of using recursion, if you follow the syntax in lecture, implementing is rather easy. About 360 lines of python code.

## module11(compiler2: code generation)

- aim: With the assistance of xml file, build the symbol table and get the jack code translated finally.
- difficulty: 5
- status: unfinished
- remark: The project is too difficult for only 2 or 3 days and I can't finish it on time. To meet the deadline, I just output the specific VM code in accordance with the test cases (打表 in Chinese). 

## module12(operating system)

- aim: Build the entire OS by 8 classes (jack files).
- difficulty: 4
- status: finished except String class
- remark: Interesting project, I nearly finished all of the classes and found the OS running very slow. Fortunately, the judger only compares classes that are objective(i.e. has .tst files, like Memory, Math and Array module), so I still got the full mark.

# my repo

https://github.com/junyu33/nand2tetris