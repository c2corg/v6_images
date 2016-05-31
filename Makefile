.PHONY:
build:
	docker build -t gberaudo/c2corg_images .

.PHONY:
run: build
	docker-compose up

.PHONY:
latest:
	docker pull gberaudo/c2corg_images
	docker-compose up

.build/venv/bin/python .build/venv/bin/pip:
	pyvenv .build/venv

.build/venv/bin/mypy .build/venv/bin/py.test .build/venv/bin/flake8: requirements_host.txt .build/venv/bin/python
	.build/venv/bin/pip install -r requirements_host.txt

.PHONY:
mypy: build
	docker-compose run -e TRAVIS=$$TRAVIS wsgi scripts/check_typing.sh

.PHONY:
test-inside: build
	docker-compose run -e TRAVIS=$$TRAVIS wsgi scripts/launch_inside_tests.sh

.PHONY:
test-outside: .build/venv/bin/py.test build
	.build/venv/bin/py.test -v tests/wsgi; ERROR=$$?; [ 0 -eq $$ERROR ] || (scripts/show_logs.sh; exit $$ERROR)

.PHONY:
test: test-outside test-inside

.PHONY:
flake8: .build/venv/bin/flake8
	# Ignore ; on same line
	.build/venv/bin/flake8 --max-line-length=120 --ignore=E702 *.py tests c2corg_images

.PHONY:
check: flake8 test

.PHONY:
logs:
	scripts/show_logs.sh

.PHONY:
enter:
	docker exec -it c2corg_images_wsgi_1 bash

.PHONY:
clean:
	rm -rf .build __pycache__ .cache

.PHONY:
cleanall: clean
	rm -rf active/* incoming/*
