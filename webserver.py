#!/usr/bin/python3
import RPi.GPIO as GPIO
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import serial 
import platform    # For getting the operating system name
import subprocess  # For executing a shell command
import time
#from ventilateur_l298n import wake_pc
#from ventilateur_l298n import ventilateurs

host_name = '192.168.1.36'  # IP Address of Raspberry Pi
host_port = 4590

def ping(host):
    """
    Returns True if host (str) responds to a ping request.
    Remember that a host may not respond to a ping (ICMP) request even if the host name is valid.
    """

    # Option for the number of packets as a function of
    param = '-n' if platform.system().lower()=='windows' else '-c'

    # Building the command. Ex: "ping -c 1 google.com"
    command = ['ping', param, '1', host]

    return subprocess.call(command) == 0

def setupGPIO():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(27, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(14, GPIO.OUT, initial=GPIO.LOW) #garage remote control (back door)
    GPIO.setup(15, GPIO.OUT, initial=GPIO.LOW) # garage remote control (front door)
    GPIO.setup(23,GPIO.OUT,  initial=GPIO.LOW)
    GPIO.setwarnings(False)
    GPIO.output(14,GPIO.HIGH)
    GPIO.output(15,GPIO.HIGH)


def getTemperature():
    return '6.0'

class MyServer(BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def _redirect(self, path):
        self.send_response(303)
        self.send_header('Content-type', 'text/html')
        self.send_header('Location', path)
        self.end_headers()

    def do_GET(self):
        html = '''
           <html>
           <body 
            style="width:960px; margin: 20px auto;">
           <h1>Interface web de controle de controle de la raspberry pi </h1>
           <form action="/" method="POST">
               <p>UTILISER LES BOUTONS POUR EFFECTUER LES  FONCTION</p>
               <div style = 'background-color:#118CDE; height: 30%;'>
                        <input type="submit" name="submit" value="cuisine" style ='-webkit-appearance:none;-moz-appearance:none;appearance:none;height: 100%;width:100%;background-color:#118CDE;font-size:175;'>
               </div>
               <div style = 'background-color:#DEC511; height: 30%;'>
                        <input type="submit" name="submit" value="chambre" style ='-webkit-appearance:none;-moz-appearance:none;appearance:none;height: 100%;width:100%;background-color:#DEC511;font-size:175;'>>
               </div>
               <div style = 'background-color:#1FD078; height: 30%;'>
                        <input type="submit" name="submit" value="bip" style ='-webkit-appearance:none;-moz-appearance:none;appearance:none;height: 100%;width:100%;background-color:#1FD078;font-size:175;'>
               </div>
                <div style = 'background-color:#9683EC; height: 30%;'>
                        <input type="submit" name="submit" value="PC" style ='-webkit-appearance:none;-moz-appearance:none;appearance:none;height: 100%;width:100%;background-color:#9683EC;font-size:175;'>
               </div>
           </form>
           </body>
           </html>
        '''
        #ventilateurs()
        temp = getTemperature()
        self.do_HEAD()
        self.wfile.write(html.format(temp[5:]).encode("utf-8"))

    def do_POST(self):

        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode("utf-8")
        post_data = post_data.split("=")[1]
        #ventilateurs()

        setupGPIO()

        if post_data == 'cuisine':
            #GPIO.output(27, GPIO.HIGH)
            ser = serial.Serial('/dev/ttyACM0',9600, timeout=1)
            ser.flush()
            ser.write(b"on\n")
            time.sleep(1)
            ser.write(b"off\n")
            time.sleep(1)
            ser.write(b"on\n")
            time.sleep(5)
            ser.write(b"off\n")
        elif post_data == 'chambre':
            GPIO.output(27,GPIO.HIGH)
            time.sleep(5)
            GPIO.output(27,GPIO.LOW)
        elif post_data == 'bip':
            GPIO.output(15,GPIO.LOW)
            time.sleep(2)
            GPIO.output(15,GPIO.HIGH)
            time.sleep(1)
            GPIO.output(14,GPIO.LOW)
            time.sleep(2)
            GPIO.output(14,GPIO.HIGH)
        elif post_data == 'PC':
            etat = ping('192.168.1.98')
            if etat == False:
                temps_ini = time.time()
                while etat == False and time.time() - temps_ini  < 15: #set a timeout if the computer is already on but disconnected from the internet
                    etat = ping('192.168.1.98')
                    GPIO.output(23,GPIO.HIGH)
                    time.sleep(1)
                    GPIO.output(23,GPIO.LOW)
            GPIO.output(23,GPIO.LOW)

        print("LED is {}".format(post_data))
        self._redirect('/')  # Redirect back to the root url


# # # # # Main # # # # #

if __name__ == '__main__':
    http_server = HTTPServer((host_name, host_port), MyServer)
    print("Server Starts - %s:%s" % (host_name, host_port))

    try:
        http_server.serve_forever()
    except KeyboardInterrupt:
        http_server.server_close()
