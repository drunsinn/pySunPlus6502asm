#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: drunsinn
@license: MIT License
"""
import os
import re
import sys
import logging
from pyparsing import (ParserElement, Group, Optional, Word, alphas, alphanums,
                      Suppress, Literal, restOfLine, ParseException, Or, LineEnd,
                      LineStart, CaselessKeyword)
from AssemblerInstructions import *
from PreProcessInstructions import *

class SunPlus6502Assembler(object):
    def __init__(self, main_asm_file):
        '''steps: - none of this works currently!!!!!!
        1. read file and convert each line to list of objects
        2. read list while calculating the address of each instruchtion and calculate adress for each label
        3. replace all labels with thier address
        4. output instructions as hex file'''
        self.logger = logging.getLogger(__name__)
        self.main_asm_file = main_asm_file
        self.__build_grammar()
        tokens = self.parse_file(main_asm_file)
        for i, token in enumerate(tokens):
            print("%d : %s" % (i, token))

    def __build_grammar(self):
        ParserElement.setDefaultWhitespaceChars(' \t')

        # labels as per sunplus manual page 22, acceptabel characters might have to be tuned
        label_name = Word(alphas, bodyChars=alphanums+'_', min=1, max=32)
        label_field = Group(label_name + Suppress(Literal(':'))).setResultsName('label').setParseAction(Label.from_parsing)

        op_code_field = Word(alphas).setResultsName('op_code').setParseAction(AssemblyInstruction.parse_opcode)

        operand_field = Word(alphanums+'#%$(),_').setResultsName('operand').setParseAction(SunPlus6502Assembler.parse_operand_field)

        comment_filed = Group(Suppress(Literal(';')) + restOfLine()).setResultsName('comment').setParseAction(Comment.from_parsing)

        assembly_instruction = Group(Optional(label_field) + op_code_field + Optional(operand_field) + Optional(comment_filed)).setParseAction(SunPlus6502Assembler.parse_op_code)

        label_only = Group(label_name + Suppress(Literal(':')) + LineEnd()).setResultsName('label').setParseAction(Label.from_parsing)
        comment_line = Group(Suppress(Literal(';')) + restOfLine()).setResultsName('comment').setParseAction(Comment.from_parsing)

        self.grammar = Or(assembly_instruction | label_only | comment_line)
        self.logger.debug('grammer is ready')

    def parse_file(self, file_path):
        if not os.path.isfile(file_path):
            self.logger.error(u'file not found')
            return None
        self.logger.debug('start parsing of {:s}'.format(file_path))

        instructions = list()
        with open(file_path, 'r') as fp:
            for line in fp:
                line = line.strip()
                instr = None
                try:
                    if len(line) > 0: # filter empty lines
                        instr = self.grammar.parseString(line)
                except ParseException as pe:
                    self.logger.error('parsing faild on line "%s"', line)
                    self.logger.debug('Parse Error: %s', pe)
                    return None

                if instr is not None:
                    if isinstance(instr, PreInst_Include):
                        include_instr = parse_file(instr.get_filename())
                        instructions.extend(include_instr)
                    else:
                        instructions.append(instr)
                else:
                    self.logger.error('parsing faild on line "%s"', line)

        self.logger.info('parser found %d tokens', len(instructions))
        return instructions

    @staticmethod
    def parse_operand_field(token):
        '''operand can be an address value, a numerical value or a label. we
        decide here which it is and return the correct object'''
        logger = logging.getLogger(__name__)
        #print(token.dump(), type(token['operand']))

        operand = token['operand'].strip()
        if operand is 'A':
            logger.debug('Parse operand %s as Accumulator', operand)
            return AddressValue(value='A', type=AddressValue.TYPE_ACCUMULATOR)
        elif operand.startswith('$'):
            logger.debug('Parse operand %s as address value', operand)
            operand = operand.lstrip('$')
            if operand.endswith(',X'):
                operand.rstrip(',X')
                value = SunPlus6502Assembler.parse_number_string(operand)
                if value > 0xFF:
                    type = AddressValue.TYPE_ABSOLUTE_INDEXED_X
                else:
                    type = AddressValue.TYPE_ZERO_PAGED_INDEXED_X
            elif operand.endswith(',Y'):
                operand.rstrip(',Y')
                value = SunPlus6502Assembler.parse_number_string(operand)
                type = AddressValue.TYPE_ABSOLUTE_INDEXED_Y
            else:
                value = SunPlus6502Assembler.parse_number_string(operand)
                if value > 0xFF:
                    type = AddressValue.TYPE_ABSOLUTE
                else:
                    type = AddressValue.TYPE_ZERO_PAGED
            #print(operand, value, type)
            return AddressValue(value, type)
        elif operand.startswith('#'):
            logger.debug('Parse operand %s as numerical value', operand)
            #TODO depending on the op code this could be an address or just a numerical value....
            return SunPlus6502Assembler.parse_number_string(operand)
        elif operand.startswith('($'):
            logger.debug('Parse operand %s as indirect or indexed address value', operand)
            operand = operand.lstrip('($')
            if operand.endswith(',X)'):
                operand.rstrip(',X)')
                value = SunPlus6502Assembler.parse_number_string(operand)
                type = AddressValue.TYPE_INDEXED_INDIRECT
            elif operand.endswith('),Y'):
                operand.rstrip('),Y')
                value = SunPlus6502Assembler.parse_number_string(operand)
                type = AddressValue.TYPE_INDIRECT_INDEXED
            else:
                operand.rstrip(')')
                value = SunPlus6502Assembler.parse_number_string(operand)
                type = AddressValue.TYPE_INDIRECT
            return AddressValue(value, type)
        else:
            logger.debug('Parse operand %s as label', operand)
            return AddressValue(value=token['operand'], type=AddressValue.TYPE_LABEL)

    @staticmethod
    def parse_number_string(str):
        '''
        binary: #%00000001 or #00000001B
        decimal: #01 or #01D
        hexdecimal: #01H or #$01
        '''
        logger = logging.getLogger(__name__)
        re_binary = re.compile('#%([01]{8})|#([01]{8})B')
        re_decimal = re.compile('#([\d]{1,7})(?!H|B|\d)D?')
        re_hexadecimal = re.compile('#([0-9A-F]{2,4})H|#\$([0-9A-F]{2,4})')
        value = None
        bin_result = re_binary.match(str)
        dec_result = re_decimal.match(str)
        hex_result = re_hexadecimal.match(str)
        if bin_result is not None:
            if bin_result.group(1) is not None:
                value = int(bin_result.group(1), 2)
            else:
                value = int(bin_result.group(2), 2)
        elif dec_result is not None:
            value = int(dec_result.group(1), 10)
        elif hex_result is not None:
            value = int(hex_result.group(1), 16)
        else:
            raise ValueError('could not match operand to numerical value: %s' % str)
        logger.debug('parsed string %s to int %d' % (str, value))
        return value

    @staticmethod
    def parse_op_code(token):
        op_code = token[0]['op_code']
        if 'operand' in token[0]:
            operand = token[0]['operand']
        else:
            operand = None
        if op_code is AssemblyInstruction.INSTRUCTION_ADC:
            return Inst_ADC(operand)
        elif op_code is AssemblyInstruction.INSTRUCTION_AND:
            return Inst_AND(operand)
        elif op_code is AssemblyInstruction.INSTRUCTION_ASL:
            return Inst_ASL(operand)
        elif op_code is AssemblyInstruction.INSTRUCTION_BCC:
            raise NotImplementedError() #TODO
        elif op_code is AssemblyInstruction.INSTRUCTION_BCS:
            raise NotImplementedError() #TODO
        elif op_code is AssemblyInstruction.INSTRUCTION_BEQ:
            raise NotImplementedError() #TODO
        elif op_code is AssemblyInstruction.INSTRUCTION_BMI:
            raise NotImplementedError() #TODO
        elif op_code is AssemblyInstruction.INSTRUCTION_BNE:
            raise NotImplementedError() #TODO
        elif op_code is AssemblyInstruction.INSTRUCTION_BPL:
            raise NotImplementedError() #TODO
        elif op_code is AssemblyInstruction.INSTRUCTION_BVC:
            raise NotImplementedError() #TODO
        elif op_code is AssemblyInstruction.INSTRUCTION_BVS:
            raise NotImplementedError() #TODO
        elif op_code is AssemblyInstruction.INSTRUCTION_BIT:
            raise NotImplementedError() #TODO
        elif op_code is AssemblyInstruction.INSTRUCTION_CLC:
            return Inst_CLC()
        elif op_code is AssemblyInstruction.INSTRUCTION_CLD:
            return Inst_CLD()
        elif op_code is AssemblyInstruction.INSTRUCTION_CLI:
            return Inst_CLI()
        elif op_code is AssemblyInstruction.INSTRUCTION_CLR:
            raise NotImplementedError() #TODO
        elif op_code is AssemblyInstruction.INSTRUCTION_CLV:
            return Inst_CLV()
        elif op_code is AssemblyInstruction.INSTRUCTION_CMP:
            raise NotImplementedError() #TODO
        elif op_code is AssemblyInstruction.INSTRUCTION_CPX:
            raise NotImplementedError() #TODO
        elif op_code is AssemblyInstruction.INSTRUCTION_CPY:
            raise NotImplementedError() #TODO
        elif op_code is AssemblyInstruction.INSTRUCTION_DEC:
            raise NotImplementedError() #TODO
        elif op_code is AssemblyInstruction.INSTRUCTION_DEX:
            return Inst_DEX()
        elif op_code is AssemblyInstruction.INSTRUCTION_DEY:
            return Inst_DEY()
        elif op_code is AssemblyInstruction.INSTRUCTION_EOR:
            raise NotImplementedError() #TODO
        elif op_code is AssemblyInstruction.INSTRUCTION_INC:
            raise NotImplementedError() #TODO
        elif op_code is AssemblyInstruction.INSTRUCTION_INX:
            return Inst_INX()
        elif op_code is AssemblyInstruction.INSTRUCTION_INY:
            return Inst_INY()
        elif op_code is AssemblyInstruction.INSTRUCTION_JMP:
            raise NotImplementedError() #TODO
        elif op_code is AssemblyInstruction.INSTRUCTION_JSR:
            raise NotImplementedError() #TODO
        elif op_code is AssemblyInstruction.INSTRUCTION_LDA:
            raise NotImplementedError() #TODO
        elif op_code is AssemblyInstruction.INSTRUCTION_LDX:
            raise NotImplementedError() #TODO
        elif op_code is AssemblyInstruction.INSTRUCTION_LDY:
            raise NotImplementedError() #TODO
        elif op_code is AssemblyInstruction.INSTRUCTION_LSR:
            raise NotImplementedError() #TODO
        elif op_code is AssemblyInstruction.INSTRUCTION_NOP:
            return Inst_NOP()
        elif op_code is AssemblyInstruction.INSTRUCTION_ORA:
            raise NotImplementedError() #TODO
        elif op_code is AssemblyInstruction.INSTRUCTION_PHA:
            return Inst_PHA()
        elif op_code is AssemblyInstruction.INSTRUCTION_PHP:
            return Inst_PHP()
        elif op_code is AssemblyInstruction.INSTRUCTION_PLA:
            return Inst_PLA()
        elif op_code is AssemblyInstruction.INSTRUCTION_PLP:
            return Inst_PLP()
        elif op_code is AssemblyInstruction.INSTRUCTION_ROL:
            raise NotImplementedError() #TODO
        elif op_code is AssemblyInstruction.INSTRUCTION_ROR:
            raise NotImplementedError() #TODO
        elif op_code is AssemblyInstruction.INSTRUCTION_RTI:
            return Inst_RTI()
        elif op_code is AssemblyInstruction.INSTRUCTION_RTS:
            return Inst_RTS()
        elif op_code is AssemblyInstruction.INSTRUCTION_SBC:
            raise NotImplementedError() #TODO
        elif op_code is AssemblyInstruction.INSTRUCTION_SEC:
            return Inst_SEC()
        elif op_code is AssemblyInstruction.INSTRUCTION_SED:
            return Inst_SED()
        elif op_code is AssemblyInstruction.INSTRUCTION_SEI:
            return Inst_SEI()
        elif op_code is AssemblyInstruction.INSTRUCTION_SET:
            raise NotImplementedError() #TODO
        elif op_code is AssemblyInstruction.INSTRUCTION_STA:
            raise NotImplementedError() #TODO
        elif op_code is AssemblyInstruction.INSTRUCTION_STX:
            raise NotImplementedError() #TODO
        elif op_code is AssemblyInstruction.INSTRUCTION_STY:
            raise NotImplementedError() #TODO
        elif op_code is AssemblyInstruction.INSTRUCTION_TAX:
            return Inst_TAX()
        elif op_code is AssemblyInstruction.INSTRUCTION_TAY:
            return Inst_TAY()
        elif op_code is AssemblyInstruction.INSTRUCTION_TST:
            raise NotImplementedError() #TODO
        elif op_code is AssemblyInstruction.INSTRUCTION_TSX:
            return Inst_TSX()
        elif op_code is AssemblyInstruction.INSTRUCTION_TXA:
            return Inst_TXA()
        elif op_code is AssemblyInstruction.INSTRUCTION_TXS:
            return Inst_TXS()
        elif op_code is AssemblyInstruction.INSTRUCTION_TYA:
            return Inst_TYA()
        elif 'include' in op_code:
            return PreInst_Include(operand.get_value())
        else:
            print(token.dump())
            raise NotImplementedError('unknown op code %s'%op_code)

if __name__ == "__main__":
    import argparse
    logging_levels = {'critical': logging.CRITICAL, 'error': logging.ERROR, 'warn': logging.WARNING,
                      'warning': logging.WARNING, 'info': logging.INFO, 'debug': logging.DEBUG}

    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="main assembler file")
    parser.add_argument("-l", "--log_level", default="warning", help="set level for logger")

    args = parser.parse_args()
    print(args)
    selected_level = logging_levels.get(args.log_level.lower())
    logging.basicConfig(level=selected_level)
    logger = logging.getLogger(__name__)

    fasm = SunPlus6502Assembler(args.input)
