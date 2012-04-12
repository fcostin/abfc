# works for me with python2 or python3...
PYTHON := python

GCC_OPTS := -nostdlib -Wl,--build-id=none

# either --x64-64 or --ia32 . very unlikely to generate portable code!
BF_ARCH := --x86-64

all: build/hello.out check_fixed_point
	build/hello.out
.PHONY: all

check_fixed_point: build/bf_compiler_self_hosted.s build/bf_compiler_self_hosted_2.s
	diff build/bf_compiler_self_hosted.s build/bf_compiler_self_hosted_2.s
.PHONY: check_fixed_point

clean:
	rm -f build/bf_compiler.brainfuck
	rm -f build/bf_compiler_boot.s
	rm -f build/bf_compiler_boot.out
	rm -f build/bf_compiler_self_hosted.s
	rm -f build/bf_compiler_self_hosted_2.s
	rm -f build/bf_compiler_self_hosted.out
	rm -f build/hello.s
	rm -f build/hello.out
.PHONY: clean

build/bf_compiler.brainfuck:	macros/self_hosting_bf_compiler.py
	$(PYTHON) abfc/compile_macro.py $(BF_ARCH) $< > $@

build/bf_compiler_boot.s:	build/bf_compiler.brainfuck
	$(PYTHON) abfc/bootstrap_bf.py $(BF_ARCH) $< > $@

build/bf_compiler_boot.out:	build/bf_compiler_boot.s
	gcc $< $(GCC_OPTS) -o $@

build/bf_compiler_self_hosted.s:	build/bf_compiler_boot.out build/bf_compiler.brainfuck
	cat build/bf_compiler.brainfuck | ./$< > $@

build/bf_compiler_self_hosted.out:	build/bf_compiler_self_hosted.s
	gcc $< $(GCC_OPTS) -o $@

build/bf_compiler_self_hosted_2.s:	build/bf_compiler_self_hosted.out build/bf_compiler.brainfuck
	cat build/bf_compiler.brainfuck | build/bf_compiler_self_hosted.out > $@

build/hello.s:	build/bf_compiler_self_hosted.out bf_demos/hello.brainfuck
	cat bf_demos/hello.brainfuck | build/bf_compiler_self_hosted.out> $@

build/hello.out:	build/hello.s
	gcc $< $(GCC_OPTS) -o $@
