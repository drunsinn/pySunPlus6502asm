#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: drunsinn
@license: MIT License
"""
import logging

class Label(object):
    def __init__(self, label_name):
        self.__value = label_name
    def __str__(self):
        return ';' + self.__value
    @staticmethod
    def from_parsing(token):
        #print(token.dump())
        return Label(token['label'])

class Comment(object):
    def __init__(self, comment_text):
        self.__value = comment_text
    def __str__(self):
        return ';' + self.__value
    @staticmethod
    def from_parsing(token):
        #print(token.dump())
        return Comment(token['comment'])



class AddressValue(object):
    TYPE_ACCUMULATOR = 0
    TYPE_ABSOLUTE = 1
    TYPE_ZERO_PAGED = 2
    TYPE_ABSOLUTE_INDEXED_X = 3
    TYPE_ABSOLUTE_INDEXED_Y = 4
    TYPE_ZERO_PAGED_INDEXED_X = 5
    TYPE_INDEXED_INDIRECT = 6
    TYPE_INDIRECT_INDEXED = 7
    TYPE_INDIRECT = 8
    TYPE_LABEL = 9
    def __init__(self, value, type):
        self.__value = value
        self.__type = type
    def get_type(self):
        return self.__type

class AssemblyInstruction(object):
    INSTRUCTION_ADC = 0
    INSTRUCTION_AND = 1
    INSTRUCTION_ASL = 2
    INSTRUCTION_BCC = 3
    INSTRUCTION_BCS = 4
    INSTRUCTION_BEQ = 5
    INSTRUCTION_BMI = 6
    INSTRUCTION_BNE = 7
    INSTRUCTION_BPL = 8
    INSTRUCTION_BVC = 9
    INSTRUCTION_BVS = 10
    INSTRUCTION_BIT = 11
    INSTRUCTION_CLC = 12
    INSTRUCTION_CLD = 13
    INSTRUCTION_CLI = 14
    INSTRUCTION_CLR = 15
    INSTRUCTION_CLV = 16
    INSTRUCTION_CMP = 17
    INSTRUCTION_CPX = 18
    INSTRUCTION_CPY = 19
    INSTRUCTION_DEC = 20
    INSTRUCTION_DEX = 21
    INSTRUCTION_DEY = 22
    INSTRUCTION_EOR = 23
    INSTRUCTION_INC = 24
    INSTRUCTION_INV = 25
    INSTRUCTION_INX = 26
    INSTRUCTION_INY = 27
    INSTRUCTION_JMP = 28
    INSTRUCTION_JSR = 29
    INSTRUCTION_LDA = 30
    INSTRUCTION_LDX = 31
    INSTRUCTION_LDY = 32
    INSTRUCTION_LSR = 33
    INSTRUCTION_NOP = 34
    INSTRUCTION_ORA = 35
    INSTRUCTION_PHA = 36
    INSTRUCTION_PHP = 37
    INSTRUCTION_PLA = 38
    INSTRUCTION_PLP = 39
    INSTRUCTION_ROL = 40
    INSTRUCTION_ROR = 41
    INSTRUCTION_RTI = 42
    INSTRUCTION_RTS = 43
    INSTRUCTION_SBC = 44
    INSTRUCTION_SEC = 45
    INSTRUCTION_SED = 46
    INSTRUCTION_SEI = 47
    INSTRUCTION_SET = 48
    INSTRUCTION_STA = 49
    INSTRUCTION_STX = 50
    INSTRUCTION_STY = 51
    INSTRUCTION_TAX = 52
    INSTRUCTION_TAY = 53
    INSTRUCTION_TST = 54
    INSTRUCTION_TSX = 55
    INSTRUCTION_TSY = 56
    INSTRUCTION_TXS = 57
    INSTRUCTION_TXA = 58
    INSTRUCTION_TYA = 59

    KNOWN_INSTRUCTIONS = {
        'ADC' : INSTRUCTION_ADC,
        'AND' : INSTRUCTION_AND,
        'ASL' : INSTRUCTION_ASL,
        'BCC' : INSTRUCTION_BCC,
        'BCS' : INSTRUCTION_BCS,
        'BEQ' : INSTRUCTION_BEQ,
        'BMI' : INSTRUCTION_BMI,
        'BNE' : INSTRUCTION_BNE,
        'BPL' : INSTRUCTION_BPL,
        'BVC' : INSTRUCTION_BVC,
        'BVS' : INSTRUCTION_BVS,
        'BIT' : INSTRUCTION_BIT,
        'CLC' : INSTRUCTION_CLC,
        'CLD' : INSTRUCTION_CLD,
        'CLI' : INSTRUCTION_CLI,
        'CLR' : INSTRUCTION_CLR,
        'CLV' : INSTRUCTION_CLV,
        'CMP' : INSTRUCTION_CMP,
        'CPX' : INSTRUCTION_CPX,
        'CPY' : INSTRUCTION_CPY,
        'DEC' : INSTRUCTION_DEC,
        'DEX' : INSTRUCTION_DEX,
        'DEY' : INSTRUCTION_DEY,
        'EOR' : INSTRUCTION_EOR,
        'INC' : INSTRUCTION_INC,
        'INV' : INSTRUCTION_INV,
        'INX' : INSTRUCTION_INX,
        'INY' : INSTRUCTION_INY,
        'JMP' : INSTRUCTION_JMP,
        'JSR' : INSTRUCTION_JSR,
        'LDA' : INSTRUCTION_LDA,
        'LDX' : INSTRUCTION_LDX,
        'LDY' : INSTRUCTION_LDY,
        'LSR' : INSTRUCTION_LSR,
        'NOP' : INSTRUCTION_NOP,
        'ORA' : INSTRUCTION_ORA,
        'PHA' : INSTRUCTION_PHA,
        'PHP' : INSTRUCTION_PHP,
        'PLA' : INSTRUCTION_PLA,
        'PLP' : INSTRUCTION_PLP,
        'ROL' : INSTRUCTION_ROL,
        'ROR' : INSTRUCTION_ROR,
        'RTI' : INSTRUCTION_RTI,
        'RTS' : INSTRUCTION_RTS,
        'SBC' : INSTRUCTION_SBC,
        'SEC' : INSTRUCTION_SEC,
        'SED' : INSTRUCTION_SED,
        'SEI' : INSTRUCTION_SEI,
        'SET' : INSTRUCTION_SET,
        'STA' : INSTRUCTION_STA,
        'STX' : INSTRUCTION_STX,
        'STY' : INSTRUCTION_STY,
        'TAX' : INSTRUCTION_TAX,
        'TAY' : INSTRUCTION_TAY,
        'TST' : INSTRUCTION_TST,
        'TSX' : INSTRUCTION_TSX,
        'TXA' : INSTRUCTION_TXA,
        'TXS' : INSTRUCTION_TXS
    }
    # INSTRUCTION_DATA = {
    #     AddressValue.TYPE_ABSOLUTE :                {'opcode':0x00, 'numbytes':0, 'numcycles':2},
    #     AddressValue.TYPE_ZERO_PAGED :              {'opcode':0x00, 'numbytes':0, 'numcycles':2},
    #     AddressValue.TYPE_ABSOLUTE_INDEXED_X :      {'opcode':0x00, 'numbytes':0, 'numcycles':2},
    #     AddressValue.TYPE_ABSOLUTE_INDEXED_Y :      {'opcode':0x00, 'numbytes':0, 'numcycles':2},
    #     AddressValue.TYPE_ZERO_PAGED_INDEXED_X :    {'opcode':0x00, 'numbytes':0, 'numcycles':2},
    #     AddressValue.TYPE_INDEXED_INDIRECT :        {'opcode':0x00, 'numbytes':0, 'numcycles':2}, # (Adr,X)
    #     AddressValue.TYPE_INDIRECT_INDEXED :        {'opcode':0x00, 'numbytes':0, 'numcycles':2}, # (Adr),Y
    #     AddressValue.TYPE_INDIRECT :                {'opcode':0x00, 'numbytes':0, 'numcycles':2}, # (Adr)
    #     AddressValue.TYPE_LABEL :                   {'opcode':0x00, 'numbytes':0, 'numcycles':2},
    # }
    @staticmethod
    def parse_opcode(token):
        '''this converts the op code string to a easiert to handle integer'''
        #print(token.dump())
        op_code = token['op_code'].upper()
        return AssemblyInstruction.KNOWN_INSTRUCTIONS.get(op_code, None)
    @staticmethod
    def decode_instruction_data(instruction_data, operand):
        data = instruction_data.get(operand.get_type(), None)
        if data is not None:
            return data['opcode'], data['numbytes'], data['numcycles']
        else:
            raise ValueError('unknonw Adress Type for instuction')

class Inst_ADC(AssemblyInstruction):
    INSTRUCTION_DATA = {
        AddressValue.TYPE_ABSOLUTE :                {'opcode':0x6D, 'numbytes':3, 'numcycles':4},
        AddressValue.TYPE_ZERO_PAGED :              {'opcode':0x65, 'numbytes':2, 'numcycles':3},
        AddressValue.TYPE_ABSOLUTE_INDEXED_X :      {'opcode':0x7D, 'numbytes':3, 'numcycles':4},
        AddressValue.TYPE_ABSOLUTE_INDEXED_Y :      {'opcode':0x79, 'numbytes':3, 'numcycles':4},
        AddressValue.TYPE_ZERO_PAGED_INDEXED_X :    {'opcode':0x75, 'numbytes':2, 'numcycles':4},
        AddressValue.TYPE_INDEXED_INDIRECT :        {'opcode':0x61, 'numbytes':2, 'numcycles':6}, # (Adr,X)
        AddressValue.TYPE_INDIRECT_INDEXED :        {'opcode':0x71, 'numbytes':2, 'numcycles':6}, # (Adr),Y
        #AddressValue.TYPE_INDIRECT :                {'opcode':0x00, 'numbytes':2, 'numcycles':2}, # (Adr)
        #AddressValue.TYPE_LABEL :                   {'opcode':0x00, 'numbytes':2, 'numcycles':2},
    }
    def __init__(self, operand):
        self.__operand = operand
        self.__op_code = -1
        self.__num_bytes = -1
        self.__num_cycles = -1
        if isinstance(self.__operand, int):
            self.__op_code = 0x69
            self.__num_bytes = 2
            self.__num_cycles = 2
        elif isinstance(self.__operand, AddressValue):
            if self.__operand.get_type() is AddressValue.TYPE_LABEL:
                '''if the operand is a label we have to wait until the actual
                assembly of the program to get an address'''
                pass
            else:
                self.__op_code, self.__num_bytes, self.__num_cycles = AssemblyInstruction.decode_instruction_data(self.INSTRUCTION_DATA, self.__operand)
        else:
            raise NotImplementedError('somthing went wrong or we found a case that we didnt think about')

class Inst_CLC(AssemblyInstruction):
    def __init__(self):
        self.__op_code = 0x18
        self.__num_bytes = 1
        self.__num_cycles = 2
class Inst_CLD(AssemblyInstruction):
    def __init__(self):
        self.__op_code = 0xD8
        self.__num_bytes = 1
        self.__num_cycles = 2
class Inst_CLI(AssemblyInstruction):
    def __init__(self):
        self.__op_code = 0x58
        self.__num_bytes = 1
        self.__num_cycles = 2
class Inst_CLV(AssemblyInstruction):
    def __init__(self):
        self.__op_code = 0xB8
        self.__num_bytes = 1
        self.__num_cycles = 2
class Inst_DEX(AssemblyInstruction):
    def __init__(self):
        self.__op_code = 0xCA
        self.__num_bytes = 1
        self.__num_cycles = 2
class Inst_DEY(AssemblyInstruction):
    def __init__(self):
        self.__op_code = 0x88
        self.__num_bytes = 1
        self.__num_cycles = 2
class Inst_INX(AssemblyInstruction):
    def __init__(self):
        self.__op_code = 0xE8
        self.__num_bytes = 1
        self.__num_cycles = 2
class Inst_INY(AssemblyInstruction):
    def __init__(self):
        self.__op_code = 0xC8
        self.__num_bytes = 1
        self.__num_cycles = 2
class Inst_NOP(AssemblyInstruction):
    def __init__(self):
        self.__op_code = 0xEA
        self.__num_bytes = 1
        self.__num_cycles = 2
class Inst_PHA(AssemblyInstruction):
    def __init__(self):
        self.__op_code = 0x48
        self.__num_bytes = 1
        self.__num_cycles = 3
class Inst_PHP(AssemblyInstruction):
    def __init__(self):
        self.__op_code = 0x08
        self.__num_bytes = 1
        self.__num_cycles = 3
class Inst_PLA(AssemblyInstruction):
    def __init__(self):
        self.__op_code = 0x68
        self.__num_bytes = 1
        self.__num_cycles = 4
class Inst_PLP(AssemblyInstruction):
    def __init__(self):
        self.__op_code = 0x28
        self.__num_bytes = 1
        self.__num_cycles = 4
class Inst_RTI(AssemblyInstruction):
    def __init__(self):
        self.__op_code = 0x40
        self.__num_bytes = 1
        self.__num_cycles = 6
class Inst_RTS(AssemblyInstruction):
    def __init__(self):
        self.__op_code = 0x60
        self.__num_bytes = 1
        self.__num_cycles = 6
class Inst_SEC(AssemblyInstruction):
    def __init__(self):
        self.__op_code = 0x38
        self.__num_bytes = 1
        self.__num_cycles = 2
class Inst_SED(AssemblyInstruction):
    def __init__(self):
        self.__op_code = 0xF8
        self.__num_bytes = 1
        self.__num_cycles = 2
class Inst_SEI(AssemblyInstruction):
    def __init__(self):
        self.__op_code = 0x78
        self.__num_bytes = 1
        self.__num_cycles = 2
class Inst_TAX(AssemblyInstruction):
    def __init__(self):
        self.__op_code = 0xAA
        self.__num_bytes = 1
        self.__num_cycles = 2
class Inst_TAY(AssemblyInstruction):
    def __init__(self):
        self.__op_code = 0xA8
        self.__num_bytes = 1
        self.__num_cycles = 2
class Inst_TSX(AssemblyInstruction):
    def __init__(self):
        self.__op_code = 0xBA
        self.__num_bytes = 1
        self.__num_cycles = 2
class Inst_TXA(AssemblyInstruction):
    def __init__(self):
        self.__op_code = 0x8A
        self.__num_bytes = 1
        self.__num_cycles = 2
class Inst_TXS(AssemblyInstruction):
    def __init__(self):
        self.__op_code = 0x9A
        self.__num_bytes = 1
        self.__num_cycles = 2
class Inst_TYA(AssemblyInstruction):
    def __init__(self):
        self.__op_code = 0x98
        self.__num_bytes = 1
        self.__num_cycles = 2
