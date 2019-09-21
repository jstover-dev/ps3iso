MODULE_MAIN     := ps3iso
MODULE_TEST     := test

# Sphinx Documentation Generator
SPHINX_OPTS    	?=
SPHINX_BUILD   	?= sphinx-build
SPHINX_APIDOC   ?= sphinx-apidoc
DOC_BUILD_DIR   ?= doc/build
DOC_SOURCE_DIR  ?= doc/src
DOC_APIDOC_DIR  ?= doc/src/apidoc

BUILD_DIRS 		:= $(wildcard build/) $(wildcard dist/) $(wildcard *.egg-info) $(wildcard htmlcov/)

default: build doc coverage

test: coverage

coverage:
	coverage run -m --source $(MODULE_MAIN) $(MODULE_TEST)
	coverage report
	coverage html

doc:
	@$(SPHINX_BUILD) -b html "$(DOC_SOURCE_DIR)" "$(DOC_BUILD_DIR)" $(SPHINX_OPTS)

clean:
	rm -fr "$(DOC_BUILD_DIR)" "$(DOC_APIDOC_DIR)" $(BUILD_DIRS)

build:
	python setup.py sdist bdist_wheel

upload: build
	twine upload dist/*


.PHONY: default build test upload coverage doc clean
