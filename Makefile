# Find executables

ifneq ($(shell type -p python3),)
PYTHON ?= python3
else ifneq ($(shell type -p python),)
PYTHON ?= python
else
$(error "Python interpreter not found in PATH")
endif

ifneq ($(shell type -p coverage),)
COVERAGE ?= coverage
else ifneq ($(shell type -p python-coverage),)
COVERAGE ?= python3-coverage
endif

ANYBADGE ?= $(shell type -p anybadge)


# Project
MODULE_MAIN     := ps3iso
MODULE_TEST     := test
MODULE_VERSION  := $(shell $(PYTHON) -c 'import setup; print(setup.version)')
MODULE_LICENSE  := $(shell $(PYTHON) -c 'import setup; print(setup.license)')
SOURCE_FILES    := $(shell find $(MODULE_MAIN) $(MODULE_TEST) setup.py test -iname '*.py')
ARTIFACTS_DIR   := artifacts/

# Sphinx Documentation Generator
SPHINX_OPTS    	?=
SPHINX_BUILD   	?= sphinx-build
SPHINX_APIDOC   ?= sphinx-apidoc
DOC_BUILD_DIR   ?= doc/build
DOC_SOURCE_DIR  ?= doc/src
DOC_APIDOC_DIR  ?= doc/src/apidoc

# Badge generation
BADGES_DIR 		:= $(ARTIFACTS_DIR)badges/
COVERAGE_BADGE  := $(BADGES_DIR)coverage.svg
LICENSE_BADGE   := $(BADGES_DIR)license.svg

# Coverage
COVERAGE_FILE   := .coverage
COVERAGE_HTML   := $(ARTIFACTS_DIR)htmlcov/

PYPI_SDIST      := dist/$(MODULE_MAIN)-$(MODULE_VERSION).tar.gz

BUILD_DIRS 		:= $(wildcard build/) $(wildcard dist/) $(wildcard *.egg-info) $(wildcard $(ARTIFACTS_DIR)) $(wildcard __pycache__)
MAKEFILE_DIR    := $(dir $(realpath $(lastword $(MAKEFILE_LIST))))
CLEAN_FILES     := $(BUILD_DIRS) $(wildcard .coverage) $(wildcard *.pyc)


default: package doc coverage-html artifacts

clean:
	rm -fr "$(DOC_BUILD_DIR)" "$(DOC_APIDOC_DIR)" $(CLEAN_FILES)

test:
	$(PYTHON) -m test


# PyPi Targets
#------------------------------------------------------------------------------
package: $(PYPI_SDIST)

$(PYPI_SDIST): $(SOURCE_FILES)
	$(PYTHON) setup.py sdist bdist_wheel

upload: package
	twine upload dist/*


# Documentation Targets
#------------------------------------------------------------------------------
doc: $(DOC_BUILD_DIR)

$(DOC_BUILD_DIR): _sphinx_build $(SOURCE_FILES)
	@$(SPHINX_BUILD) -b html "$(DOC_SOURCE_DIR)" "$(DOC_BUILD_DIR)" $(SPHINX_OPTS)




# Coverage Targets
#------------------------------------------------------------------------------
coverage: _coverage $(COVERAGE_FILE)
	$(COVERAGE) report

coverage-html: $(COVERAGE_HTML)

$(COVERAGE_HTML): _coverage $(COVERAGE_FILE)
	[ ! -d "$(COVERAGE_HTML)" ] || rm -r "$(COVERAGE_HTML)"
	$(COVERAGE) html -d "$(COVERAGE_HTML)"

$(COVERAGE_FILE): _coverage $(SOURCE_FILES)
	$(COVERAGE) run -m --source $(MODULE_MAIN) $(MODULE_TEST)



# Artifact Targets
#------------------------------------------------------------------------------
artifacts: $(COVERAGE_BADGE) coverage-html

$(COVERAGE_BADGE): _coverage _anybadge $(BADGES_DIR) $(COVERAGE_FILE)
	$(ANYBADGE) -v $$($(COVERAGE) report | awk '/^TOTAL/{gsub("%","",$$4);print $$4}') -o -f $@ coverage

$(LICENSE_BADGE): _anybadge $(BADGES_DIR) LICENSE
	$(ANYBADGE) -c '#97ca00' -l license -v $(MODULE_LICENSE) -o -f $@

$(BADGES_DIR):
	[ -d "$(BADGES_DIR)" ] || mkdir -p "$(BADGES_DIR)"

$(ARTIFACTS_DIR):
	[ -d "$(ARTIFACTS_DIR)" ] || mkdir -p "$(ARTIFACTS_DIR)"


# Targets which fail if the executable is not available
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

.PHONY: default clean test doc coverage coverage-html upload artifacts package badges _anybage _coverage _sphinx_build

