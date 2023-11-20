# =============================================================================
# Inherit values from ENV _or_ command line or use defaults for:
# $PYTHON_VERSION e.g. 2.7.13 (use current unless given)
# $PYTHON_SHORT e.g. 2.7 (optional)
# $PYTHON_VSHORT e.g. 2  (optional)
#
# e.g.
# > make install PYTHON_SHORT=2.7 PYTHON_VERSIONS=2.7.13
#
# or
# > setenv PYTHON_SHORT 2.7; setenv PYTHON_SHORT 2.7;
# > make install
#
# $TARGET may also be applied explicitly for e.g. install at /project/res
# > setenv RESTARGET ${SDP_BINDIST_ROOT}/lib/python${PYTHON_SHORT}/site-packages
# > make siteinstall TARGET=$RESTARGET
# =============================================================================

xt.PHONY: clean clean-test clean-pyc clean-build docs help pyver
.DEFAULT_GOAL := help

define PRINT_HELP_PYSCRIPT
import re, sys
for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT


APPLICATION := grid3d_maps
DOCSINSTALL := /project/sdpdocs/XTGeo/apps

BROWSER := firefox

PYTHON_VERSION ?= $(shell python -c "import sys; print('{0[0]}.{0[1]}.{0[2]}'.format(sys.version_info))")
PYTHON_SHORT ?= `echo ${PYTHON_VERSION} | cut -d. -f1,2`
PYTHON_VSHORT ?= `echo ${PYTHON_VERSION} | cut -d. -f1`

# Active python my be e.g. 'python3.4' or 'python3' (depends...)
ifeq (, python${PYTHON_SHORT})
PSHORT := ${PYTHON_SHORT}
else
PSHORT := ${PYTHON_VSHORT}
endif
PYTHON := python${PSHORT}
PIP := pip${PSHORT}


TARGET := ${SDP_BINDIST_ROOT}


help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)


clean: clean-build clean-pyc clean-test ## remove all build, test, coverage...


clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -fr {} +


clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +


clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr TMP/

develop:  ## make develop mode (for pure python only)
	${PIP} install -e .

lint: ## check style with flake8
	flake8 ${APPLICATION} tests


test:  ## run tests quickly with the default Python
	@${PYTHON} setup.py test

coverage: ## check code coverage quickly with the default Python
	coverage run --source ${APPLICATION} -m pytest
	coverage report -m
	coverage html
	$(BROWSER) htmlcov/index.html


docsrun: clean ## generate Sphinx HTML documentation, including API docs
	rm -f docs/${APPLICATION}*.rst
	rm -f docs/modules.rst
	rm -fr docs/_build
	$(MAKE) -C docs clean
	$(MAKE) -C docs html


docs: docsrun ## generate and display Sphinx HTML documentation...
	$(BROWSER) docs/_build/html/index.html


dist: clean  ## builds wheel package
	@echo "Running ${PYTHON} (${PYTHON_VERSION}) bdist_wheel..."
	@${PYTHON} setup.py bdist_wheel


install: dist
	@echo "Running ${PIP} (${PYTHON_VERSION}) ..."
	${PIP} install . --upgrade
	#@${PIP} install --upgrade --global-option=build \
	#--global-option='--executable=/usr/bin/env python' .


siteinstall: dist ## Install in project/res (Trondheim) using $TARGET
	@echo $(HOST)
	PYTHONUSERBASE=${TARGET} ${PIP} install . --user --upgrade

userinstall: dist
	@echo $(HOST)
	PYTHONUSERBASE=${HOME} ${PIP} install . --user --upgrade


docsinstall: docsrun
	rsync -av --delete docs/_build/html ${DOCSINSTALL}/${APPLICATION}
	/project/res/bin/res_perm ${DOCSINSTALL}/${APPLICATION}
