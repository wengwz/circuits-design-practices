
TOP = m2s_pipe
WAVE = 0
REF = 0

ifeq ($(WAVE), 1)
	OPT += --wave
endif

ifeq ($(REF), 1)
	OPT += --ref
endif

sim: clean
	python3 test_$(TOP).py $(OPT)

clean:
	rm -rf __pycache__ build