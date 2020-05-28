#!/usr/bin/env python

'''
Author :
    * Muhammed Ahad <ahad3112@yahoo.com, maaahad@gmail.com>

Usage:
    $ python3 generate_specifications_file.py -h/--help
'''

import hpccm

import argparse
from utilities.cli import CLI
import container.recipes as recipes

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='HPCCM recipes for GROMACS container')
    cli = CLI(parser=parser)

    hpccm.config.set_container_format(cli.args.format)

    recipes.prepare_and_cook(args=cli.args)
