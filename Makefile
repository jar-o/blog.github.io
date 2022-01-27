generate:
	@echo Run source .venv3/bin/activate!
	python gen.py

blog: generate
	open index.html
