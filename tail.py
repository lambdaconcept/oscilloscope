#!/usr/bin/env python
# 2021 - LambdaConcept - po@lambdaconcept.com

import os
import sys
import time

class Tail():
    def __init__(self, fname):
        self.fname = fname
        self.open()

    def open(self):
        self.file = open(self.fname)
        # Go to the end of file
        self.file.seek(0, 2)

    def readall(self):
        # Go to the beginning
        self.file.seek(0, 0)
        return self.file.readlines()

    def fetch(self):
        pos = self.file.tell()
        line = self.file.readline()
        if line is None:
            self.file.seek(pos)
        else:
            return line
