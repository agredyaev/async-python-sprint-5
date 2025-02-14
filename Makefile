ONESHELL:

TEST-COMPOSE-FILE=.temp-docker-compose.yml

define temp_compose_up
	printf "include:\n- docker/docker-compose.yml\n-$(1)" > $(TEST-COMPOSE-FILE) && \
	docker compose -f $(TEST-COMPOSE-FILE) up --build
endef

define temp_interg_compose_up
	printf "include:\n- docker/docker-compose.yml\n-$(1)\n-$(2)" > $(TEST-COMPOSE-FILE) && \
	docker compose -f $(TEST-COMPOSE-FILE) up -d
endef

.PHONY: env
env:
	@find . -name ".env.example" | while read file; do \
		cp "$$file" "$$(dirname $$file)/.env"; \
	done

.PHONY: compose-up-auth-tests-func
compose-up-auth-tests-func: env
	$(call temp_compose_up, services/auth/tests/functional/docker-compose.yml)

.PHONY: sync
sync:
	@uv sync --all-groups --all-packages --frozen

.PHONY: setup
setup:
	@curl -LsSf https://astral.sh/uv/install.sh | sh


.PHONY: install_hooks
install_hooks:
	@pre-commit install

.PHONY: upd_hooks
upd_hooks:
	@pre-commit clean
	@pre-commit install --install-hooks

.PHONY: check
check:
	@git add .
	@pre-commit run

.PHONY: check-all
check-all:
	@git add .
	@pre-commit run --all

.PHONY: up
up: env setup sync

.PHONY: run
run: sync env
	@python -m src.main

.PHONY: test
test:
	@pytest --maxfail=10 --disable-warnings --tb=short


.PHONY: migrate
migrate:
	@alembic upgrade head

.PHONY: migrate-test
migrate-test: migrate test



.PHONY: compose-down
compose-down:
	@docker compose down -v

.PHONY: clean
clean: compose-down
	- docker ps -q | xargs -r docker stop || true
	- docker ps -a -q | xargs -r docker rm || true
	- docker system prune -af --volumes || true
	- docker volume ls -q | xargs -r docker volume rm || true
	- docker images -q | xargs -r docker rmi || true
	- find . -type d -name "__pycache__" -exec rm -r {} \+ || true



.PHONY: compose-up
compose-up:
	@docker compose up --build
