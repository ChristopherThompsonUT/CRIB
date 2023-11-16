try:
  import usocket as socket
except:
  import socket

import network
from machine import ADC, Pin
import machine 
import esp
import uselect as select
esp.osdebug(None)

import gc
gc.collect()

import time 

def monitor():
  print("Monitoring for Breath and Heart Rate")
  breath = None
  heart = None
  for i in range(4):
    time.sleep(3)
    try:
      print(x)
      x = radar_info.read()
      byte_array = bytearray(x)
      for i in range(len(byte_array)):
        if byte_array[i] == 0x81 and byte_array[i+1] == 0x02:
          breath = byte_array[i+4]
        if byte_array[i] == 0x85 and byte_array[i+1] == 0x02:
          heart = byte_array[i+4]
    except:
      pass
          
  if breath == None and heart == None:
    pass
        #Raise the Alarm
    #speaker.value(1)  

def client_handler(conn, init_array, mat_in_arr):
  print('Got a connection from %s' % str(addr))
  request = conn.recv(1024)
  print('Content = %s' % str(request))
  heart = 0
  breath = 0

  ar_array = [0 for i in range(32)]

  for i, j in enumerate(mat_in_arr):
    j.value(1)
    time.sleep(0.1)
    ar_array[4 * i] = adc1.read()
    ar_array[4 * i + 1] = adc2.read()
    ar_array[4 * i + 2] = adc3.read()
    ar_array[4 * i + 3] = adc4.read()
    j.value(0)

  for i in range(len(init_array)):
    if init_array[i]==0:
      init_array[i]=1
    
  print("AR_ARRAY")
  print(ar_array)
  # find the percent difference from the initialization to the new reading
  dif_array = [ar_array[i] / init_array[i] for i in range(32)]

  # create the output for the webpage with 2 decimal place accuracy
  round_dif = [round(i, 1) for i in dif_array]

  # reset the values of the ouradtpu3t array
  out = [0 for i in range(32)]
  jj = 0
  fill = 0.2

  # find the index of the "heaviest value" and set the output array to the same
  low = round_dif.index(min(round_dif))
  out[low] = 1 - round_dif[low]

  while jj < 32:
    if jj == low:
      # Define the neighbors of the current patch
      neighbors = [jj - 1, jj + 1, jj - 4, jj + 4, jj - 3, jj + 3, jj - 5, jj + 5]

      # Update the neighbors based on their position
      for neighbor in neighbors:
        # Check if neighbor is not on the edge
        not_on_left_edge = ((jj - 3) % 4 != 0) or neighbor not in [jj + 1, jj - 3, jj + 5]
        not_on_right_edge = (jj % 4 != 0) or neighbor not in [jj - 1, jj + 3, jj - 5]
        not_on_top_row = jj >= 4 or neighbor not in [jj - 4, jj - 3, jj - 5]
        not_on_bottom_row = jj < 28 or neighbor not in [jj + 4, jj + 3, jj + 5]

        if not_on_left_edge and not_on_right_edge and not_on_top_row and not_on_bottom_row and (0 <= neighbor < 32):
          out[neighbor] += 0.2
    else:
          # Reinitialize every other patch to prevent noise
      init_array[jj] = ar_array[jj]
    jj += 1

    for row in (range(0, len(out), 4)):
      indices = reversed(range(row, row + 4))
      print(", ".join([str(out[i]) for i in indices]))

      print("\n")
      print(low)
      print("\n")
      crib_flag=False
      try:
        x = radar_info.read()
        byte_array = bytearray(x)
        for i in range(len(byte_array)):
          if byte_array[i] == 0x81 and byte_array[i+1] == 0x02:
            breath = byte_array[i+4]
          if byte_array[i] == 0x85 and byte_array[i+1] == 0x02:
            heart = byte_array[i+4]
          if heart != 0 and breath != 0:
            break
      except:
          pass

      if x is None:
        response = web_page(0, 0, out)
      elif crib_flag:
        response=web_page_mat_issue()
      else:
        response = web_page(breath, heart, out)
      conn.send(response)
      conn.close()

  

ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid="Test-Access-Point")

while ap.active() == False:
	pass


print("Connection Successful")
print(ap.ifconfig())

from machine import UART

radar_info = UART(2, baudrate=115201, bits=8, parity=None, stop=1, tx=16, rx =17)

def web_page(breath, heart, out):
    html = """<html><head><meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
			#main_page {
				background-color: #4b4945;
				font-family:'tradegothiclt-light',sans-serif;
				color: #999999;
				text-align:center;
			}
			
			.center {margin-left: auto;margin-right: auto;}


			.patch {
			color: transparent;
			text-shadow: 0 0 0 #7f56c5;
			font-size:40pt;
			
			}
		</style></head>
    <body id = "main_page"><h1 style="color:#cccccc">CRIB Interface</h1>
    <p id="breath" >Breathing Rate: """ + str(breath) + """</p> 
    <p id="heart">Heart Rate:""" + str(heart) + """</p>
    <table class="center" style="background-color:#000000;color:7f56c5"><tr><td>
    <span class="patch" style="opacity:"""+str(out[0])+""";">&#11035;</span></td><td><span class="patch" style=opacity:"""+str(out[1])+""";">&#11035;</span></td><td><span class="patch" style="opacity:"""+str(out[2])+""";">&#11035;</span></td><td><span class="patch" style="opacity:"""+str(out[3])+""";">&#11035;</span></td>
			</tr>
			<tr>
				<td><span class="patch" style="opacity:"""+str(out[4])+""";">&#11035;</span></td><td><span class="patch" style="opacity:"""+str(out[5])+""";">&#11035;</span></td><td><span class="patch" style="opacity:"""+str(out[6])+""";">&#11035;</span></td><td><span class="patch" style="opacity:"""+str(out[7])+""";">&#11035;</span></td>
		</tr>
			<tr>
				<td><span class="patch" style="opacity:"""+str(out[8])+""";">&#11035;</span></td><td><span class="patch" style="opacity:"""+str(out[9])+""";">&#11035;</span></td><td><span class="patch" style="opacity:"""+str(out[10])+""";">&#11035;</span></td><td><span class="patch" style="opacity:"""+str(out[11])+""";">&#11035;</span></td>
		</tr>
			<tr>
				<td><span class="patch" style="opacity:"""+str(out[12])+""";">&#11035;</span></td><td><span class="patch" style="opacity:"""+str(out[13])+""";">&#11035;</span></td><td><span class="patch" style="opacity:"""+str(out[14])+""";">&#11035;</span></td><td><span class="patch" style="opacity:"""+str(out[15])+""";">&#11035;</span></td>
		</tr>
			<tr>
				<td><span class="patch" style="opacity:"""+str(out[16])+""";">&#11035;</span></td><td><span class="patch" style="opacity:"""+str(out[17])+""";">&#11035;</span></td><td><span class="patch" style="opacity:"""+str(out[18])+""";">&#11035;</span></td><td><span class="patch" style="opacity:"""+str(out[19])+""";">&#11035;</span></td>
		</tr>
			<tr>
				<td><span class="patch" style="opacity:"""+str(out[20])+""";">&#11035;</span></td><td><span class="patch" style="opacity:"""+str(out[21])+""";">&#11035;</span></td><td><span class="patch" style="opacity:"""+str(out[22])+""";">&#11035;</span></td><td><span class="patch" style="opacity:"""+str(out[23])+""";">&#11035;</span></td>
		</tr>
			<tr>
				<td><span class="patch" style="opacity:"""+str(out[24])+""";">&#11035;</span></td><td><span class="patch" style="opacity:"""+str(out[25])+""";">&#11035;</span></td><td><span class="patch" style="opacity:"""+str(out[26])+""";">&#11035;</span></td><td><span class="patch" style="opacity:"""+str(out[27])+""";">&#11035;</span></td>
		</tr>
			<tr>
				<td><span class="patch" style="opacity:"""+str(out[28])+""";">&#11035;</span></td><td><span class="patch" style="opacity:"""+str(out[29])+""";">&#11035;</span></td><td><span class="patch" style="opacity:"""+str(out[30])+""";">&#11035;</span></td><td><span class="patch" style="opacity:"""+str(out[31])+""";">&#11035;</span></td>
		</tr>
		
		
		</table>

    </body></html>"""
    #TODO Add baby alert for warning close to edge
    return html
  

def web_page_radar_issue():
    html = """<html><head><meta name="viewport" content="width=device-width, initial-scale=1"><style>
			#main_page {
				background-color: #4b4945;
				font-family:'tradegothiclt-light',sans-serif;
				color: #999999;
				text-align:center;
			}
			
			.center {
			  margin-left: auto;
			  margin-right: auto;
			}


			.patch {
			color: transparent;
			text-shadow: 0 0 0 #7f56c5;
			font-size:20pt;
			
			}
		</style></head>
    <body id="main_page"><h1 style="color:#cccccc">CRIB Interface</h1>
    <p>It appears the Radar isn't working right now. Please check your connection</p> 
    </body></html>"""   
    return html

def web_page_mat_issue():
    html = """<html><head><meta name="viewport" content="width=device-width, initial-scale=1"><style>
			#main_page {
				background-color: #4b4945;
				font-family:'tradegothiclt-light',sans-serif;
				color: #999999;
				text-align:center;
			}
			
			.center {
			  margin-left: auto;
			  margin-right: auto;
			}


			.patch {
			color: transparent;
			text-shadow: 0 0 0 #7f56c5;
			font-size:20pt;
			
			}
		</style></head>
    <body id="main_page"><h1 style="color:#cccccc">CRIB Interface</h1>
    <p>It appears the Pressure Sensing Mat isn't working right now. Please check your connections</p> 
    </body></html>"""   
    return html

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)

mat_in1 = Pin(19, Pin.OUT)
mat_in2 = Pin(23, Pin.OUT)
mat_in3 = Pin(18, Pin.OUT)
mat_in4 = Pin(5, Pin.OUT)
mat_in5 = Pin(4, Pin.OUT)
mat_in6 = Pin(0, Pin.OUT)
mat_in7 = Pin(2, Pin.OUT)
mat_in8 = Pin(15, Pin.OUT)

mat_in_arr = [mat_in1,mat_in2,mat_in3,mat_in4,mat_in5,mat_in6,mat_in7,mat_in8]

adc1 = ADC(Pin(33, mode=Pin.IN))
adc2 = ADC(Pin(32, mode=Pin.IN))
adc3 = ADC(Pin(35, mode=Pin.IN))
adc4 = ADC(Pin(34, mode=Pin.IN))
adc1.atten(ADC.ATTN_11DB)
adc2.atten(ADC.ATTN_11DB)
adc3.atten(ADC.ATTN_11DB)
adc4.atten(ADC.ATTN_11DB)

speaker = Pin(13, Pin.OUT)

led = Pin(22, Pin.OUT)
led.value(0)

init_array = [0 for i in range(32)]
# init0 = init1 = init2 = init3 = init4 = init5 = init6 = init7 = init8 = init9 = init10 = init11 = init12 = init13 = init14 = init15 = init16 = init17 = init18 = init19 = init20 = init21 = init22 = init23 = init24 = init25 = init26 = init27 = init28 = init29 = init30 = init31 = 0

# initialization voltage on the patches
for i,j in enumerate(mat_in_arr):
  j.value(1)
  time.sleep(0.1)
  init_array[4*i]= adc1.read()
  init_array[4*i+1]= adc2.read()
  init_array[4*i+2]= adc3.read()
  init_array[4*i+3]= adc4.read()
  j.value(0)


while True:
  led.value(0)
  r, w, err = select.select((s,), (), (), 1)

  if r:
    for readable in r:
      conn, addr = s.accept()
    try:
      client_handler(conn, init_array, mat_in_arr)
    except OSError as e:
      pass
      
  monitor()
