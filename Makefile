MODULE_MAIN     := ps3iso
MODULE_TEST     := test

# Sphinx Documentation Generator
SPHINX_OPTS    	?=
SPHINX_BUILD   	?= sphinx-build
SPHINX_APIDOC   ?= sphinx-apidoc
DOC_BUILD_DIR   ?= doc/build
DOC_SOURCE_DIR  ?= doc/src
DOC_APIDOC_DIR  ?= doc/src/apidoc

default: doc coverage

test: coverage

coverage:
	coverage run -m --source $(MODULE_MAIN) $(MODULE_TEST)
	coverage report
	coverage html

doc:
	@$(SPHINX_BUILD) -b html "$(DOC_SOURCE_DIR)" "$(DOC_BUILD_DIR)" $(SPHINX_OPTS)

clean:
	rm -fr "$(DOC_BUILD_DIR)" "$(DOC_APIDOC_DIR)"

.PHONY: default test coverage doc clean
