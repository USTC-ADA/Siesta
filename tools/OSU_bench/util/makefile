
MPICC = /home/cs/sunjw/common/openmpi-3.1.0/bin/mpicc
TARGET = osu_util.o \
	osu_util_mpi.o \
	osu_util_graph.o \
	osu_util_papi.o
SRC = $(wildcard *.c)
INC = $(wildcard *.h)
OBJ = $(patsubst %.c %.o,$(SRC))

all : $(TARGET)

%.o : %.c $(INC)
	$(MPICC) -I. -g -O2 -c -o $@ $< -lm

.PHONY : clean
clean :
	rm -f *.o