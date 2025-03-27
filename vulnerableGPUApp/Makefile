FILE_NAME := vuln

# Location of the CUDA Toolkit
CUDA_PATH ?= /usr/local/cuda-12.6

# architecture
HOST_ARCH   := $(shell uname -m)
TARGET_ARCH ?= $(HOST_ARCH)
TARGET_SIZE := 64
SMS := 75

# operating system
HOST_OS   := $(shell uname -s 2>/dev/null | tr "[:upper:]" "[:lower:]")
TARGET_OS ?= $(HOST_OS)
HOST_COMPILER := clang++
NVCC          := $(CUDA_PATH)/bin/nvcc -ccbin $(HOST_COMPILER)

# internal flags
NVCCFLAGS   := -m${TARGET_SIZE} 
CCFLAGS     :=
LDFLAGS     :=

# build flags

# Link flag for customized HOST_COMPILER with gcc realpath
GCC_PATH := $(shell which gcc)

# Debug build flags
ifeq ($(dbg),1)
      NVCCFLAGS += -g -G 
      BUILD_TYPE := debug
else
      BUILD_TYPE := release
endif

ALL_CCFLAGS :=
ALL_CCFLAGS += $(NVCCFLAGS)
ALL_CCFLAGS += $(EXTRA_NVCCFLAGS)
ALL_CCFLAGS += $(addprefix -Xcompiler ,$(CCFLAGS))
ALL_CCFLAGS += $(addprefix -Xcompiler ,$(EXTRA_CCFLAGS))

SAMPLE_ENABLED := 1

ALL_LDFLAGS :=
ALL_LDFLAGS += $(ALL_CCFLAGS)
ALL_LDFLAGS += $(addprefix -Xlinker ,$(LDFLAGS))
ALL_LDFLAGS += $(addprefix -Xlinker ,$(EXTRA_LDFLAGS))

# Common includes and paths for CUDA
INCLUDES  := -I$(CUDA_PATH)/samples/common/inc/


GENCODE_FLAGS := --generate-code arch=compute_75,code=sm_75

ALL_CCFLAGS += --threads 0 --std=c++11

ifeq ($(SAMPLE_ENABLED),0)
EXEC ?= @echo "[@]"
endif

################################################################################

# Target rules
all: build 

build: $(FILE_NAME)

check.deps:
ifeq ($(SAMPLE_ENABLED),0)
	@echo "Sample will be waived due to the above missing dependencies"
else
	@echo "Sample is ready - all dependencies have been met"
endif

$(FILE_NAME).o:$(FILE_NAME).cu
	$(EXEC) mkdir -p ./build
	$(EXEC) $(NVCC) $(INCLUDES) $(ALL_CCFLAGS) $(GENCODE_FLAGS) -o ./build/$@ -c $<


$(FILE_NAME): $(FILE_NAME).o
	$(EXEC) $(NVCC) $(ALL_LDFLAGS) $(GENCODE_FLAGS) -o ./build/$@ ./build/$+ $(LIBRARIES)


run: build
	$(EXEC) ./$(FILE_NAME)

testrun: build

clean:
	rm -f $(FILE_NAME) $(FILE_NAME).o
	rm -rf ./build
