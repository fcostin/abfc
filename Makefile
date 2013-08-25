# works for me with python2 or python3...
PYTHON := python

CC := gcc
CC_OPTS := -nostdlib -Wl,--build-id=none

# either --x64-64 or --ia32 . very unlikely to generate portable code!
BF_ARCH := --x86-64

all: build/bf_compiler_self_hosted.out
.PHONY: all


clean:
	rm -f build/bf_compiler.brainfuck
	rm -f build/bf_compiler_boot.s
	rm -f build/bf_compiler_boot.out
	rm -f build/bf_compiler_self_hosted.s
	rm -f build/bf_compiler_self_hosted.out
.PHONY: clean


build/bf_compiler.brainfuck:	macros/self_hosting_bf_compiler.py
	$(PYTHON) abfc/compile_macro.py $(BF_ARCH) $< > $@

build/bf_compiler_boot.s:	build/bf_compiler.brainfuck
	$(PYTHON) abfc/bootstrap_bf.py $(BF_ARCH) $< > $@

build/bf_compiler_boot.out:	build/bf_compiler_boot.s
	$(CC) $< $(CC_OPTS) -o $@

build/bf_compiler_self_hosted.s:	build/bf_compiler_boot.out build/bf_compiler.brainfuck
	cat build/bf_compiler.brainfuck | ./$< > $@

build/bf_compiler_self_hosted.out:	build/bf_compiler_self_hosted.s
	$(CC) $< $(CC_OPTS) -o $@


# TEST stuff

TESTCHECK := ./tools/testcheck.sh
TESTREPORT := python ./tools/testreport.py


test: test_fixed_point/testresult test_hello/testresult
	$(TESTREPORT) $^
.PHONY: test


test_fixed_point/testresult:	build/bf_compiler.brainfuck build/bf_compiler_self_hosted.s build/bf_compiler_self_hosted.out
	mkdir -p test_fixed_point
	cp build/bf_compiler.brainfuck test_fixed_point/in.brainfuck
	cp build/bf_compiler_self_hosted.s test_fixed_point/expected_output.s
	cat test_fixed_point/in.brainfuck | build/bf_compiler_self_hosted.out > test_fixed_point/output.s
	diff test_fixed_point/output.s test_fixed_point/expected_output.s
	$(TESTCHECK) test_fixed_point/output.s test_fixed_point/expected_output.s $@

test_hello/testresult:		build/bf_compiler_self_hosted.out test_hello/hello.brainfuck
	cat test_hello/hello.brainfuck | build/bf_compiler_self_hosted.out > test_hello/hello.s
	$(CC) test_hello/hello.s $(CC_OPTS) -o test_hello/hello.out
	test_hello/hello.out > test_hello/output.txt
	$(TESTCHECK) test_hello/output.txt test_hello/expected_output.txt $@

