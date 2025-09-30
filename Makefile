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
	systemctl enable --now mpd

configure_mpd.rpi:
	# Disable internal audio
	sed -i 's|^dtparam=audio=on$$|dtparam=audio=off|' /boot/firmware/config.txt
	sed -i '/dtoverlay=vc4-kms-v3d/d' /boot/firmware/config.txt
	# Enable rpi-codeczero
	echo 'dtoverlay=rpi-codeczero' | tee -a /boot/firmware/config.txt
	# Add ALSA config for rpi-codeczero
	curl -O https://raw.githubusercontent.com/raspberrypi/Pi-Codec/refs/heads/master/Codec_Zero_Playback_only.state
	alsactl store -D Zero -f Codec_Zero_Playback_only.state || true
	# Add MPD configuration for rpi-codeczero
	cat config/mpd_audio.rpi.conf >> /etc/mpd.conf
	# Move media to mpd dir and link it back to media
	mv media /var/lib/mpd/music/
	ln -s /var/lib/mpd/music/media /media
	# Launch MPD at boot
	systemctl enable --now mpd

deploy:
	cat config/ouistici.service | sed 's|INSTALL_DIR|$(INSTALL_DIR)|g' > /etc/systemd/system/ouistici.service
	cat config/ouistici_serverconfig.service | sed 's|INSTALL_DIR|$(INSTALL_DIR)|g' > /etc/systemd/system/ouistici_serverconfig.service
	cat config/ouistici_rtl_433.service | sed 's|INSTALL_DIR|$(INSTALL_DIR)|g' | sed 's|RTL_433_BIN|$(RTL_433_BIN)|g' > /etc/systemd/system/ouistici_rtl_433.service
	systemctl daemon-reload
	systemctl enable --now ouistici_rtl_433.service
	systemctl enable --now ouistici_serverconfig.service
	systemctl enable --now ouistici.service
	reboot

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
