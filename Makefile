
build:
	docker-compose build

start-server: build
	docker-compose up

kill-server:
	docker-compose stop -t 1
	docker-compose down

new-server: kill-server start-server

test-server:
	docker-compose run --rm -e ENV_NAME="TEST" proy2-backend poetry run pytest

test-server-cov:
	docker-compose run --rm -e ENV_NAME="TEST" -v "$(pwd)/coverage:/coverage" proy2-backend poetry run pytest --cov=app --cov-report xml:/coverage/coverage.xml


