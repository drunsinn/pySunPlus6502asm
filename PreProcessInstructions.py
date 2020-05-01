#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: drunsinn
@license: MIT License
"""
import logging

class PreInst_Include(object):
    def __init__(self, filename):
        self.__filename = str(filename)
    def get_filename(self):
        return self.__filename
    @staticmethod
    def from_parsing(token):
        return PreInst_Include(token[0][0])
