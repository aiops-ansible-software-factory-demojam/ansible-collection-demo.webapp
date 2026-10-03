.DEFAULT_GOAL := help
PYTHON ?= python3
VENV ?= .venv

export MOLECULE_GLOB := extensions/molecule/*/molecule.yml

.PHONY: help setup hooks lint build test converge destroy

help:
	@printf '%s\n' \
	  'make setup     Install pinned lint tools and collection dependencies' \
	  'make hooks     Install Git pre-commit hooks in this checkout' \
	  'make lint      Run every pre-commit check on the collection' \
	  'make build     Build the collection into /tmp' \
	  'make test      Run both Molecule scenarios sequentially (demo sandbox)' \
	  'make converge  Converge both Molecule scenarios' \
	  'make destroy   Destroy Molecule test VMs'

$(VENV)/bin/python:
	$(PYTHON) -m venv "$(VENV)"

$(VENV)/.dev-deps: requirements-dev.txt extensions/molecule/requirements-test.yml | $(VENV)/bin/python
	"$(VENV)/bin/pip" install -r requirements-dev.txt
	"$(VENV)/bin/ansible-galaxy" collection install -r extensions/molecule/requirements-test.yml
	touch "$@"

setup: $(VENV)/.dev-deps
	mkdir -p .ansible/source/ansible_collections/demo
	ln -sfn "$(CURDIR)" .ansible/source/ansible_collections/demo/webapp

hooks: setup
	"$(VENV)/bin/pre-commit" install --install-hooks

lint: setup
	"$(VENV)/bin/pre-commit" run --all-files

build: setup
	"$(VENV)/bin/ansible-galaxy" collection build --force --output-path /tmp

test:
	molecule test --all

converge:
	molecule converge --all

destroy:
	molecule destroy --all
