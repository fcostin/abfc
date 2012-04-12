"""
A brainfuck to GNU assembler compiler, implemented
as a python macro-language dsl.

To compile this source to brainfuck opcodes, run this file via

    python --arch abfc/compile_macro.py self_hosting_bf_compiler.py

where arch is e.g. ia32 or x86_64
"""

# ====================
# A BRAINFUCK COMPILER
# ====================
#   featuring:
#       *   support for up to 0x10000 loops
#       *   run-length encoding for repeated
#           strings of +,-,<,> instructions


# ================================
# IMPORT ASSEMBLY STRING CONSTANTS
# ================================

# ===========
# MATH MACROS
# ===========

# compute quotient of x div y
#   -- xxx todo make this less awful
DEF_MACRO('div_q', 'x', 'y', 'q')(
    LOCAL('r'),
    CLEAR('q'),
    COPY('x', 'r'),
    LOCAL('t'),
    AS_LOGICAL('r', 't'),
    WHILE('t')(
        LOCAL('i'),
        COPY('y', 'i'),
        LOCAL('t2'),
        LOGICAL_AND('i', 't', 't2'),
        WHILE('t2')(
            CONSTANT_SUB(INT_CONSTANT(1), 'i'),
            CONSTANT_SUB(INT_CONSTANT(1), 'r'),
            AS_LOGICAL('r', 't'),
            LOGICAL_AND('i', 't', 't2'),
        ),
        LOCAL('t3'),
        LOGICAL_NOT('i', 't3'),
        IF('t3')(
            CONSTANT_ADD(INT_CONSTANT(1), 'q'),
        ),
        # else break outer loop
        LOCAL('t4'),
        LOGICAL_NOT('t3', 't4'),
        IF('t4')(
            CLEAR('t'),
        )
    )
)

# compute remainder of x div y, given quotient q
DEF_MACRO('div_r', 'x', 'y', 'q', 'r')(
    COPY('x', 'r'),
    LOCAL('i'),
    COPY('q', 'i'),
    WHILE('i')(
        STACK_SUB('y', 'r'),
        CONSTANT_SUB(INT_CONSTANT(1), 'i'),
    ),
)

# compute quotient and remainder of x div y
DEF_MACRO('div', 'x', 'y', 'q', 'r')(
    CALL('div_q', 'x', 'y', 'q'),
    CALL('div_r', 'x', 'y', 'q', 'r'),
)

# =============
# OUTPUT MACROS
# =============

# print hex digit x, 0 <= x < 16
DEF_MACRO('print_hex_digit', 'x')(
    LOCAL('y'),
    CLEAR('y'),
    CONSTANT_ADD(INT_CONSTANT(10),'y'),
    LOCAL('q'),
    LOCAL('r'),
    CALL('div', 'x', 'y','q','r'),
    IF('q')(
        CONSTANT_ADD(CHAR_CONSTANT('a'), 'r'),
    ),
    LOCAL('not_q'),
    LOGICAL_NOT('q', 'not_q'),
    IF('not_q')(
        CONSTANT_ADD(CHAR_CONSTANT('0'), 'r'),
    ),
    PUT_CHAR('r'),
)

DEF_MACRO('print_hex_byte', 'x')(
    LOCAL('y'),
    CLEAR('y'),
    CONSTANT_ADD(INT_CONSTANT(16),'y'),
    LOCAL('q'),
    LOCAL('r'),
    CALL('div', 'x', 'y','q','r'),
    CALL('print_hex_digit', 'q'),
    CALL('print_hex_digit', 'r'),
)

# ==============
# COUNTER MACROS
# ==============
# these are used to manage the 2-byte counter
# used to uniquely name labels

DEF_MACRO('counter_init', 'x0', 'x1')(
   CLEAR('x0'),
   CLEAR('x1'),
)

DEF_MACRO('counter_inc', 'x0', 'x1')(
    CONSTANT_ADD(INT_CONSTANT(1), 'x0'),
    LOCAL('test'),
    LOGICAL_NOT('x0', 'test'),
    IF('test')(
        CLEAR('x0'),
        CONSTANT_ADD(INT_CONSTANT(1), 'x1'),
    )
)

DEF_MACRO('counter_print', 'x0', 'x1')(
    CALL('print_hex_byte', 'x1'),
    CALL('print_hex_byte', 'x0'),
)

# ============
# INPUT MACROS
# ============
# run-length encoding of input
# known bugs:
#   1 byte used for the counter n with no guard against overflow

DEF_MACRO('input_init', 'n', 'c', 'c_next')(
    CLEAR('c'),
    CLEAR('n'),
    CLEAR('c_next'),
    GET_CHAR('c_next'),
    CALL('input_update', 'n', 'c', 'c_next'),
)

DEF_MACRO('input_update', 'n', 'c', 'c_next')(
    # while n is zero or c_next == c, accumulate n
    LOCAL('n_is_zero'),
    LOGICAL_NOT('n', 'n_is_zero'),
    LOCAL('not_match'),
    COPY('c_next', 'not_match'),
    STACK_SUB('c', 'not_match'),
    LOCAL('match'),
    LOGICAL_NOT('not_match', 'match'),
    LOCAL('merge_ok'),
    LOGICAL_OR('n_is_zero', 'match', 'merge_ok'),
    WHILE('merge_ok')(
        COPY('c_next', 'c'),
        CONSTANT_ADD(INT_CONSTANT(1), 'n'),
        CLEAR('merge_ok'),
        # but stop if c_next is zero (EOF)
        IF('c_next')(
            CLEAR('c_next'),
            GET_CHAR('c_next'),
            COPY('c_next', 'not_match'),
            STACK_SUB('c', 'not_match'),
            # we know n isnt zero any more!
            LOGICAL_NOT('not_match', 'merge_ok'),
        ),
    ),
)

DEF_MACRO('input_has_next', 'n', 'c', 'c_next', 'result_has_next')(
    COPY('c', 'result_has_next'),
)

DEF_MACRO('input_peek_char', 'n', 'c', 'c_next', 'result_c')(
    COPY('c', 'result_c'),
)

DEF_MACRO('input_consume_char', 'n', 'c', 'c_next')(
    CONSTANT_SUB(INT_CONSTANT(1), 'n'),
)

DEF_MACRO('input_consume_run', 'n', 'c', 'c_next', 'result_n')(
    COPY('n', 'result_n'),
    CLEAR('n'),
)

# ===========
# MISC MACROS
# ===========

DEF_MACRO('is_equal', 'const', 'src', 'dst')(
    LOCAL('temp'),
    COPY('src', 'temp'),
    CONSTANT_SUB('const', 'temp'),
    LOGICAL_NOT('temp', 'dst'),
)

# ===================
# MAIN COMPILER MACRO
# ===================

DEF_MACRO('main')(
    # initialise name counter state
    LOCAL('name_counter_0'),
    LOCAL('name_counter_1'),
    CALL('counter_init', 'name_counter_0', 'name_counter_1'),
    # initialise input state
    LOCAL('input0'),
    LOCAL('input1'),
    LOCAL('input2'),
    CALL('input_init', 'input0', 'input1', 'input2'),
    LOCAL('input_ok'),
    CALL('input_has_next', 'input0', 'input1', 'input2', 'input_ok'),
    PUT_STRING_CONSTANT(STRING_CONSTANT(arch.PROGRAM_START)),
    LOCAL('match'),
    LOCAL('no_match_found'),
    LOCAL('c'),
    WHILE('input_ok')(
        CLEAR('no_match_found'),
        CONSTANT_ADD(INT_CONSTANT(1), 'no_match_found'),
        CALL('input_peek_char', 'input0', 'input1', 'input2', 'c'),
        CALL('is_equal', CHAR_CONSTANT('+'), 'c', 'match'), 
        IF('match')(
            LOCAL('run_length'),
            CALL('input_consume_run', 'input0', 'input1', 'input2', 'run_length'),
            PUT_STRING_CONSTANT(STRING_CONSTANT(arch.DP_INC_1)),
            CALL('print_hex_byte', 'run_length'),
            PUT_STRING_CONSTANT(STRING_CONSTANT(arch.DP_INC_2)),
            CLEAR('no_match_found'),
        ),
        CALL('is_equal', CHAR_CONSTANT('-'), 'c', 'match'), 
        IF('match')(
            LOCAL('run_length'),
            CALL('input_consume_run', 'input0', 'input1', 'input2', 'run_length'),
            PUT_STRING_CONSTANT(STRING_CONSTANT(arch.DP_DEC_1)),
            CALL('print_hex_byte', 'run_length'),
            PUT_STRING_CONSTANT(STRING_CONSTANT(arch.DP_DEC_2)),
            CLEAR('no_match_found'),
        ),
        CALL('is_equal', CHAR_CONSTANT('<'), 'c', 'match'), 
        IF('match')(
            LOCAL('run_length'),
            CALL('input_consume_run', 'input0', 'input1', 'input2', 'run_length'),
            PUT_STRING_CONSTANT(STRING_CONSTANT(arch.DP_LEFT_1)),
            CALL('print_hex_byte', 'run_length'),
            PUT_STRING_CONSTANT(STRING_CONSTANT(arch.DP_LEFT_2)),
            CLEAR('no_match_found'),
        ),
        CALL('is_equal', CHAR_CONSTANT('>'), 'c', 'match'), 
        IF('match')(
            LOCAL('run_length'),
            CALL('input_consume_run', 'input0', 'input1', 'input2', 'run_length'),
            PUT_STRING_CONSTANT(STRING_CONSTANT(arch.DP_RIGHT_1)),
            CALL('print_hex_byte', 'run_length'),
            PUT_STRING_CONSTANT(STRING_CONSTANT(arch.DP_RIGHT_2)),
            CLEAR('no_match_found'),
        ),
        CALL('is_equal', CHAR_CONSTANT('['), 'c', 'match'), 
        IF('match')(
            CALL('input_consume_char', 'input0', 'input1', 'input2'),
            PUT_STRING_CONSTANT(STRING_CONSTANT(arch.BEGIN_WHILE_1)),
            CALL('counter_print', 'name_counter_0', 'name_counter_1'),
            PUT_STRING_CONSTANT(STRING_CONSTANT(arch.BEGIN_WHILE_2)),
            CALL('counter_print', 'name_counter_0', 'name_counter_1'),
            PUT_STRING_CONSTANT(STRING_CONSTANT(arch.BEGIN_WHILE_3)),
            GROW_STACK(INT_CONSTANT(2)),
            COPY('name_counter_0', STACK_ADDRESS(-2)),
            COPY('name_counter_1', STACK_ADDRESS(-1)),
            CALL('counter_inc', 'name_counter_0', 'name_counter_1'),
            CLEAR('no_match_found'),
        ),
        CALL('is_equal', CHAR_CONSTANT(']'), 'c', 'match'), 
        IF('match')(
            CALL('input_consume_char', 'input0', 'input1', 'input2'),
            PUT_STRING_CONSTANT(STRING_CONSTANT(arch.END_WHILE_1)),
            CALL('counter_print', STACK_ADDRESS(-2), STACK_ADDRESS(-1)),
            PUT_STRING_CONSTANT(STRING_CONSTANT(arch.END_WHILE_2)),
            CALL('counter_print', STACK_ADDRESS(-2), STACK_ADDRESS(-1)),
            PUT_STRING_CONSTANT(STRING_CONSTANT(arch.END_WHILE_3)),
            SHRINK_STACK(INT_CONSTANT(2)),
            CLEAR('no_match_found'),
        ),
        CALL('is_equal', CHAR_CONSTANT(','), 'c', 'match'), 
        IF('match')(
            CALL('input_consume_char', 'input0', 'input1', 'input2'),
            PUT_STRING_CONSTANT(STRING_CONSTANT(arch.READ_CHAR)),
            CLEAR('no_match_found'),
        ),
        CALL('is_equal', CHAR_CONSTANT('.'), 'c', 'match'), 
        IF('match')(
            CALL('input_consume_char', 'input0', 'input1', 'input2'),
            PUT_STRING_CONSTANT(STRING_CONSTANT(arch.WRITE_CHAR)),
            CLEAR('no_match_found'),
        ),
        IF('no_match_found')(
            # ignore unmatchable input characters
            CALL('input_consume_char', 'input0', 'input1', 'input2'),
        ),
        CALL('input_update', 'input0', 'input1', 'input2'),
        CALL('input_has_next', 'input0', 'input1', 'input2', 'input_ok'),
    ),
    PUT_STRING_CONSTANT(STRING_CONSTANT(arch.PROGRAM_END)),
)
