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
    TYPE_IMMEDIATE = 9
    TYPE_LABEL = 10
    TYPE_IMPLIED = 11
    def __init__(self, value, type):
        self.__value = value
        self.__type = type
    def get_type(self):
        return self.__type
    def get_value(self):
        return self.__value

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
        'ADC' : INSTRUCTION_ADC, 'AND' : INSTRUCTION_AND,
        'ASL' : INSTRUCTION_ASL, 'BCC' : INSTRUCTION_BCC,
        'BCS' : INSTRUCTION_BCS, 'BEQ' : INSTRUCTION_BEQ,
        'BMI' : INSTRUCTION_BMI, 'BNE' : INSTRUCTION_BNE,
        'BPL' : INSTRUCTION_BPL, 'BVC' : INSTRUCTION_BVC,
        'BVS' : INSTRUCTION_BVS, 'BIT' : INSTRUCTION_BIT,
        'CLC' : INSTRUCTION_CLC, 'CLD' : INSTRUCTION_CLD,
        'CLI' : INSTRUCTION_CLI, 'CLR' : INSTRUCTION_CLR,
        'CLV' : INSTRUCTION_CLV, 'CMP' : INSTRUCTION_CMP,
        'CPX' : INSTRUCTION_CPX, 'CPY' : INSTRUCTION_CPY,
        'DEC' : INSTRUCTION_DEC, 'DEX' : INSTRUCTION_DEX,
        'DEY' : INSTRUCTION_DEY, 'EOR' : INSTRUCTION_EOR,
        'INC' : INSTRUCTION_INC, 'INV' : INSTRUCTION_INV,
        'INX' : INSTRUCTION_INX, 'INY' : INSTRUCTION_INY,
        'JMP' : INSTRUCTION_JMP, 'JSR' : INSTRUCTION_JSR,
        'LDA' : INSTRUCTION_LDA, 'LDX' : INSTRUCTION_LDX,
        'LDY' : INSTRUCTION_LDY, 'LSR' : INSTRUCTION_LSR,
        'NOP' : INSTRUCTION_NOP, 'ORA' : INSTRUCTION_ORA,
        'PHA' : INSTRUCTION_PHA, 'PHP' : INSTRUCTION_PHP,
        'PLA' : INSTRUCTION_PLA, 'PLP' : INSTRUCTION_PLP,
        'ROL' : INSTRUCTION_ROL, 'ROR' : INSTRUCTION_ROR,
        'RTI' : INSTRUCTION_RTI, 'RTS' : INSTRUCTION_RTS,
        'SBC' : INSTRUCTION_SBC, 'SEC' : INSTRUCTION_SEC,
        'SED' : INSTRUCTION_SED, 'SEI' : INSTRUCTION_SEI,
        'SET' : INSTRUCTION_SET, 'STA' : INSTRUCTION_STA,
        'STX' : INSTRUCTION_STX, 'STY' : INSTRUCTION_STY,
        'TAX' : INSTRUCTION_TAX, 'TAY' : INSTRUCTION_TAY,
        'TST' : INSTRUCTION_TST, 'TSX' : INSTRUCTION_TSX,
        'TXA' : INSTRUCTION_TXA, 'TXS' : INSTRUCTION_TXS
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

    def __init__(self, inst_data, operand=None):
        self.__op_code = -1
        self.__num_bytes = -1
        self.__num_cycles = -1
        self.__operand = operand
        if self.__operand is not None:
            if isinstance(self.__operand, int): # Adress type immediate
                self.__op_code = inst_data[AddressValue.TYPE_IMMEDIATE]['opcode']
                self.__num_bytes = inst_data[AddressValue.TYPE_IMMEDIATE]['numbytes']
                self.__num_cycles = inst_data[AddressValue.TYPE_IMMEDIATE]['numcycles']
            elif isinstance(self.__operand, AddressValue):
                if self.__operand.get_type() is AddressValue.TYPE_LABEL:
                    '''if the operand is a label we have to wait until the actual
                    assembly of the program to get an address'''
                    pass
                else:
                    self.__op_code, self.__num_bytes, self.__num_cycles = self.decode_instruction_data(inst_data, self.__operand)
            else:
                raise NotImplementedError('somthing went wrong or we found a case that we didnt think about')
        else:
            self.__op_code = inst_data[AddressValue.TYPE_IMPLIED]['opcode']
            self.__num_bytes = inst_data[AddressValue.TYPE_IMPLIED]['numbytes']
            self.__num_cycles = inst_data[AddressValue.TYPE_IMPLIED]['numcycles']

    def decode_instruction_data(self, instruction_data, operand):
        data = instruction_data.get(operand.get_type(), None)
        if data is not None:
            return data['opcode'], data['numbytes'], data['numcycles']
        else:
            raise ValueError('unknonw Adress Type for instuction')

    def to_bin(self):
        if isinstance(self.__operand, int):
            value = self.__operand
        else:
            value = self.__operand.get_value()
        if self.__num_bytes is 1:
            return '{:02X}'.format(self.__op_code)
        elif self.__num_bytes is 2:
            if value > 0xFF:
                raise ValueError('operand value to big for op code')
            return '{:02X}{:02X}'.format(self.__op_code, value)
        elif self.__num_bytes is 3:
            return '{:02X}{:04X}'.format(self.__op_code, value)
        else:
            raise ValueError('unexpected number of bytes for operation')

class Inst_ADC(AssemblyInstruction):
    INSTRUCTION_DATA = {
        AddressValue.TYPE_IMMEDIATE :               {'opcode':0x56, 'numbytes':2, 'numcycles':2},
        AddressValue.TYPE_ABSOLUTE :                {'opcode':0x57, 'numbytes':3, 'numcycles':4},
        AddressValue.TYPE_ZERO_PAGED :              {'opcode':0x17, 'numbytes':2, 'numcycles':3},
        AddressValue.TYPE_ABSOLUTE_INDEXED_X :      {'opcode':0x5F, 'numbytes':3, 'numcycles':4},
        AddressValue.TYPE_ABSOLUTE_INDEXED_Y :      {'opcode':0x5E, 'numbytes':3, 'numcycles':4},
        AddressValue.TYPE_ZERO_PAGED_INDEXED_X :    {'opcode':0x1F, 'numbytes':2, 'numcycles':4},
        AddressValue.TYPE_INDEXED_INDIRECT :        {'opcode':0x16, 'numbytes':2, 'numcycles':6}, # (Adr,X)
        AddressValue.TYPE_INDIRECT_INDEXED :        {'opcode':0x1E, 'numbytes':2, 'numcycles':6}, # (Adr),Y
        #AddressValue.TYPE_INDIRECT :                {'opcode':0x00, 'numbytes':2, 'numcycles':2}, # (Adr)
        #AddressValue.TYPE_LABEL :                   {'opcode':0x00, 'numbytes':2, 'numcycles':2},
    }
    def __init__(self, operand):
        super().__init__(self.INSTRUCTION_DATA, operand)


class Inst_AND(AssemblyInstruction):
    INSTRUCTION_DATA = {
        AddressValue.TYPE_IMMEDIATE :               {'opcode':0x54, 'numbytes':2, 'numcycles':2},
        AddressValue.TYPE_ZERO_PAGED :              {'opcode':0x15, 'numbytes':2, 'numcycles':3},
        AddressValue.TYPE_ZERO_PAGED_INDEXED_X :    {'opcode':0x1D, 'numbytes':2, 'numcycles':4},
        AddressValue.TYPE_ABSOLUTE :                {'opcode':0x55, 'numbytes':3, 'numcycles':4},
        AddressValue.TYPE_ABSOLUTE_INDEXED_X :      {'opcode':0x5D, 'numbytes':3, 'numcycles':4},
        AddressValue.TYPE_ABSOLUTE_INDEXED_Y :      {'opcode':0x5C, 'numbytes':3, 'numcycles':4},
        AddressValue.TYPE_INDEXED_INDIRECT :        {'opcode':0x14, 'numbytes':2, 'numcycles':6}, # (Adr,X)
        AddressValue.TYPE_INDIRECT_INDEXED :        {'opcode':0x1C, 'numbytes':2, 'numcycles':6}, # (Adr),Y
        #AddressValue.TYPE_INDIRECT :                {'opcode':0x00, 'numbytes':2, 'numcycles':2}, # (Adr)
    }
    def __init__(self, operand):
        super().__init__(self.INSTRUCTION_DATA, operand)


class Inst_ASL(AssemblyInstruction):
    INSTRUCTION_DATA = {
        AddressValue.TYPE_ACCUMULATOR :             {'opcode':0xC0, 'numbytes':1, 'numcycles':2},
        AddressValue.TYPE_ZERO_PAGED :              {'opcode':0x81, 'numbytes':2, 'numcycles':5},
        AddressValue.TYPE_ZERO_PAGED_INDEXED_X :    {'opcode':0x89, 'numbytes':2, 'numcycles':6},
        AddressValue.TYPE_ABSOLUTE :                {'opcode':0xC1, 'numbytes':3, 'numcycles':6},
        AddressValue.TYPE_ABSOLUTE_INDEXED_X :      {'opcode':0xC9, 'numbytes':3, 'numcycles':6},
        #AddressValue.TYPE_ABSOLUTE_INDEXED_Y :      {'opcode':0x5C, 'numbytes':3, 'numcycles':4},
        #AddressValue.TYPE_INDEXED_INDIRECT :        {'opcode':0x14, 'numbytes':2, 'numcycles':6}, # (Adr,X)
        #AddressValue.TYPE_INDIRECT_INDEXED :        {'opcode':0x1C, 'numbytes':2, 'numcycles':6}, # (Adr),Y
        #AddressValue.TYPE_INDIRECT :                {'opcode':0x00, 'numbytes':2, 'numcycles':2}, # (Adr)
    }
    def __init__(self, operand):
        super().__init__(self.INSTRUCTION_DATA, operand)


class Inst_CLC(AssemblyInstruction):
    INSTRUCTION_DATA = {AddressValue.TYPE_IMPLIED : {'opcode':0x48, 'numbytes':1, 'numcycles':2}}
    def __init__(self):
        super().__init__(self.INSTRUCTION_DATA)

class Inst_CLD(AssemblyInstruction):
    INSTRUCTION_DATA = {AddressValue.TYPE_IMPLIED : {'opcode':0x6A, 'numbytes':1, 'numcycles':2}}
    def __init__(self):
        super().__init__(self.INSTRUCTION_DATA)

class Inst_CLI(AssemblyInstruction):
    INSTRUCTION_DATA = {AddressValue.TYPE_IMPLIED : {'opcode':0x4A, 'numbytes':1, 'numcycles':2}}
    def __init__(self):
        super().__init__(self.INSTRUCTION_DATA)

class Inst_CLV(AssemblyInstruction):
    INSTRUCTION_DATA = {AddressValue.TYPE_IMPLIED : {'opcode':0x78, 'numbytes':1, 'numcycles':2}}
    def __init__(self):
        super().__init__(self.INSTRUCTION_DATA)

class Inst_DEX(AssemblyInstruction):
    INSTRUCTION_DATA = {AddressValue.TYPE_IMPLIED : {'opcode':0xE2, 'numbytes':1, 'numcycles':2}}
    def __init__(self):
        super().__init__(self.INSTRUCTION_DATA)

class Inst_DEY(AssemblyInstruction):
    INSTRUCTION_DATA = {AddressValue.TYPE_IMPLIED : {'opcode':0x60, 'numbytes':1, 'numcycles':2}}
    def __init__(self):
        super().__init__(self.INSTRUCTION_DATA)

class Inst_INX(AssemblyInstruction):
    INSTRUCTION_DATA = {AddressValue.TYPE_IMPLIED : {'opcode':0x72, 'numbytes':1, 'numcycles':2}}
    def __init__(self):
        super().__init__(self.INSTRUCTION_DATA)

class Inst_INY(AssemblyInstruction):
    INSTRUCTION_DATA = {AddressValue.TYPE_IMPLIED : {'opcode':0x62, 'numbytes':1, 'numcycles':2}}
    def __init__(self):
        super().__init__(self.INSTRUCTION_DATA)

class Inst_NOP(AssemblyInstruction):
    INSTRUCTION_DATA = {AddressValue.TYPE_IMPLIED : {'opcode':0xF2, 'numbytes':1, 'numcycles':2}}
    def __init__(self):
        super().__init__(self.INSTRUCTION_DATA)

class Inst_PHA(AssemblyInstruction):
    INSTRUCTION_DATA = {AddressValue.TYPE_IMPLIED : {'opcode':0x42, 'numbytes':1, 'numcycles':3}}
    def __init__(self):
        super().__init__(self.INSTRUCTION_DATA)

class Inst_PHP(AssemblyInstruction):
    INSTRUCTION_DATA = {AddressValue.TYPE_IMPLIED : {'opcode':0x40, 'numbytes':1, 'numcycles':3}}
    def __init__(self):
        super().__init__(self.INSTRUCTION_DATA)

class Inst_PLA(AssemblyInstruction):
    INSTRUCTION_DATA = {AddressValue.TYPE_IMPLIED : {'opcode':0x52, 'numbytes':1, 'numcycles':4}}
    def __init__(self):
        super().__init__(self.INSTRUCTION_DATA)

class Inst_PLP(AssemblyInstruction):
    INSTRUCTION_DATA = {AddressValue.TYPE_IMPLIED : {'opcode':0x50, 'numbytes':1, 'numcycles':4}}
    def __init__(self):
        super().__init__(self.INSTRUCTION_DATA)

class Inst_RTI(AssemblyInstruction):
    INSTRUCTION_DATA = {AddressValue.TYPE_IMPLIED : {'opcode':0x02, 'numbytes':1, 'numcycles':6}}
    def __init__(self):
        super().__init__(self.INSTRUCTION_DATA)

class Inst_RTS(AssemblyInstruction):
    INSTRUCTION_DATA = {AddressValue.TYPE_IMPLIED : {'opcode':0x12, 'numbytes':1, 'numcycles':6}}
    def __init__(self):
        super().__init__(self.INSTRUCTION_DATA)

class Inst_SEC(AssemblyInstruction):
    INSTRUCTION_DATA = {AddressValue.TYPE_IMPLIED : {'opcode':0x58, 'numbytes':1, 'numcycles':2}}
    def __init__(self):
        super().__init__(self.INSTRUCTION_DATA)

class Inst_SED(AssemblyInstruction):
    INSTRUCTION_DATA = {AddressValue.TYPE_IMPLIED : {'opcode':0x7A, 'numbytes':1, 'numcycles':2}}
    def __init__(self):
        super().__init__(self.INSTRUCTION_DATA)

class Inst_SEI(AssemblyInstruction):
    INSTRUCTION_DATA = {AddressValue.TYPE_IMPLIED : {'opcode':0x5A, 'numbytes':1, 'numcycles':2}}
    def __init__(self):
        super().__init__(self.INSTRUCTION_DATA)

class Inst_TAX(AssemblyInstruction):
    INSTRUCTION_DATA = {AddressValue.TYPE_IMPLIED : {'opcode':0xF0, 'numbytes':1, 'numcycles':2}}
    def __init__(self):
        super().__init__(self.INSTRUCTION_DATA)

class Inst_TAY(AssemblyInstruction):
    INSTRUCTION_DATA = {AddressValue.TYPE_IMPLIED : {'opcode':0x70, 'numbytes':1, 'numcycles':2}}
    def __init__(self):
        super().__init__(self.INSTRUCTION_DATA)

class Inst_TSX(AssemblyInstruction):
    INSTRUCTION_DATA = {AddressValue.TYPE_IMPLIED : {'opcode':0xF8, 'numbytes':1, 'numcycles':2}}
    def __init__(self):
        super().__init__(self.INSTRUCTION_DATA)

class Inst_TXA(AssemblyInstruction):
    INSTRUCTION_DATA = {AddressValue.TYPE_IMPLIED : {'opcode':0xE0, 'numbytes':1, 'numcycles':2}}
    def __init__(self):
        super().__init__(self.INSTRUCTION_DATA)

class Inst_TXS(AssemblyInstruction):
    INSTRUCTION_DATA = {AddressValue.TYPE_IMPLIED : {'opcode':0xE8, 'numbytes':1, 'numcycles':2}}
    def __init__(self):
        super().__init__(self.INSTRUCTION_DATA)

class Inst_TYA(AssemblyInstruction):
    INSTRUCTION_DATA = {AddressValue.TYPE_IMPLIED : {'opcode':0x68, 'numbytes':1, 'numcycles':2}}
    def __init__(self):
        super().__init__(self.INSTRUCTION_DATA)
