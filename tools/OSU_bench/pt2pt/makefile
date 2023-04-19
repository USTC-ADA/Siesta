
MPICC = /home/cs/sunjw/common/openmpi-3.1.0/bin/mpicc
INCDIR = ../util
BINDIR = ../bin
SRC = $(wildcard *.c)
INC = $(wildcard *.h)
TAR = $(patsubst %.c, %, $(SRC))

UTILITIES = ../util/osu_util.o \
	../util/osu_util_mpi.o \
	../util/osu_util_graph.o \
	../util/osu_util_papi.o

all : $(TAR)

$(TAR) : %:%.c
	$(MPICC) -I$(INCDIR) -g -O2 -o $@ $< $(UTILITIES) -lm

.PHONY : clean
clean :
	rm -f $(TAR)