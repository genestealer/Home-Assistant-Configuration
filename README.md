# Home Assistant Configuration

My [Home Assistant](https://home-assistant.io/) Configuration Files

## Inspiration and Support

- [Graeme Smith](https://github.com/Instagraeme)
- [Johan Bloemberg](https://github.com/aequitas)

## My Setup

- Original OS: Windows 10 32-bit virtualization on Windows Server 2016 Hyper-V
- Original Home Assistant: Python folder, home assistant run command run at start-up from shortcut in Windows start-up folder.
- 2nd OS: Ubuntu Server 16.04.1 LTS virtualization on Windows Server 2016 Hyper-V.
- 2nd Home Assistant: Python virtual environment with homeassistant user. As per [Manual installation on a Raspberry Pi](https://www.home-assistant.io/docs/installation/raspberry-pi/). [HASSCTL](https://github.com/dale3h/hassctl) Used for management.
- 3rd OS: Ubuntu Server 18.04.1 LTS virtualization on Windows Server 2016 Hyper-V
- 3rd Home Assistant: Hass.IO in Docker on Ubuntu Server 18.04, as per [these instructions](https://bonani.tech/how-to-install-hass.io-on-ubuntu-server-18.04/)
- Current OS: HASS.IO on Raspberry Pi 4 Model B
- Current Home Assistant: Hass.IO for Raspberry Pi 4 Model B 32bit
### HASSIO Add-ons
- MQTT: [Mosquitto broker](https://github.com/home-assistant/hassio-addons/tree/master/mosquitto) MQTT broker add.
- HTTPS Certificate: [Nginx Proxy Manager](https://github.com/hassio-addons/addon-nginx-proxy-manager)
- OLD HTTPS Certificate originally generated via by home assistant via [Let's Encript Instructions](https://home-assistant.io/docs/ecosystem/certificates/lets_encrypt/), with scripts to auto-update and automations to alert via HTML5 push notification if renew date threshold is close. (Search my repository for [ssl_cert.yaml](https://github.com/Genestealer/Home-Assistant-Configuration/blob/master/includes/automation/ssl_cert.yaml))
- [Dasshio](https://github.com/danimtb/dasshio) Hass.io add-on to easily use Amazon Dash Buttons with Home Assistant
- [ESPHome](https://esphome.io/) ESPHome is a system to control your ESP8266/ESP32 by simple yet powerful configuration files and control them remotely through Home Automation systems. Also required MariaDB to be installed.
- [Samba share](https://home-assistant.io/addons/samba/)
- [APC UPS Daemon (No USB)](https://github.com/korylprince/hassio-apcupsd/tree/master/apcupsd_net) View information from APC Network UPSs.
- [AdGuard Home](https://github.com/hassio-addons/addon-adguard-home) Network-wide ads & trackers blocking DNS server.


### ESPHome Things
 - Busylight, I built so my family can know when I'm busy and working in my Home Office. See [busylight.yaml](https://github.com/genestealer/Home-Assistant-Configuration/blob/master/esphome/busylight.yaml) and [busylight_controller.yaml](https://github.com/genestealer/Home-Assistant-Configuration/blob/master/esphome/busylight_controller.yaml)

| BusyLight Controller  | BusyLight Light |
| ------------- | ------------- |
| ![Diagram](https://raw.githubusercontent.com/genestealer/Home-Assistant-Configuration/master/esphome/images/busylight_controller.jpg)  | ![Diagram](https://raw.githubusercontent.com/genestealer/Home-Assistant-Configuration/master/esphome/images/busylight_light.jpg)  |

 - Doorbell with Neopixel LED buttons and external sounder bell. See [doorbell_controller.yaml](https://github.com/genestealer/Home-Assistant-Configuration/blob/master/esphome/doorbell_controller.yaml)
 
 - Non-Invasive Power Meter for House Electricity with visible light phototransistor on LED of electricity meter. See [doorbell_controller.yaml](https://github.com/genestealer/Home-Assistant-Configuration/blob/master/esphome/doorbell_controller.yaml)
 

## Devices

- HPE ProLiant MicroServer Gen8 Server
- [APC UPS - APC UPS Daemon](http://www.apcupsd.org/wordpress/)
- Google Chromecast Audio
- Google Chromecast
- Nest Thermostat
- Amazon Echo Dot (2nd Generation) (using [Emulated Hue Bridge](https://home-assistant.io/components/emulated_hue/) to control hass with voice commands)
- Plex Media Server
- Amazon Dash Button 
- Axis IP CCTV Cameras
- [Raspberry Pi 3 IP CCTV](https://github.com/Motion-Project/motion) with help from [link](https://pimylifeup.com/raspberry-pi-webcam-server)
- IKEA Trådfri (Tradfri) lights (One of the reasons for moving to Linux as the modified lib-coap doesn’t exists for Windows)

#### Items controlled via my [RFLink Controller](https://github.com/Genestealer/Home-Assistant-RFLink-Gateway-ESP8266)
- [Energenie Wall Light Switch MIHO026](https://energenie4u.co.uk/catalogue/product/MIHO026)
- Room lamps plugged into [Maclean MCE07GB Remote Control Sockets](https://www.amazon.co.uk/Maclean-MCE07GB-Control-Sockets-Programmable/dp/B00OV1TTU6) and [Status RCS-K09 Remote Control Sockets](https://www.amazon.co.uk/Status-Remote-Control-Socket-Pack/dp/B003XOXAVG)
- Hacked Ikea E1201C Remote 'relay' for kitchen extractor fan (302.329.80 433MHz two button remote & in-line switch.)
- Ikea Ansluta Lights: Works together with Ikea 2.4GHz Remote control (903.007.73) with CC2500 Transceiver.
- Bunny fluff extractor fan, plug-in air freshener, room wax melters and extra lights (Christmas) plugged into [Status RCS-K09 Remote Control Sockets](https://www.amazon.co.uk/Status-Remote-Control-Socket-Pack/dp/B003XOXAVG)


## Homemade hardware
- [Homemade 433Mhz MQTT transmitter gatway](https://github.com/Genestealer/ESP8266-433Mhz-Controller-Gateway)
- [Homemade 433Mhz bunny shed heating contoller](https://github.com/Genestealer/Bunny-Shed-Climate-Control)
- [Home Assistant to RFLink Gateway Controller](https://github.com/Genestealer/Home-Assistant-RFLink-Gateway-ESP8266)
- [Controllino-Irrigation](https://github.com/genestealer/Controllino-Irrigation)
- [Irrigation-Controller](https://github.com/genestealer/Irrigation-Controller)


## Example
![Home Assistant](git_photos/example_screen.PNG)
