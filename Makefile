# Override Python interpreter
PYTHON          ?= python

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
CLEAN_FILES     := $(BUILD_DIRS) $(wildcard .coverage)


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
	echo $(PYPI_SDIST)

upload: package
	twine upload dist/*


# Documentation Targets
#------------------------------------------------------------------------------
doc: $(DOC_BUILD_DIR)

$(DOC_BUILD_DIR): $(SOURCE_FILES)
	@$(SPHINX_BUILD) -b html "$(DOC_SOURCE_DIR)" "$(DOC_BUILD_DIR)" $(SPHINX_OPTS)




# Coverage Targets
#------------------------------------------------------------------------------
coverage: $(COVERAGE_FILE)
	coverage report

coverage-html: $(COVERAGE_HTML)

$(COVERAGE_HTML): $(COVERAGE_FILE)
	[ ! -d "$(COVERAGE_HTML)" ] || rm -r "$(COVERAGE_HTML)"
	coverage html -d "$(COVERAGE_HTML)"

$(COVERAGE_FILE): $(SOURCE_FILES)
	coverage run -m --source $(MODULE_MAIN) $(MODULE_TEST)



# Artifact Targets
#------------------------------------------------------------------------------
artifacts: $(COVERAGE_BADGE) coverage-html

$(COVERAGE_BADGE): $(BADGES_DIR) $(COVERAGE_FILE)
	anybadge -v $$(coverage report | awk '/^TOTAL/{gsub("%","",$$4);print $$4}') -o -f $@ coverage

$(LICENSE_BADGE): $(BADGES_DIR) LICENSE
	anybadge -c '#97ca00' -l license -v $(MODULE_LICENSE) -o -f $@

$(BADGES_DIR):
	[ -d "$(BADGES_DIR)" ] || mkdir -p "$(BADGES_DIR)"

$(ARTIFACTS_DIR):
	[ -d "$(ARTIFACTS_DIR)" ] || mkdir -p "$(ARTIFACTS_DIR)"



.PHONY: default clean test doc coverage coverage-html upload artifacts package badges

