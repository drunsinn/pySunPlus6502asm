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
        '''WIP, not for actual use!'''
        self.logger = logging.getLogger(__name__)
        self.main_asm_file = main_asm_file
        self.__build_grammar()
        instructions = self.parse_file(main_asm_file)
        for i, instr in enumerate(instructions):
            print("%d : %s : %s" % (i, type(instr), instr))

        self.check_labels(instructions)

        label_addr_map = self.calculate_lable_pos(instructions)

        self.replace_label(instructions, label_addr_map)

        print(label_addr_map)

        for i, instr in enumerate(instructions):
            if isinstance(instr, AssemblyInstruction):
                print('line {:04d} translates to {:s}'.format(i, instr.to_bin()))



    def __build_grammar(self):
        ParserElement.setDefaultWhitespaceChars(' \t')

        # labels as per sunplus manual page 22, acceptabel characters might have to be tuned
        label_name = Word(alphas, bodyChars=alphanums+'_', min=1, max=32)
        label_field = Group(label_name + Suppress(Literal(':'))).setResultsName('label').setParseAction(Label.from_parsing)

        op_code_field = Word(alphas).setResultsName('op_code').setParseAction(AssemblyInstruction.parse_opcode)

        operand_field = Word(alphanums+'#%$(),_').setResultsName('operand').setParseAction(SunPlus6502Assembler.parse_operand_field)

        comment_filed = Group(Suppress(Literal(';')) + restOfLine()).setResultsName('comment').setParseAction(Comment.from_parsing)

        include_instruction = Group(Suppress(CaselessKeyword('Include')) + Word(alphanums+'_.') + Optional(comment_filed)).setParseAction(PreInst_Include.from_parsing)

        assembly_instruction = Group(Optional(label_field) + op_code_field + Optional(operand_field) + Optional(comment_filed)).setParseAction(SunPlus6502Assembler.parse_op_code)

        label_only = Group(label_name + Suppress(Literal(':')) + LineEnd()).setResultsName('label').setParseAction(Label.from_parsing)
        comment_line = Group(Suppress(Literal(';')) + restOfLine()).setResultsName('comment').setParseAction(Comment.from_parsing)

        self.grammar = Or(include_instruction | assembly_instruction | label_only | comment_line)
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
                        instr, = self.grammar.parseString(line)

                except ParseException as pe:
                    self.logger.error('parsing faild on line "%s"', line)
                    self.logger.debug('Parse Error: %s', pe)
                    return None

                if instr is not None:
                    if isinstance(instr, PreInst_Include):
                        self.logger.debug('Include statement for file: %s', instr.get_filename())
                        # TODO check if this file was already parsed to make shure we dont run into a infinite loop
                        include_instr = self.parse_file(instr.get_filename())
                        instructions.extend(include_instr)
                    elif isinstance(instr, AssemblyInstruction):
                        # if there was an label infront of the instruction we add them as seperate instructions
                        if instr.get_label() is not None:
                            instructions.append(instr.get_label())
                        instructions.append(instr)
                    elif isinstance(instr, Comment):
                        # comments are ignored
                        pass
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
        if 'label' in token[0]:
            label = token[0]['label']
        else:
            label = None

        op_code = token[0]['op_code']
        if 'operand' in token[0]:
            operand = token[0]['operand']
        else:
            operand = None
        if op_code is AssemblyInstruction.INSTRUCTION_ADC:
            return Inst_ADC(label, operand)
        elif op_code is AssemblyInstruction.INSTRUCTION_AND:
            return Inst_AND(label, operand)
        elif op_code is AssemblyInstruction.INSTRUCTION_ASL:
            return Inst_ASL(label, operand)
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
            return Inst_CLC(label)
        elif op_code is AssemblyInstruction.INSTRUCTION_CLD:
            return Inst_CLD(label)
        elif op_code is AssemblyInstruction.INSTRUCTION_CLI:
            return Inst_CLI(label)
        elif op_code is AssemblyInstruction.INSTRUCTION_CLR:
            raise NotImplementedError() #TODO
        elif op_code is AssemblyInstruction.INSTRUCTION_CLV:
            return Inst_CLV(label)
        elif op_code is AssemblyInstruction.INSTRUCTION_CMP:
            raise NotImplementedError() #TODO
        elif op_code is AssemblyInstruction.INSTRUCTION_CPX:
            raise NotImplementedError() #TODO
        elif op_code is AssemblyInstruction.INSTRUCTION_CPY:
            raise NotImplementedError() #TODO
        elif op_code is AssemblyInstruction.INSTRUCTION_DEC:
            raise NotImplementedError() #TODO
        elif op_code is AssemblyInstruction.INSTRUCTION_DEX:
            return Inst_DEX(label)
        elif op_code is AssemblyInstruction.INSTRUCTION_DEY:
            return Inst_DEY(label)
        elif op_code is AssemblyInstruction.INSTRUCTION_EOR:
            raise NotImplementedError() #TODO
        elif op_code is AssemblyInstruction.INSTRUCTION_INC:
            raise NotImplementedError() #TODO
        elif op_code is AssemblyInstruction.INSTRUCTION_INX:
            return Inst_INX(label)
        elif op_code is AssemblyInstruction.INSTRUCTION_INY:
            return Inst_INY(label)
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
            return Inst_NOP(label)
        elif op_code is AssemblyInstruction.INSTRUCTION_ORA:
            raise NotImplementedError() #TODO
        elif op_code is AssemblyInstruction.INSTRUCTION_PHA:
            return Inst_PHA(label)
        elif op_code is AssemblyInstruction.INSTRUCTION_PHP:
            return Inst_PHP(label)
        elif op_code is AssemblyInstruction.INSTRUCTION_PLA:
            return Inst_PLA(label)
        elif op_code is AssemblyInstruction.INSTRUCTION_PLP:
            return Inst_PLP(label)
        elif op_code is AssemblyInstruction.INSTRUCTION_ROL:
            raise NotImplementedError() #TODO
        elif op_code is AssemblyInstruction.INSTRUCTION_ROR:
            raise NotImplementedError() #TODO
        elif op_code is AssemblyInstruction.INSTRUCTION_RTI:
            return Inst_RTI(label)
        elif op_code is AssemblyInstruction.INSTRUCTION_RTS:
            return Inst_RTS(label)
        elif op_code is AssemblyInstruction.INSTRUCTION_SBC:
            raise NotImplementedError() #TODO
        elif op_code is AssemblyInstruction.INSTRUCTION_SEC:
            return Inst_SEC(label)
        elif op_code is AssemblyInstruction.INSTRUCTION_SED:
            return Inst_SED(label)
        elif op_code is AssemblyInstruction.INSTRUCTION_SEI:
            return Inst_SEI(label)
        elif op_code is AssemblyInstruction.INSTRUCTION_SET:
            raise NotImplementedError() #TODO
        elif op_code is AssemblyInstruction.INSTRUCTION_STA:
            raise NotImplementedError() #TODO
        elif op_code is AssemblyInstruction.INSTRUCTION_STX:
            raise NotImplementedError() #TODO
        elif op_code is AssemblyInstruction.INSTRUCTION_STY:
            raise NotImplementedError() #TODO
        elif op_code is AssemblyInstruction.INSTRUCTION_TAX:
            return Inst_TAX(label)
        elif op_code is AssemblyInstruction.INSTRUCTION_TAY:
            return Inst_TAY(label)
        elif op_code is AssemblyInstruction.INSTRUCTION_TST:
            raise NotImplementedError() #TODO
        elif op_code is AssemblyInstruction.INSTRUCTION_TSX:
            return Inst_TSX(label)
        elif op_code is AssemblyInstruction.INSTRUCTION_TXA:
            return Inst_TXA(label)
        elif op_code is AssemblyInstruction.INSTRUCTION_TXS:
            return Inst_TXS(label)
        elif op_code is AssemblyInstruction.INSTRUCTION_TYA:
            return Inst_TYA(label)
        elif 'include' in op_code:
            return PreInst_Include(operand.get_value())
        else:
            print(token.dump())
            raise NotImplementedError('unknown op code %s'%op_code)

    def check_labels(self, instructions):
        '''check list of instructions for dublicates and missing labels'''
        known_label = list()
        for instr in instructions:
            if isinstance(instr, Label):
                if instr.get_name() in known_label:
                    self.logger.error('multible definitions for label %s', instr.get_name())
                    raise Exception('multible definitions for label %s', instr.get_name())
                else:
                    known_label.append(instr.get_name())
        self.logger.info('found %d label definitions', len(known_label))

        for instr in instructions:
            if isinstance(instr, AssemblyInstruction):
                operand = instr.get_operand()
                if isinstance(operand, AddressValue) and operand.get_type() is AddressValue.TYPE_LABEL:
                    label_name = operand.get_value()
                    if label_name not in known_label:
                        self.logger.error('label %s used but not defined', label_name)
                        raise Exception('label %s used but not defined', label_name)
        self.logger.info('all used labels found in definition')

    def calculate_lable_pos(self, instructions):
        '''this is where each label definition gets assigned its label'''
        addr = 0x00
        label_addr = dict()
        for instr in instructions:
            if isinstance(instr, Label):
                label_addr[instr.get_name()] = addr
                self.logger.debug("{:s}@{:04X}".format(instr.get_name(), addr))
            elif isinstance(instr, AssemblyInstruction):
                addr += instr.get_cycles()
            else:
                self.logger.error('unknow type encountered {:s}'.format(instr))
                raise Exception('unknow type encountered {:s}'.format(instr))
        self.logger.info('assigned {:d} labels, program length is {:04X}'.format(len(label_addr), addr))
        return label_addr

    def replace_label(self, instructions, label_addr_map):
        for instr in instructions:
            if isinstance(instr, AssemblyInstruction):
                operand = instr.get_operand()
                if isinstance(operand, AddressValue) and operand.get_type() is AddressValue.TYPE_LABEL:
                    label_name = operand.get_value()
                    if label_name not in label_addr_map:
                        self.logger.error('label {:s} used but not defined'.format(label_name))
                        raise Exception('label {:s} used but not defined'.format(label_name))
                    else:
                        self.logger.info('replace labele {:s} in instruction {:02X}h with address {:04X}h used but not defined'.format(label_name, instr.get_opcode(), label_addr_map[label_name]))
                        instr.replace_label(label_addr_map[label_name])


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
