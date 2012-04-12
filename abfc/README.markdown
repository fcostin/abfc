abfc
====

+   `compile_macro.py` : top-level script for using the macro-language compiler
+   `codegen.py` : code generation backend for the "brainfuck machine".
+   `compile.py` : compiles simplified macro-language expressions to brainfuck
+   `expr.py` : simplifies macro-language expressions using a collection
        of expression rewrite rules
+   `pattern_match.py` : an incredibly ugly implementation of pattern matching
        and destructuring, used for processing macro-language expressions
+   `sugar.py` : syntactic sugar for macro-language constructs
+   `prelude.py` : imported at the beginning of macro-language source files
+   `arch/` : GNU assembler syntax literals for machine code generation
+   `bootstrap_bf.py` : a stand-alone brainfuck to GNU assembler syntax compiler.
    Generates code from the literals inside `arch/`
