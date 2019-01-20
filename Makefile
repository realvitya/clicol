init:
	pip install -r requirements.txt

clean:
	python setup.py clean

install:
	pip install .

uninstall:
	pip uninstall clicol
