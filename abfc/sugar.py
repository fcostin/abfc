import codegen

_BUILT_IN_MACROS = codegen._BUILT_IN_MACROS

def _make_built_in_macro_wrapper(name):
    def _wrapper(*args):
        return CALL_BUILTIN(name, *args)
    return _wrapper

def _register_built_in_macros():
    for name in sorted(_BUILT_IN_MACROS):
        wrapper_func = _make_built_in_macro_wrapper(name)
        wrapper_name = name.upper()
        globals()[wrapper_name] = wrapper_func

_register_built_in_macros()

def L(x):
    return ('literal', x)

def NAME(x):
    return ('name', L(x))

def LOCAL(x):
    return ('local', L(x))

def PARAMS(*params):
    return tuple(['parameters'] + list(map(L, params)))

def ARGS(*args):
    return tuple(['arguments'] + list(map(L, args)))

def CALL(name, *args):
    return ('call_macro', NAME(name), ARGS(*args))

def CALL_BUILTIN(name, *args):
    return ('call_builtin', NAME(name), ARGS(*args))

def BODY(*statements):
    return tuple(['body'] + list(statements))

def MACRO(name, *params):
    def _capture_user_macro_body(*body):
        return ('user_macro', NAME(name), PARAMS(*params), BODY(*body))
    return _capture_user_macro_body

def INT_CONSTANT(x):
    return ('int_constant', int(x))

def STRING_CONSTANT(x):
    return ('string_constant', str(x))

def CHAR_CONSTANT(x):
    return ('int_constant', ord(x))

def HIDDEN(x):
    # n.b. this shouldn't be used by the user
    return ('hidden', x)

def STACK_ADDRESS(x):
    return ('stack_address', x)

def WHILE(*args):
    def _capture_while_body(*body):
        return ('while', ARGS(*args), BODY(*body))
    return _capture_while_body

def IF(*args):
    def _capture_if_body(*body):
        return ('if', ARGS(*args), BODY(*body))
    return _capture_if_body
