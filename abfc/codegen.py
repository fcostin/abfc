def make_stack_address(offset):
    return ('stack_address', offset)

def is_stack_address(x):
    try:
        x = tuple(x)
        assert len(x) == 2
        assert x[0] == 'stack_address'
        offset = int(x[1])
    except Exception:
        return False
    return True

def match_stack_address(x):
    assert is_stack_address(x)
    return x[1]

def assert_no_aliasing(*args):
    offsets = list(map(match_stack_address, args))
    assert len(offsets) == len(list(set(offsets)))

def make_constant(x):
    return ('int_constant', int(x))

def is_constant(x):
    try:
        x = tuple(x)
        assert len(x) == 2
        assert x[0] == 'int_constant'
        const = int(x[1])
    except Exception:
        return False
    return True

def match_constant(x):
    assert is_constant(x)
    return x[1]

def make_string_constant(x):
    return ('string_constant', str(x))

def is_string_constant(x):
    try:
        x = tuple(x)
        assert len(x) == 2
        assert x[0] == 'string_constant'
        const = str(x[1])
    except Exception:
        return False
    return True

def match_string_constant(x):
    assert is_string_constant(x)
    return x[1]

class Machine:
    def __init__(self, n_cells):
        self.n_cells = n_cells
        self.bf_ptr = 0
        self.stack_ptr = 0
        self.code = []
        self.loop_stack = []

    def validate(self):
        assert 0 <= self.bf_ptr < self.n_cells

    def get_bf_ptr_relative_to_stack(self):
        return self.bf_ptr - self.stack_ptr

    def do_move(self, offset):
        if offset == 0:
            pass
        elif offset > 0:
            self.code.append('>' * offset)
        else:
            self.code.append('<' * (-offset))
        self.bf_ptr += offset
        self.validate()

    def do_move_to_stack_address(self, stack_address):
        stack_offset = match_stack_address(stack_address)
        dst_ptr = self.stack_ptr + stack_offset
        offset = dst_ptr - self.bf_ptr
        self.do_move(offset)

    def do_left(self):
        self.do_move(-1)

    def do_right(self):
        self.do_move(1)

    def do_inc(self, n = 1):
        assert n >= 0
        if n > 0:
            self.code.append('+' * n)
        self.validate()

    def do_dec(self, n = 1):
        assert n >= 0
        if n > 0:
            self.code.append('-' * n)
        self.validate()

    def do_begin_loop(self):
        self.code.append('[')
        self.loop_stack.append(self.get_bf_ptr_relative_to_stack())
        self.validate()

    def do_end_loop(self):
        self.code.append(']')
        # invariant : bf_ptr must have the same value
        # after [x] for all executation paths
        assert self.loop_stack.pop() == self.get_bf_ptr_relative_to_stack()
        self.validate()

    def do_read(self):
        self.code.append(',')
        self.validate()

    def do_write(self):
        self.code.append('.')
        self.validate()

    def do_unvalidated_bf(self, bf_opcodes):
        known_opcodes = '<>+-[].,'
        for c in bf_opcodes:
            assert c in known_opcodes
        self.code.append(bf_opcodes)

    def dump_code(self):
        print(''.join(self.code))

_BUILT_IN_MACROS = {}

def _invoke_macro(machine, stack_man, macro_name, *args):
    if macro_name not in _BUILT_IN_MACROS:
        raise KeyError('unknown builtin macro : %s' % repr(macro_name))
    _BUILT_IN_MACROS[macro_name](machine, stack_man, *args)

def BUILT_IN_MACRO(f):
    _BUILT_IN_MACROS[f.__name__] = f
    return f

@BUILT_IN_MACRO
def clear(machine, stack_man, dst):
    machine.do_move_to_stack_address(dst)
    machine.do_begin_loop()
    machine.do_dec()
    machine.do_end_loop()

@BUILT_IN_MACRO
def destructive_add(machine, stack_man, src, dst):
    assert_no_aliasing(src, dst)
    machine.do_move_to_stack_address(src)
    machine.do_begin_loop()
    machine.do_dec()
    machine.do_move_to_stack_address(dst)
    machine.do_inc()
    machine.do_move_to_stack_address(src)
    machine.do_end_loop()

@BUILT_IN_MACRO
def destructive_sub(machine, stack_man, src, dst):
    assert_no_aliasing(src, dst)
    machine.do_move_to_stack_address(src)
    machine.do_begin_loop()
    machine.do_dec()
    machine.do_move_to_stack_address(dst)
    machine.do_dec()
    machine.do_move_to_stack_address(src)
    machine.do_end_loop()

@BUILT_IN_MACRO
def move(machine, stack_man, src, dst):
    _invoke_macro(machine, stack_man, 'clear', dst)
    _invoke_macro(machine, stack_man, 'destructive_add', src, dst)

@BUILT_IN_MACRO
def copy(machine, stack_man, src, dst):
    _tmp0 = stack_man.allocate_local()
    assert_no_aliasing(src, dst, _tmp0)
    _invoke_macro(machine, stack_man, 'clear', dst)
    _invoke_macro(machine, stack_man, 'clear', _tmp0)
    machine.do_move_to_stack_address(src)
    machine.do_begin_loop()
    machine.do_dec()
    machine.do_move_to_stack_address(dst)
    machine.do_inc()
    machine.do_move_to_stack_address(_tmp0)
    machine.do_inc()
    machine.do_move_to_stack_address(src)
    machine.do_end_loop()
    _invoke_macro(machine, stack_man, 'destructive_add', _tmp0, src)
    stack_man.free_local(_tmp0)

@BUILT_IN_MACRO
def stack_add(machine, stack_man, src, dst):
    _tmp0 = stack_man.allocate_local()
    _invoke_macro(machine, stack_man, 'copy', src, _tmp0)
    _invoke_macro(machine, stack_man, 'destructive_add', _tmp0, dst)
    stack_man.free_local(_tmp0)

@BUILT_IN_MACRO
def constant_add(machine, stack_man, src, dst):
    a = match_constant(src)
    machine.do_move_to_stack_address(dst)
    machine.do_inc(a)

@BUILT_IN_MACRO
def stack_sub(machine, stack_man, src, dst):
    _tmp0 = stack_man.allocate_local()
    _invoke_macro(machine, stack_man, 'copy', src, _tmp0)
    _invoke_macro(machine, stack_man, 'destructive_sub', _tmp0, dst)
    stack_man.free_local(_tmp0)

@BUILT_IN_MACRO
def constant_sub(machine, stack_man, src, dst):
    a = match_constant(src)
    machine.do_move_to_stack_address(dst)
    machine.do_dec(a)

@BUILT_IN_MACRO
def as_logical(machine, stack_man, src, dst):
    _tmp0 = stack_man.allocate_local()
    assert_no_aliasing(src, dst, _tmp0)
    _invoke_macro(machine, stack_man, 'copy', src, _tmp0)
    _invoke_macro(machine, stack_man, 'clear', dst)
    machine.do_move_to_stack_address(_tmp0)
    machine.do_begin_loop()
    machine.do_move_to_stack_address(dst)
    machine.do_inc()
    _invoke_macro(machine, stack_man, 'clear', _tmp0)
    machine.do_end_loop()
    stack_man.free_local(_tmp0)

@BUILT_IN_MACRO
def logical_not(machine, stack_man, src, dst):
    _tmp0 = stack_man.allocate_local()
    assert_no_aliasing(src, dst, _tmp0)
    _invoke_macro(machine, stack_man, 'copy', src, _tmp0)
    _invoke_macro(machine, stack_man, 'clear', dst)
    machine.do_move_to_stack_address(dst)
    machine.do_inc()
    machine.do_move_to_stack_address(_tmp0)
    machine.do_begin_loop()
    machine.do_move_to_stack_address(dst)
    machine.do_dec()
    _invoke_macro(machine, stack_man, 'clear', _tmp0)
    machine.do_end_loop()
    stack_man.free_local(_tmp0)

@BUILT_IN_MACRO
def logical_or(machine, stack_man, src_a, src_b, dst):
    # much stuffing about to ensure we leave src_a, src_b untouched
    # but we operate on their 'as_logical' values
    _tmp0 = stack_man.allocate_local()
    _invoke_macro(machine, stack_man, 'clear', dst)
    _invoke_macro(machine, stack_man, 'as_logical', src_a, _tmp0)
    _invoke_macro(machine, stack_man, 'stack_add', _tmp0, dst)
    _invoke_macro(machine, stack_man, 'as_logical', src_b, _tmp0)
    _invoke_macro(machine, stack_man, 'stack_add', _tmp0, dst)
    _invoke_macro(machine, stack_man, 'as_logical', dst, _tmp0)
    _invoke_macro(machine, stack_man, 'move', _tmp0, dst)
    stack_man.free_local(_tmp0)

@BUILT_IN_MACRO
def logical_and(machine, stack_man, src_a, src_b, dst):
    _tmp0 = stack_man.allocate_local()
    _invoke_macro(machine, stack_man, 'clear', dst)
    _invoke_macro(machine, stack_man, 'logical_not', src_a, _tmp0)
    _invoke_macro(machine, stack_man, 'stack_add', _tmp0, dst)
    _invoke_macro(machine, stack_man, 'logical_not', src_b, _tmp0)
    _invoke_macro(machine, stack_man, 'stack_add', _tmp0, dst)
    _invoke_macro(machine, stack_man, 'logical_not', dst, _tmp0)
    _invoke_macro(machine, stack_man, 'move', _tmp0, dst)
    stack_man.free_local(_tmp0)

@BUILT_IN_MACRO
def get_char(machine, stack_man, dst):
    machine.do_move_to_stack_address(dst)
    machine.do_read()

@BUILT_IN_MACRO
def put_char(machine, stack_man, dst):
    machine.do_move_to_stack_address(dst)
    machine.do_write()

@BUILT_IN_MACRO
def put_string_constant(machine, stack_man, string_constant):
    s = match_string_constant(string_constant)
    _tmp0 = stack_man.allocate_local()
    _invoke_macro(machine, stack_man, 'clear', _tmp0)
    chars = list(map(ord, s))
    current_char = 0
    for c in chars:
        delta_char = c - current_char
        if delta_char > 0:
            machine.do_inc(delta_char)
        elif delta_char == 0:
            pass
        elif delta_char < 0:
            machine.do_dec(-delta_char)
        machine.do_write()
        current_char = c
    stack_man.free_local(_tmp0)

@BUILT_IN_MACRO
def begin_loop(machine, stack_man, src):
    machine.do_move_to_stack_address(src)
    machine.do_begin_loop()

@BUILT_IN_MACRO
def end_loop(machine, stack_man, src):
    machine.do_move_to_stack_address(src)
    machine.do_end_loop()

@BUILT_IN_MACRO
def grow_stack(machine, stack_man, size):
    n = match_constant(size)
    assert n >= 0
    if n == 0:
        return
    offsets = stack_man.allocated_cells()
    for x in reversed(offsets):
        src = make_stack_address(x)
        dst = make_stack_address(x + n)
        _invoke_macro(machine, stack_man, 'move', src, dst)
    for x in range(n):
        src = make_stack_address(x)
        _invoke_macro(machine, stack_man, 'clear', src)
    machine.stack_ptr += n

@BUILT_IN_MACRO
def shrink_stack(machine, stack_man, size):
    n = match_constant(size)
    assert n >= 0
    if n == 0:
        return
    offsets = stack_man.allocated_cells()
    for x in offsets:
        src = make_stack_address(x)
        dst = make_stack_address(x - n)
        _invoke_macro(machine, stack_man, 'move', src, dst)
    machine.stack_ptr -= n
