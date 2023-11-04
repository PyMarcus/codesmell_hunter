# codesmell_hunter

## How to run:

First, you must create a .env file, in the root of the project, with the following variables:
<br>

[.env]

    name=name of the user database
    database=name of database
    password=your password
    host=your host
    port=your port

    gpt_key=your key



create a virtual env

```bash
python -m venv .venv
```
activate the virtual env

```bash
source .venv/bin/activate
```

install dependencies

```bash
pip install -r requirements.txt
```

execute

```bash
python main.py
```
