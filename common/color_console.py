# -*- coding: utf-8 -*-

RED = '\033[31m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
BLUE = '\033[34m'
PURPLE = '\033[35m'
RESET = '\033[0m'


def print_red(*args, sep=' ', end='\n', file=None):
    args = [f'{RED}{s}{RESET}' for s in args]
    print(*args, sep=sep, end=end, file=file)


def print_blue(*args, sep=' ', end='\n', file=None):
    args = [f'{BLUE}{s}{RESET}' for s in args]
    print(*args, sep=sep, end=end, file=file)


def print_yellow(*args, sep=' ', end='\n', file=None):
    args = [f'{YELLOW}{s}{RESET}' for s in args]
    print(*args, sep=sep, end=end, file=file)


def print_green(*args, sep=' ', end='\n', file=None):
    args = [f'{GREEN}{s}{RESET}' for s in args]
    print(*args, sep=sep, end=end, file=file)


def print_purple(*args, sep=' ', end='\n', file=None):
    args = [f'{PURPLE}{s}{RESET}' for s in args]
    print(*args, sep=sep, end=end, file=file)