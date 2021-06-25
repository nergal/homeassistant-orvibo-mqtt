# Homeassistant Orvibo MQTT

> :warning: **DISCLAIMER:** This is a code that is in the early development stage, not even alpha, and it has many hardcoded things or works only for my setup. That will be changed and refactored in upcoming commits.

Simple bridge between most common orvibo devices - S20 socket and AllOne IR remote.

## Features
* Controll S20 socket from Homeassistant
* Use AllOne as a air conditioner controller

## Installation
```
git clone https://github.com/nergal/homeassistant-orvibo-mqtt.git /opt/homeassistant-orvibo-mqtt

cd /opt/homeassistant-orvibo-mqtt
sudo pip3 install -r requirements.txt
```

## Execution
A first test run is as easy as:

`python3 /opt/homeassistant-orvibo-mqtt/daemon.py`

## Continuous Daemon/Service
You most probably want to execute the program continuously in the background. This can be done either by using the internal daemon or cron.

**Attention:** Daemon mode must be enabled in the configuration file (default).

```
sudo cp /opt/homeassistant-orvibo-mqtt/template.service /etc/systemd/system/homeassistant-orvibo-mqtt.service

sudo systemctl daemon-reload

sudo systemctl start homeassistant-orvibo-mqtt.service
sudo systemctl status homeassistant-orvibo-mqtt.service

sudo systemctl enable homeassistant-orvibo-mqtt.service
```