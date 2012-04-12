from sugar import *

_USER_MACROS = {}

def DEF_MACRO(name, *params):
    def _capture_macro_body(*body):
        macro = MACRO(name, *params)(*body)
        _USER_MACROS[name] = macro
    return _capture_macro_body

def test_compile():
    import expr
    main_macro = expr.compile_macro(_USER_MACROS, 'main')
    import compile
    import codegen
    compile.compile_phase_2(codegen._BUILT_IN_MACROS, main_macro)
