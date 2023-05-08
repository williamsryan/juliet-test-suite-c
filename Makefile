.PHONY : all test clean

all : test

OBJS = buff.c \
		new-redirect.c \
		test.c

test :
	$(info ************  TEST TODO ************)

clean : 
	rm -rf out/ test.wat test.wasm *.log instrumented/* samples/ harnesses/* original/* bin/ wasm_bin/CWE*/*.run