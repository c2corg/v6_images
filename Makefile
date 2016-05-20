.PHONY:
build:
	docker build -t gberaudo/c2cv6images .

.PHONY:
run: build
	docker-compose up

.PHONY:
latest:
	docker pull gberaudo/c2cv6images
	docker-compose up

.build/venv/bin/python .build/venv/bin/pip:
	pyvenv .build/venv

.build/venv/bin/py.test .build/venv/bin/flake8: requirements.txt .build/venv/bin/python
	.build/venv/bin/pip install -r requirements.txt

.PHONY:
test: .build/venv/bin/py.test build
	.build/venv/bin/py.test tests

.PHONY:
flake8: .build/venv/bin/flake8
	.build/venv/bin/flake8 --max-line-length=120 *.py tests c2cv6images

.PHONY:
check: flake8 test
