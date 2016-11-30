.PHONY:
build:
	docker pull docker.io/debian:jessie
	docker build -t c2corg/v6_images:latest .

build_tests:
	docker pull docker.io/debian:jessie
	docker build -t c2corg/v6_images:latest -f Dockerfile_tests .

.PHONY:
run: build
	docker-compose up

.PHONY:
latest:
	docker pull docker.io/c2corg/v6_images:latest
	docker-compose up

.build/venv/bin/python .build/venv/bin/pip:
	pyvenv .build/venv

.build/venv/bin/mypy .build/venv/bin/py.test .build/venv/bin/flake8: requirements_host.txt .build/venv/bin/python
	.build/venv/bin/pip install -r requirements_host.txt

.PHONY:
mypy: build
	docker-compose run --rm -e TRAVIS=$$TRAVIS wsgi scripts/check_typing.sh

.PHONY:
test-inside: build_tests
	docker-compose run --rm -e TRAVIS=$$TRAVIS wsgi scripts/launch_inside_tests.sh

.PHONY:
test-outside: .build/venv/bin/py.test build_tests
	.build/venv/bin/py.test -v tests/wsgi; ERROR=$$?; [ 0 -eq $$ERROR ] || (scripts/show_logs.sh; exit $$ERROR)

.PHONY:
test: test-inside test-outside

.PHONY:
flake8: .build/venv/bin/flake8
	# Ignore ; on same line
	.build/venv/bin/flake8 --max-line-length=120 --ignore=E702 *.py tests c2corg_images

.PHONY:
check: flake8 mypy test

.PHONY:
logs:
	scripts/show_logs.sh

.PHONY:
enter:
	docker exec -it v6_images_wsgi_1 bash

.PHONY:
clean:
	rm -rf .build .cache
	find . -type f -path '*/__pycache__/*' -delete
	find . -type d -name __pycache__ -delete

.PHONY:
cleanall: clean
	rm -rf active/* incoming/*

.PHONY:
publish: clean
	scripts/travis-build.sh
	scripts/travis-publish.sh
