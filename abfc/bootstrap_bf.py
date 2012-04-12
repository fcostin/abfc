"""
a brainfuck to gnu assembler compiler
run with no arguments to see usage
output of compiler is printed to stdout
"""

import sys
import itertools
from arch import KNOWN_ARCHS, load_arch

def die(s):
    sys.stderr.write(s + '\n')
    sys.exit(1)

def emit(s):
    sys.stdout.write(s)

def compile_for_arch(arch, s):
    unique_labels = itertools.count()
    label_stack = []

    def begin_while():
        i = next(unique_labels)
        label_stack.append(i)
        return (arch.BEGIN_WHILE_1 + ('%04x' % i) +
            arch.BEGIN_WHILE_2 + ('%04x' % i) +
            arch.BEGIN_WHILE_3)

    def end_while():
        if not label_stack:
            die('error: encountered "]" without matching "["')
        i = label_stack.pop()
        return (arch.END_WHILE_1 + ('%04x' % i) +
            arch.END_WHILE_2 + ('%04x' % i) +
            arch.END_WHILE_3)

    code_generator = {
        '<' : lambda : arch.DP_LEFT,
        '>' : lambda : arch.DP_RIGHT,
        '+' : lambda : arch.DP_INC,
        '-' : lambda : arch.DP_DEC,
        '[' : begin_while,
        ']' : end_while,
        '.' : lambda : arch.WRITE_CHAR,
        ',' : lambda : arch.READ_CHAR,
    }
    emit(arch.PROGRAM_START)
    for c in s:
        if c in code_generator:
            emit(code_generator[c]())
        else:
            pass # ignore unrecognised characters
    emit(arch.PROGRAM_END)

def print_usage_and_die():
    usage_hint = 'usage: [%s] input.bf' % ('|'.join(sorted(KNOWN_ARCHS)))
    die(usage_hint)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print_usage_and_die()
    if sys.argv[1] not in KNOWN_ARCHS:
        print_usage_and_die()

    arch = load_arch(sys.argv[1])
    
    with open(sys.argv[2], 'r') as source_file:
        s = '\n'.join(source_file.readlines())

    compile_for_arch(arch, s)

