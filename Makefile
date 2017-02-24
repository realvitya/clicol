init:
	pip install -r requirements.txt

clean:
	python setup.py clean

install:
	easy_install .

uninstall:
	pip uninstall clicol
