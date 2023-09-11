
TOP = m2s_pipe
WAVE = 0
REF = 0

ifeq ($(WAVE), 1)
	OPT += -w
endif

ifeq ($(REF), 1)
	OPT += -r
endif

sim:
	python3 test_$(TOP).py $(OPT)

clean:
	rm -rf __pycache__ build