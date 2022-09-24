import hassapi as hass
from vncdotool import api

class vnctest(hass.Hass):

    def initialize(self):
    # self.log("Start VNC Test - 192.168.10.24::5901")
    # client = api.connect('192.168.10.24::5901', password='dimension')
    
        self.log("Start VNC Test")

        try:
            self.log("VNC Connect")
            client = api.connect('192.168.3.11', password='engineer')
            client.timeout = 4
            self.log("VNC Connected")
        except TimeoutError:
            self.log("Timeout when connecting VNC")
        
        try:
            self.log("VNC start type test")
            for i in 'Hello World!!':
                client.keyPress(i)
            client.keyPress('enter')
            self.log("End VNC type test")
        except TimeoutError:
            self.log("Timeout typing text")
        try:
            self.log("Capture VNC Image")
            client.captureScreen('screenshot.png')
            self.log("VNC Image Captured")
        except TimeoutError:
            self.log("Timeout when capturing screen")








  # #This will not work as the appdaemon cannot see the file system!
  #   with api.connect('192.168.10.24::5901', password='dimension') as client:
  #      client.captureScreen(' screenshot.png')

# class MyApp(mqtt.Mqtt):

#     def initialize(self):




# python_packages:
#   - Pillow==8.2.0
#   - Twisted==21.7.0
#   - zope.interface==5.4.0
#   - pycryptodome==3.12.0
#   - vncdotool==0.13

# https://python.hotexamples.com/examples/vncdotool.api/-/connect/python-connect-function-examples.html





# ****Types Text - working types but no screenshot

# init_commands: []
# python_packages:
#   - vncdotool==0.13
# system_packages: []
# log_level: info


#   def initialize(self):
#     # self.log("Start VNC Test - 192.168.10.24::5901")
#     # client = api.connect('192.168.10.24::5901', password='dimension')
#     self.log("Start VNC Test")
#     client = api.connect('192.168.3.11::5900', password='engineer')
#     self.log("Start VNC Test - connected")
#     # for i in 'Hello World':
#     #    client.keyPress(i)

#     # self.log("Start VNC Test - Type text")

#     #Worked I think
#     for i in 'Hello World!!':
#       client.keyPress(i)
#     client.keyPress('enter')
#     self.log("End VNC Test")

#     client.timeout = 4
  
#     try:
#         self.log("Capture VNC Image")
#         client.captureScreen('screenshot.png')
#     except TimeoutError:
#         self.log("Timeout when capturing screen")
#         print('Timeout when capturing screen')