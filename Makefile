init:
	python -m pip install -e .
	python -m pip install -r requirements-test.txt

test:
	py.test -s

lint:
	pylint ./scriptorium

black:
	black scriptorium/*.py
	black tests/*.py

mypy:
	mypy ./scriptorium


.PHONY: init test lint black mypy
