#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: drunsinn
@license: MIT License
"""
import logging

class PreInst_Include(object):
    def __init__(self, filename):
        self.__filename = filename
    def get_filename(self):
        return self.__filename
