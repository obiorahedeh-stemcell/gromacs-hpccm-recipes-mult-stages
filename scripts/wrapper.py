#!/usr/bin/env python3

'''
Author :
    * Muhammed Ahad <ahad3112@yahoo.com, maaahad@gmail.com>

Usage:
    $ python3 generate_specifications_file.py -h/--help
'''

import sys
import os

os.system('gmx_chooser.py ' + ' '.join(sys.argv))
