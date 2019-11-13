init:
	python -m pip install -e .

dev_init:
	python -m pip install -r requirements-dev.txt

test:
	py.test -s

lint:
	pylint ./scriptorium --rcfile=./.pylintrc

black:
	black setup.py
	black scriptorium/*.py
	black tests/*.py

mypy:
	mypy --disallow-untyped-defs --check-untyped-defs --disallow-untyped-calls --follow-imports silent ./scriptorium


.PHONY: init test lint black mypy
