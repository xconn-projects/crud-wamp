setup:
	python3 -m venv .venv
	.venv/bin/pip install -r requirements.txt

lint:
	./.venv/bin/ruff format .

check-lint:
	./.venv/bin/ruff check .

run:
	.venv/bin/xconn main:app --directory crud
