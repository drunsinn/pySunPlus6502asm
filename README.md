# pySunPlus6502asm
 as of now non functional 6502 assembler specificaly for the mcu created by Sun Plus

--- WIP ---


Steps to assemble a program:
1. read file and split into seperate lines
2. parse each line with pyparsing for correct syntax
3. convert each line to instruction object
4. if a include statement is encountered, imediatly read its content and append in place
5. if line contains lable definition and assembler instruction add two seperate instruction objects
6. check lable definitions in instruction list for dublicates

7. check assembler instructions for missing label
8. determin memmory address of each label
9. replace label in assembler instructions with memmory address
10. convert programm to string ob hex values
11. output hex string to file
