.PHONY: run
run:
	textual run "textual_wifi.app:WifiApp"

.PHONY: dev
dev:
	while true; do textual run --dev "textual_wifi.app:WifiApp"; done

.PHONY: debug
debug:
	textual console


.PHONY: env
env:
	poetry shell
