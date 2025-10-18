set PY_VERSION=3.13
set REQ_FILE=requirements.txt

uv python install %PY_VERSION%
uv venv
call .venv\Scripts\activate
uv pip install -r "%REQ_FILE%"
