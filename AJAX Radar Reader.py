try:
    import usocket as socket
except:
    import socket

import network
import esp
import gc

esp.osdebug(None)
gc.collect()

ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid="Test-Access-Point")

while not ap.active():
    pass

print("Connection Successful")
print(ap.ifconfig())

from machine import UART

radar_info = UART(2, 115200)



def web_page(breath, heart):
    html = """<!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <script>
            function updateValues() {
                var xhttp = new XMLHttpRequest();
                xhttp.onreadystatechange = function() {
                    if (this.readyState == 4 && this.status == 200) {
                        var data = JSON.parse(this.responseText);
                        document.getElementById("breath").innerHTML = "Breathing Rate: " + data.breath;
                        document.getElementById("heart").innerHTML = "Heart Rate: " + data.heart;
                    }
                };
                xhttp.open("GET", "/data", true);
                xhttp.send();
            }

            // Update values on page load
            window.onload = function() {
                updateValues();
                setInterval(updateValues, 1000); // Update values every second
            };
        </script>
    </head>
    <body>
        <h1>Hello, World! This is the ESP32</h1>
        <p id="breath">Breathing Rate: """ + str(breath) + """</p>
        <p id="heart">Heart Rate: """ + str(heart) + """</p>
    </body>
    </html>"""
    return html

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)

while True:
    conn, addr = s.accept()
    print('Got a connection from %s' % str(addr))
    request = conn.recv(1024)
    print('Content = %s' % str(request))
    try:
        byte_array = bytearray(radar_info.read())
        # Initialize heart and breath variables
        heart = 0 
        breath = 0
        print("entering loop"
        for i in range(len(byte_array)):
            if byte_array[i] == 0x81 and byte_array[i + 1] == 0x02:
                breath = byte_array[i + 4]
            if byte_array[i] == 0x85 and byte_array[i + 1] == 0x02:
                heart = byte_array[i + 4]
            if heart != 0 and breath != 0:
                break
        if 'GET /data' in request:
            # Handle AJAX request for data
            response = '{"breath": ' + str(breath) + ', "heart": ' + str(heart) + '}'
            conn.send('HTTP/1.1 200 OK\n')
            conn.send('Content-Type: application/json\n')
            conn.send('Connection: close\n\n')
            conn.send(response)
        else:
            # Send the webpage when someone connects
            response = web_page(breath, heart)
            conn.send('HTTP/1.1 200 OK\n')
            conn.send('Content-Type: text/html\n')
            conn.send('Connection: close\n\n')
            conn.send(response)
        conn.close()
    except:
        pass


