api:
	cd app; python api.py

lint:
	black app/
	bandit app/
	flake8 app/