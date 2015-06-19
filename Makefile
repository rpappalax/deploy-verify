HERE = $(shell pwd)
VENV = $(HERE)/venv
BIN = $(VENV)/bin
PYTHON = $(BIN)/python
PIP = $(BIN)/pip
INSTALL = $(PIP) install
INSTALL_STAMP = $(VENV)/.install.stamp


.PHONY: all build clean

all:	build 

build: $(VENV)/COMPLETE
$(VENV)/COMPLETE: requirements.txt
	virtualenv --no-site-packages --python=`which python` \
	    --distribute $(VENV)
	$(INSTALL) -r requirements.txt
	$(PYTHON) setup.py develop
	touch $(VENV)/COMPLETE

clean:
	rm -rf venv  *egg*  dist   .tox
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -type d -exec rm -fr {} \;
