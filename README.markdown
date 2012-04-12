a[n awful] brainfuck compiler
=============================

Compiles brainfuck programs to `ia32` or `x86_64` backends, via the GNU assembler.

The brainfuck to GNU assembler compiler is itself written in brainfuck.

Since brainfuck is a somewhat difficult language to work with, we write the brainfuck
to GNU assembler compiler in a higher-level macro language, and then compile that
macro language down to brainfuck. This higher-level macro language is a DSL
implemented in Python, and is only higher-level relative to brainfuck.

Also included is a brainfuck to GNU assembler compiler written in Python, which
is used as part of the build pipeline.


walk-through of build pipeline
------------------------------

Here's what happens when we run `make`:

1.  First we run `abfc/compile_macro.py` to compile the macro-language file
    `macros/self_hosting_bf_compiler.py`. This generates the brainfuck source file
    `build/bf_compiler.brainfuck`, which contains the code for the brainfuck to
    GNU assembler compiler:

        python2 abfc/compile_macro.py --x86-64 macros/self_hosting_bf_compiler.py > build/bf_compiler.brainfuck

2.  We then compile the generated brainfuck source for the brainfuck compiler to GNU
    assembler syntax using a Python implementation of a simple brainfuck compiler, and
    compile the resulting `.s` file using `gcc`.
        
        python2 abfc/bootstrap_bf.py --x86-64 build/bf_compiler.brainfuck > build/bf_compiler_boot.s
        gcc build/bf_compiler_boot.s -nostdlib -Wl,--build-id=none -o build/bf_compiler_boot.out
    
    This gives us our first brainfuck compiler running in machine code: `build/bf_compiler_boot.out`.

3.  Next, we compile the brainfuck source code to the brainfuck compiler using the program
    produced during the previous step

        cat build/bf_compiler.brainfuck | ./build/bf_compiler_boot.out > build/bf_compiler_self_hosted.s
        gcc build/bf_compiler_self_hosted.s -nostdlib -Wl,--build-id=none -o build/bf_compiler_self_hosted.out

    Again, `gcc` is used to assemble the output produced by the brainfuck compiler.
    This produces our second brainfuck compiler running in machine code:
    `build/bf_compiler_self_hosted.out`.

4.  To convince ourselves we've hit a fixed point, we feed the second brainfuck compiler
    it's own source code, and ensure the GNU assembly it emits is a perfect match for the
    assembly produced during the previous stage:

    cat build/bf_compiler.brainfuck | build/bf_compiler_self_hosted.out > build/bf_compiler_self_hosted_2.s
    diff build/bf_compiler_self_hosted.s build/bf_compiler_self_hosted_2.s

5.  For a final demonstration of the awesome power and practical utility of our
    brainfuck compiler, we compile the brainfuck "hello world" example from wikipedia:

        cat bf_demos/hello.brainfuck | build/bf_compiler_self_hosted.out> build/hello.s
        gcc build/hello.s -nostdlib -Wl,--build-id=none -o build/hello.out
        build/hello.out
        Hello World!

