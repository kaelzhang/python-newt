files = newt test *.py
test_files = *

test:
	pytest -s -v test/test_$(test_files).py --doctest-modules --cov newt --cov-config=.coveragerc --cov-report term-missing

lint:
	flake8 $(files)

fix:
	autopep8 --in-place -r $(files)

install:
	pip install -U -r test-requirements.txt

report:
	codecov

build: newt
	rm -rf dist
	python setup.py sdist bdist_wheel

publish:
	make build
	twine upload --config-file ~/.pypirc -r pypi dist/*

.PHONY: test build
