.PHONY: update install install-dev

update:
	pip-compile requirements.in
	pip-compile requirements-dev.in

upgrade:
	pip-compile --upgrade requirements.in
	pip-compile --upgrade requirements-dev.in

install:
	pip-sync requirements.txt

install-dev:
	pip-sync requirements.txt requirements-dev.txt
