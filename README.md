# Home Assistant Configuration

My [Home Assistant](https://home-assistant.io/) Configuration Files

## Inspiration and Support

- [Graeme Smith](https://github.com/Instagraeme)
- [Johan Bloemberg](https://github.com/aequitas)

## My Setup

- Orginal OS: Windows 10 32-bit virtualization on Windows Server 2016 Hyper-V
- Current OS: Ubuntu Server 16.04.1 LTS virtualization on Windows Server 2016 Hyper-V
- MQTT: Locally hosted [Mosquitto](https://mosquitto.org/) MQTT broker 
- HTTPS SSL Certificate generated via [Let's Encript](https://home-assistant.io/docs/ecosystem/certificates/lets_encrypt/)

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


## Github hosted homemade hardware
- [Homemade 433Mhz MQTT transmitter gatway](https://github.com/Genestealer/ESP8266-433Mhz-Controller-Gateway)
- [Homemade 433Mhz bunny shed heating contoller](https://github.com/Genestealer/Bunny-Shed-Climate-Control)
- [Home Assistant to RFLink Gateway Controller](https://github.com/Genestealer/Home-Assistant-RFLink-Gateway-ESP8266)


## Example
![Home Assistant](git_photos/example_screen.PNG)
