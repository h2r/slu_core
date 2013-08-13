default_target: all

# get a list of subdirs to build by reading tobuild.txt
TOBUILD:=$(shell grep -v "^\#" tobuild.txt)



# Figure out where to build the software.
#   Use BUILD_PREFIX if it was passed in.
#   If not, search up to two parent directories for a 'build' directory.
#   Otherwise, use ./build.
ifeq "$(BUILD_PREFIX)" ""
BUILD_PREFIX=$(shell for pfx in .. ../..; do d=`pwd`/$$pfx/build; \
               if [ -d $$d ]; then echo $$d; exit 0; fi; done; echo `pwd`/build)
endif

LAST_BUILD:=$(BUILD_PREFIX)/last_build
have_a := $(wildcard $(LAST_BUILD)) 
ALL_SUBDIRS:=$(shell grep -v "^\#" tobuild.txt)	
ifeq ($(strip $(have_a)),) 
SUBDIRS := $(ALL_SUBDIRS)
else
SUBDIRS:=$(shell find $(TOBUILD) -mount -newer $(LAST_BUILD) -printf "%H\n" | sort -u)
endif


# build quietly by default.  For a verbose build, run "make VERBOSE=1"
$(VERBOSE).SILENT:

all: 
	echo $(SUBDIRS)
	@[ -d $(BUILD_PREFIX) ] || mkdir -p $(BUILD_PREFIX) || exit 1
	@for subdir in $(SUBDIRS); do \
		echo "\n-------------------------------------------"; \
		echo "-- $$subdir"; \
		echo "-------------------------------------------"; \
		$(MAKE) -C $$subdir all || exit 2; \
	done
# Place additional commands here if you have any
	touch  $(LAST_BUILD)

clean:
	@for subdir in $(ALL_SUBDIRS); do \
		echo "\n-------------------------------------------"; \
		echo "-- $$subdir"; \
		echo "-------------------------------------------"; \
		$(MAKE) -C $$subdir clean; \
	done
	@# Place additional commands here if you have any
