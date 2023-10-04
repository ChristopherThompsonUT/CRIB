try:
  import usocket as socket
except:
  import socket

import network

import esp
esp.osdebug(None)

import gc
gc.collect()

ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid="Test-Access-Point")

while ap.active() == False:
	pass


print("Connection Successful")
print(ap.ifconfig())

from machine import UART

radar_info = UART(2, 115200)

def web_page(breath, heart):
    html = """<html><head><meta name="viewport" content="width=device-width, initial-scale=1"></head>
    <body><h1>Hello, World! This is the ESP32</h1>
    <p>Breathing Rate:""" + str(breath) + """</p> 
    <p>Heart Rate:""" + str(heart) + """</p> 
    </body></html>"""
    return html
  

def web_page_radar_issue():
    html = """<html><head><meta name="viewport" content="width=device-width, initial-scale=1"></head>
    <body><h1>CRIB Interface</h1>
    <p>It appears the Radar isn't working right now. Please check your connection</p> 
    </body></html>"""
    return html

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)

while True:
    #Wait for someone to connect to the webpage hosted at 192.168.4.1
    conn, addr = s.accept()
    print('Got a connection from %s' % str(addr))
    request = conn.recv(1024)
    print('Content = %s' % str(request))
	heart = 0
    breath = 0
    try:
        print(byte_array)
        byte_array = bytearray(radar_info.read())
        for i in range(len(byte_array)):
            if byte_array[i] == 0x81 and byte_array[i+1]==0x02:
                breath = byte_array[i+4]
            if byte_array[i] == 0x85 and byte_array[i+1]==0x02:
                heart = byte_array[i+4]
            if heart != 0 and breath != 0:
                break
    except:
        pass
	#Send the webpage when someone connects
	response = web_page(breath, heart)
	conn.send(response)
	#Stop sending information when the request is complete
	conn.close()