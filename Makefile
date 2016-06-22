.PHONY:
build:
	docker build -t c2corg/v6_images:latest .

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
check: flake8 mypy test

.PHONY:
logs:
	scripts/show_logs.sh

.PHONY:
enter:
	docker exec -it v6_images_wsgi_1 bash

.PHONY:
clean:
	rm -rf .build __pycache__ .cache

.PHONY:
cleanall: clean
	rm -rf active/* incoming/*

.PHONY:
publish:
	docker login -e $$DOCKER_EMAIL -u $$DOCKER_USER -p $$DOCKER_PASS
	docker push c2corg/v6_images:latest
