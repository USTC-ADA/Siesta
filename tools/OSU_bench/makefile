
MPICC = /home/cs/sunjw/common/openmpi-3.1.0/bin/mpicc
PT2PTDIR = ./pt2pt
COLLECTIVEDIR = ./collective
TARGETDIR = ./bin
UTILDIR = ./util
SRC = $(wildcard $(PT2PTDIR)/*.c $(COLLECTIVEDIR)/*.c)
TAR = $(patsubst %.c, %, $(SRC))
TARGETS = $(notdir $(TAR))

module_make = $(MAKE) -C $(1);
module_clean = $(MAKE) clean -C $(1);


all :
	@ $(foreach name,$(UTILDIR) $(COLLECTIVEDIR) $(PT2PTDIR), $(call module_make, $(name)))
	cp $(TAR) $(TARGETDIR)/

.PHONY : clean
clean :
	@ $(foreach name,$(UTILDIR) $(COLLECTIVEDIR) $(PT2PTDIR), $(call module_clean, $(name)))
	rm -f $(TARGETDIR)/*
