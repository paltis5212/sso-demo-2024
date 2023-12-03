# start

start_server:
	@ screen -dmS sso_server bash -c '. .venv/bin/activate && python -m sso_server.start'
	@ echo "SSO Server Start OK."

start_client:
	@ screen -dmS sso_client bash -c '. .venv/bin/activate && python -m sso_client.start'
	@ echo "SSO Client Start OK."

start:
	@- make start_server
	@- make start_client

# stop

stop_server:
	@- screen -S sso_server -X quit
	@- kill -9 $$(pgrep -f "sso_server.start")
	@ echo "SSO Server Stop OK."

stop_client:
	@- screen -S sso_client -X quit
	@- kill -9 $$(pgrep -f "sso_client.start")
	@ echo "SSO Client Stop OK."

stop:
	@- make stop_server
	@- make stop_client

# restart

restart_server:
	@ make stop_server
	@ make start_server

restart_client:
	@ make stop_client
	@ make start_client

restart:
	@ make restart_server
	@ make restart_client

# ls

ls:
	@ screen -ls

# tail -f log

log_server:
	@ screen -S sso_server bash -c 'tail -f log/sso_server.log'

log_client:
	@ screen -S sso_client bash -c 'tail -f log/sso_client.log'