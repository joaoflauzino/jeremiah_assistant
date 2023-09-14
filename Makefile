api:
	cd app; python bot_api.py

database_api:
	cd app; python database_api.py

lint:
	black app/
	bandit app/
	flake8 app/