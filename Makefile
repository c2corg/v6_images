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
test-inside: .build/venv/bin/py.test build
	docker-compose run wsgi python3 /usr/local/lib/python3.4/dist-packages/pytest.py tests/inside

.PHONY:
test-outside: .build/venv/bin/py.test build
	.build/venv/bin/py.test tests/wsgi; ERROR=$$?; [ 0 -eq $$ERROR ] || (scripts/show_logs.sh; exit $$ERROR)

.PHONY:
test: test-outside test-inside

.PHONY:
flake8: .build/venv/bin/flake8
	# Ignore ; on same line
	.build/venv/bin/flake8 --max-line-length=120 --ignore=E702 *.py tests c2cv6images

.PHONY:
check: flake8 test

.PHONY:
logs:
	scripts/show_logs.sh

.PHONY:
enter:
	docker exec -it c2cv6images_wsgi_1 bash
