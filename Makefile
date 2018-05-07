GIT_HASH := $(shell git rev-parse HEAD)

all: build test

.PHONY:
pull:
	for image in `find -name Dockerfile | xargs grep --no-filename FROM | awk '{print $$2}' | sort -u`; do docker pull $$image; done

.PHONY:
build:
	docker build -t c2corg/v6_images:latest --build-arg "GIT_HASH=$(GIT_HASH)" .

.PHONY:
run: build
	docker-compose up

.PHONY:
latest:
	docker pull docker.io/c2corg/v6_images:latest
	docker-compose up

.build/venv/bin/python .build/venv/bin/pip:
	python3 -m venv .build/venv

.build/venv/bin/py.test: requirements_host.txt requirements.txt .build/venv/bin/python
	.build/venv/bin/pip install -r requirements_host.txt -r requirements.txt

.PHONY:
test-inside: build
	docker-compose run --rm -e TRAVIS wsgi scripts/launch_inside_tests.sh

.PHONY:
test-outside: .build/venv/bin/py.test build
	.build/venv/bin/py.test -v tests/wsgi; ERROR=$$?; [ 0 -eq $$ERROR ] || (scripts/show_logs.sh; exit $$ERROR)

.PHONY:
test: test-inside test-outside

.PHONY:
check: test

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
