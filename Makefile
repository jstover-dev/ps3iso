# Find executables

findpath = $(shell which $(1))

ifneq ($(call findpath,python3),)
PYTHON ?= python3
else ifneq ($(call findpath,python),)
PYTHON ?= python
else
$(error "Python interpreter not found in PATH")
endif

ifneq ($(call findpath,coverage),)
COVERAGE ?= coverage
else ifneq ($(call findpath,python3-coverage),)
COVERAGE ?= python3-coverage
endif

ANYBADGE ?= $(call findpath,anybadge)

# recursive wilcard (https://stackoverflow.com/a/18258352)
rwildcard=$(foreach d,$(wildcard $(1:=/*)),$(call rwildcard,$d,$2) $(filter $(subst *,%,$2),$d))

# Project
MODULE_MAIN     := ps3iso
MODULE_TEST     := test
MODULE_VERSION  := $(shell $(PYTHON) -B -c 'import setup; print(setup.version)')
MODULE_LICENSE  := $(shell $(PYTHON) -B -c 'import setup; print(setup.license)')
ARTIFACTS_DIR   := artifacts/

# Test runner
TEST_RUN 		:= $(PYTHON) -m $(MODULE_TEST)
TEST_OPTIONS    +=

# Sphinx Documentation Generator
SPHINX_OPTS    	?=
SPHINX_BUILD   	?= sphinx-build
SPHINX_APIDOC   ?= sphinx-apidoc
DOC_BUILD_DIR   ?= doc/build
DOC_SOURCE_DIR  ?= doc/src
DOC_APIDOC_DIR  ?= doc/src/apidoc
APIDOC_OPTS  	?= members,show-inheritance,no-undoc-members

# Badge generation
BADGES_DIR 		:= $(ARTIFACTS_DIR)badges/
COVERAGE_BADGE  := $(BADGES_DIR)coverage.svg
LICENSE_BADGE   := $(BADGES_DIR)license.svg

# Coverage
COVERAGE_FILE   := .coverage
COVERAGE_HTML   := $(ARTIFACTS_DIR)htmlcov/
COVERAGE_OMIT   := $(addprefix --omit=,*/__main__.py)

# Source Packages
SDIST_NAME 			:= $(MODULE_MAIN)-$(MODULE_VERSION).tar.gz
PYPI_SDIST      	:= dist/$(SDIST_NAME)
DEBIAN_SDIST		:= ../$(SDIST_NAME)

# Build FIles
_BUILD_DIRS  		:= build dist *.egg-info .pytest_cache $(ARTIFACTS_DIR) $(DOC_BUILD_DIR)
BUILD_DIRS  		:= $(strip $(foreach d,$(_BUILD_DIRS),$(wildcard $(d))))
BUILD_DIRS 			+= $(foreach d,. * */* */*/* */*/*/*,$(wildcard $(d)/__pycache__))
DOC_BUILD_FILES 	?=

# Source Files
SOURCE_FILES 		:= $(call rwildcard,.,*.py)
DOC_SOURCE_FILES	:= $(filter-out $(DOC_BUILD_FILES),$(call rwildcard,$(DOC_SOURCE_DIR),*.py *.rst))

MAKEFILE_DIR    	:= $(dir $(realpath $(lastword $(MAKEFILE_LIST))))
CLEAN_FILES     	:= $(foreach f, $(BUILD_DIRS) $(wildcard $(COVERAGE_FILE)) $(DOC_BUILD_FILES), $(strip $(f)))


default:
	@echo "No target specified, try running one of the following:"
	@echo "    make all             | Same as 'make artifacts coverage-html doc pypi'"
	@echo "    make artifacts       | Generate artifacts such as badges"
	@echo "    make clean           | Clean the working directory of all build files"
	@echo "    make coverage        | Generate coverage report and show text report"
	@echo "    make coverage-html   | Generate HTML coverage report"
	@echo "    make doc             | Build the documentation"
	@echo "    make pypi            | Build the package ready for PyPi upload"
	@echo "    make pypi-upload     | Upload the package to PyPI"
	@echo "    make test            | Run the unit tests without coverage report"

all: artifacts coverage-html doc pypi

clean:
ifneq ($(strip $(CLEAN_FILES)),)
	rm -rf $(CLEAN_FILES)
endif

test:
	$(TEST_RUN) $(TEST_OPTIONS)


# PyPi Targets
#------------------------------------------------------------------------------
pypi: $(PYPI_SDIST)

$(PYPI_SDIST): $(SOURCE_FILES)
	$(PYTHON) setup.py sdist bdist_wheel

pypi-upload: pypi
	twine upload dist/*


# Documentation Targets
#------------------------------------------------------------------------------
doc: $(DOC_BUILD_DIR) $(SOURCE_FILES) $(DOC_SOURCE_FILES)

$(DOC_BUILD_DIR): export SPHINX_APIDOC_OPTIONS = $(APIDOC_OPTS)
$(DOC_BUILD_DIR): $(SOURCE_FILES) | _sphinx_build
	$(SPHINX_BUILD) -b html "$(DOC_SOURCE_DIR)" "$(DOC_BUILD_DIR)" $(SPHINX_OPTS)


# Coverage Targets
#------------------------------------------------------------------------------
coverage: $(COVERAGE_FILE) $(SOURCE_FILES) | _coverage
	$(COVERAGE) report

coverage-html: $(COVERAGE_HTML) $(SOURCE_FILES)

$(COVERAGE_HTML): $(COVERAGE_FILE) | _coverage
	[ ! -d "$(COVERAGE_HTML)" ] || rm -r "$(COVERAGE_HTML)"
	$(COVERAGE) html -d "$(COVERAGE_HTML)"

$(COVERAGE_FILE): $(SOURCE_FILES) | _coverage
	$(COVERAGE) run -m $(COVERAGE_OMIT) --source $(MODULE_MAIN) $(MODULE_TEST)


# Artifact Targets
#------------------------------------------------------------------------------
artifacts: $(COVERAGE_BADGE) coverage-html

$(COVERAGE_BADGE): $(BADGES_DIR) $(COVERAGE_FILE) | _coverage _anybadge
	$(ANYBADGE) -v $$($(COVERAGE) report | awk '/^TOTAL/{gsub("%","",$$4);print $$4}') -o -f $@ coverage

$(LICENSE_BADGE): $(BADGES_DIR) LICENSE | _anybadge
	$(ANYBADGE) -c '#97ca00' -l license -v $(MODULE_LICENSE) -o -f $@

$(BADGES_DIR):
	[ -d "$(BADGES_DIR)" ] || mkdir -p "$(BADGES_DIR)"

$(ARTIFACTS_DIR):
	[ -d "$(ARTIFACTS_DIR)" ] || mkdir -p "$(ARTIFACTS_DIR)"


# Targets which fail if the executable is not available
#------------------------------------------------------------------------------
_anybadge:
ifeq ($(ANYBADGE),)
	$(error anybadge executable not found in PATH. Unable to build badges.)
endif
	
_coverage:
ifeq ($(COVERAGE),)
	$(error coverage executable not found in PATH. Unable to generate coverage reports.)
endif

_sphinx_build:
ifeq ($(SPHINX_BUILD),)
	$(error sphinx-build executable not found in PATH. Unable to build documentation.) 
endif

.PHONY: default all clean test doc coverage coverage-html pypi pypi-upload artifacts badges _anybage _coverage _sphinx_build

