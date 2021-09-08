import appdaemon.plugins.hass.hassapi as hass
import mqttapi as mqtt
from vncdotool import api

class vnctest(hass.Hass):

  def initialize(self):
    self.log("Start VNC Test - 192.168.10.23::5900")
    client = api.connect('192.168.10.23::5900', password='dimension')
    # for i in 'Hello World':
    #    client.keyPress(i)
    for i in 'Hello World!!':
      client.keyPress(i)
    client.keyPress('enter')
    self.log("End VNC Test")

    client.timeout = 10
    try:
        self.log("Capture VNC Image")
        client.captureScreen('/appdaemon/screenshot.png')
    except TimeoutError:
        self.log("Timeout when capturing screen")
        print('Timeout when capturing screen')


# class MyApp(mqtt.Mqtt):

#     def initialize(self):
