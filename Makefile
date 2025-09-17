.PHONY: install dependencies deploy test

# Directory variables
INSTALL_DIR = $(shell pwd)
RTL_433_BIN = $(shell which rtl_433)

install: dependencies configure_mpd deploy

dependencies:
	sudo apt update
	sudo apt install -y python3-pip python3-venv rtl-433 libasound2-dev mpd
	python3 -m venv ouistici
	ouistici/bin/pip install -r requirements.txt

configure_mpd:
	cat config/mpd_audio.conf >> /etc/mpd.conf
	ln -s $(INSTALL_DIR)/media/ /var/lib/mpd/music/
	systemctl restart mpd

deploy:
	cat config/ouistici.service | sed 's|INSTALL_DIR|$(INSTALL_DIR)|g' > /etc/systemd/system/ouistici.service
	cat config/ouistici_serverconfig.service | sed 's|INSTALL_DIR|$(INSTALL_DIR)|g' > /etc/systemd/system/ouistici_serverconfig.service
	cat config/ouistici_rtl_433.service | sed 's|INSTALL_DIR|$(INSTALL_DIR)|g' | sed 's|RTL_433_BIN|$(RTL_433_BIN)|g' > /etc/systemd/system/ouistici_rtl_433.service
	systemctl daemon-reload
	systemctl enable --now ouistici_rtl_433.service
	systemctl enable --now ouistici_serverconfig.service
	systemctl enable --now ouistici.service

test:
	tmux new-session -d -s ouistici
	tmux split-window -h -t ouistici:0
	tmux split-window -h -t ouistici:0
	tmux send-keys -t ouistici:0.0 "rtl_433 -R 0 -c config/rtl_433_ouistici.conf -F http" Enter
	tmux send-keys -t ouistici:0.1 "source ouistici/bin/activate && python3 serverconfig.py" Enter
	tmux send-keys -t ouistici:0.2 "source ouistici/bin/activate && python3 ouistici.py" Enter
	tmux attach-session -t ouistici
