"""
code fragments for brainfuck -> gnu assembly code generation
"""

from . import ia32
from . import x86_64

KNOWN_ARCHS = {
    '--ia32' : ia32,
    '--x86-64' : x86_64,
}

def load_arch(arch_module_name):
    return KNOWN_ARCHS[arch_module_name]
