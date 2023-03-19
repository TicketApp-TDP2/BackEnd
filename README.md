# TDP2-TicketApp

Repositorio para el backend del proyecto TicketApp de la materia Taller de Desarrollo de Proyectos II en FIUBA.


## API

### Develop: http://localhost:{PORT}/api/
### Production: http:///api/

## Run the server

One commands is given in order to simplify server execution:

```bash
make start-server
```

* Will start a server.

Host and port on which the server will run can be specified by using two variables on  `start-server`:

```bash
make start-server PORT=4000 HOST=127.0.0.1
```

If not specified, port will be defaulted to 4000 and host to 0.0.0.0

## Docker

You can easily get TicketApp API up by running

```
docker build -t ticketapp .
docker run -d --name ticketapp-container -p 8080:8080 ticketapp

```

## Virtual Env (Optional)

- Install virtualenv

- Create virtual env

```bash
virtualenv acp1 --python=python3
```

- Activate env

```bash
source acp1/bin/activate
```

- To deactivate run

```bash
deactivate
```


## Install

- Install Poetry

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

or

```bash
pip install poetry
```

- Check enviroment variables

- Install dependencies

```
poetry install
```

