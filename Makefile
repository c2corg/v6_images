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
