.PHONY: install dependencies deploy test

# Directory variables
INSTALL_DIR = $(shell pwd)
RTL_433_BIN = $(shell which rtl_433)

install: dependencies configure_mpd deploy
install.rpi: dependencies.rpi configure_mpd.rpi deploy

dependencies:
	apt update
	apt install -y python3-pip python3-venv rtl-433 libasound2-dev mpd mpc espeak-ng tmux
	python3 -m venv ouistici
	grep -v '^rpi.lgpio' requirements.txt | ouistici/bin/pip install -r /dev/stdin

dependencies.rpi:
	apt update
	apt install -y python3-pip python3-venv python3-dev rtl-433 alsa-utils libasound2-dev mpd mpc espeak-ng tmux gcc swig liblgpio-dev
	python3 -m venv ouistici
	ouistici/bin/pip install -r requirements.txt

configure_mpd:
	cat config/mpd_audio.conf >> /etc/mpd.conf
	ln -s $(INSTALL_DIR)/media/ /var/lib/mpd/music/
	systemctl restart mpd

configure_mpd.rpi:
	sed -i '/^dtparam=audio=on/s/^/#/' /boot/firmware/config.txt
	echo 'dtoverlay=rpi-codeczero' | tee -a /boot/firmware/config.txt
	cp config/asound.conf /etc/asound.conf
	cat config/mpd_audio.rpi.conf >> /etc/mpd.conf
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

clean:
	rm -rf ouistici .lgd-nfy0
