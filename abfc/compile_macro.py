import sys
import importlib

from arch import KNOWN_ARCHS, load_arch

def print_usage_and_die():
    usage_hint = 'usage: [%s] input_macro.py' % ('|'.join(sorted(KNOWN_ARCHS)))
    sys.stderr.write(usage_hint + '\n')
    sys.exit(1)

def compile_macro_for_arch(arch, macro_code):
    COMPILER_FUNC_NAME = 'test_compile'
    # set up environment to run macro_code inside:
    #   1.  define a global variable 'arch' containing the code fragments for
    #       the selected architecture.
    #
    #   2.  find all of the attributes inside the prelude module which have
    #       NAMES_THAT_START_WITH_AN_UPPERCASE_LETTER and put those in the
    #       environment too. These are the macro definitions
    macro_globals = {'arch' : arch, }
    prelude = __import__('prelude')
    prelude_macro_names = [name for name in dir(prelude) if (name and name[0].isupper())]
    for name in prelude_macro_names:
        macro_globals[name] = getattr(prelude, name)
    # now, run the user-supplied macro code inside our environment. this should accumulate
    # the user macro definitions into some global variables in there somewhere.
    exec(macro_code, macro_globals, macro_globals)
    # finally, add the compiler function to the environment, and run that. output will
    # be written to stdout
    macro_globals[COMPILER_FUNC_NAME] = getattr(prelude, COMPILER_FUNC_NAME)
    exec('%s()' % COMPILER_FUNC_NAME, macro_globals, macro_globals)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print_usage_and_die()
    if sys.argv[1] not in KNOWN_ARCHS:
        print_usage_and_die()

    arch = load_arch(sys.argv[1])
    
    with open(sys.argv[2], 'r') as source_file:
        macro_code = '\n'.join(source_file.readlines())
    
    compile_macro_for_arch(arch, macro_code)

