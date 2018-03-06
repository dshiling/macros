.PHONY = build run stop test open push

PROJECT_NAME :=
PROJECT_PORT :=

GIT_COMMIT_SHORT := $(shell git rev-parse --short=8 HEAD)

BUILD_PARAMS =

DOCKER_REGISTRY =
DOCKER_REPO =
DOCKER_RUN_PARAMS = -d -p $(PROJECT_PORT):$(PROJECT_PORT)
DOCKER_TAG = $(GIT_COMMIT_SHORT)

CONTAINER = $(DOCKER_REGISTRY)/$(DOCKER_REPO):$(DOCKER_TAG)

PG_USER =
PG_HOST =

build:
	@echo "Building image $(CONTAINER)..."
	docker build -t $(CONTAINER) $(BUILD_PARAMS) .

run: stop
	@echo "Starting container..."
	docker run --name $(PROJECT_NAME) $(DOCKER_RUN_PARAMS) $(CONTAINER)

push:
	docker push $(CONTAINER)

stop:
	@echo "Stopping and removing container..."
	-@docker stop $(PROJECT_NAME)
	-@docker rm $(PROJECT_NAME)

check-env:
	@if [ -z $(VIRTUAL_ENV) ]; then\
		echo "You need a virtual environment!";\
	fi

setup-db:
	-psql -h $(PG_HOST) -U $(PG_USER) -c "CREATE USER $(PROJECT_NAME);"
	psql -h $(PG_HOST) -U $(PG_USER) -c "DROP DATABASE IF EXISTS $(PROJECT_NAME);"
	psql -h $(PG_HOST) -U $(PG_USER) -c "CREATE DATABASE $(PROJECT_NAME);"

setup-test-db:
	-psql -h $(PG_HOST) -U $(PG_USER) -c "CREATE USER $(PROJECT_NAME);"
	psql -h $(PG_HOST) -U $(PG_USER) -c "DROP DATABASE IF EXISTS $(PROJECT_NAME)_test;"
	psql -h $(PG_HOST) -U $(PG_USER) -c "CREATE DATABASE $(PROJECT_NAME)_test;"

lint: check-env
	pylint $(PROJECT_NAME)
	pycodestyle .

test: check-env lint
	pytest .
open:
	$(eval $@_HOST := http://localhost:$(PROJECT_PORT))
	@echo "Running at $($@_HOST)"
	@open $($@_HOST)
# -------------------------  Continous Integration Section -----------------------

ci-test: build ci-clean
	@echo "Testing release $(DOCKER_TAG)..."
	docker run -d \
		--name ci_postgres \
		-e "POSTGRES_USER=$(POSTGRES_USER)" \
		-e "POSTGRES_DB=$(PROJECT_NAME)" \
		postgres
	docker run --rm \
		-e "SQLALCHEMY_DATABASE_URI=postgresql://$(POSTGRES_USER)@test_db/$(PROJECT_NAME)" \
		--link ci_postgres:test_db \
		$(CONTAINER) ./docker_run_tests.sh

ci-clean:
	-docker stop ci_postgres
	-docker rm ci_postgres

bamboo-vars:
	@echo "Writing vars for version $(DOCKER_TAG)"
	@echo "image_tag=$(DOCKER_TAG)" > .bamboo_vars

bamboo-docker-login:
	@echo "Docker registry $(DOCKER_REGISTRY) login $(bamboo_registry_username)..."
	@docker login -u ${bamboo_registry_username} -p "${bamboo_registry_password}" $(DOCKER_REGISTRY)

bamboo-docker-logout:
	@echo "Docker logout"
	@docker logout ${DOCKER_REGISTRY}

bamboo-release: bamboo-docker-login bamboo-vars build | ci-test push bamboo-docker-logout
bamboo-clean: ci-clean
