# Makefile for MPIP	-*-Makefile-*-
# Please see license in doc/UserGuide.html
# testing/Makefile.  Generated from Makefile.in by configure.

srcdir=.
include_mpi_io_tests=yes
include_mpi_rma_tests=yes


include ../Defs.mak

#  Specify compile flags to ensure debugging symbols and no optimization
CFLAGS	= -g
FFLAGS  = -g
LDFLAGS	+= -L..
CXXLIBS	:= -l$(MPIPCXXLIB) $(LIBS) $(CXXLIBS)
FLIBS	:= -l$(MPIPFLIB) $(LIBS)
LIBS	:= -lmpiP $(LIBS)
CPPFLAGS =

CSRCS =	0-simple.c \
	0-simple-c++.C \
	1-hot-potato.c \
	2-pcontrol.c \
	3-stacktrace.c \
	4-demangle.C \
	5-medley.c \
	6-nonblock.c \
	7-nonblock-waitall.c \
	8-test.c \
	9-test-mpip-time.c \
	10-coll-mess-size.c \
	11-p2p-mess-size.c \
	12-null-null.c \
	13-pcontrol-report.c \
	15-pcontrol.c \
	18-coll-non-block.c

ifeq (${include_mpi_io_tests},yes)
CSRCS += 14-mpiio.c
endif

ifeq (${include_mpi_rma_tests},yes)
CSRCS += 17-rma.c
endif

FSRCS =	0-simplef.f sweep-ops.f sweep-ops-stack.f 16-waitallf.f 

TEXES = $(CSRCS:.c=.exe)
EXES = $(TEXES:.C=.exe)
EXES += $(FSRCS:.f=.exe)

all: ${EXES}
	make -C mt
	@echo All done.


.SUFFIXES: .exe
.c.exe::
	${CC} ${CFLAGS} ${CPPFLAGS} $< ${ADD_OBJS} -o $@ ${LDFLAGS} ${LIBS}

.C.exe:
	${CXX} ${CFLAGS} ${CPPFLAGS} $< ${ADD_OBJS} -o $@ ${LDFLAGS} ${CXXLIBS}

.f.exe:
	${FC} ${FFLAGS} ${CPPFLAGS} $< ${ADD_OBJS} -o $@ ${LDFLAGS} ${FLIBS}

clean::
	rm -f ${EXES} *.mpiP *.o
	make -C mt clean

include $(srcdir)/../Rules.mak

##### EOF
