#Imports necessary libraries to allow internet connectivity, timing, parsing, and allowing web requests.
import network
import socket
import ure
import time

# Wifi Connection Details.
ssid = "REDACTED"
password = "REDACTED"

#Configure Station Interface 
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(ssid, password)


#Connection Status
print("Connecting to WiFi...")
while not wifi.isconnected():
    time.sleep(0.3)

print("Connected!")
print("ESP32 IP address:", wifi.ifconfig()[0])


# Scary HTML Page that displays a heading and creates four buttons.
html = """<!DOCTYPE html>
<html>
<head>
<title>What is Your House? </title>
<style>
    body { font-family: Arial; text-align: center; margin-top: 40px; }
    button {
        width: 250px; height: 50px; margin: 10px;
        font-size: 20px;
        background-color: #4CAF50; color:white;
        border:none; border-radius: 8px;
    }
</style>
</head>
<body>
<h2>What characteristic do you envy?</h2>

<button onclick="location.href='/answer?choice=A'">Bravery</button><br>
<button onclick="location.href='/answer?choice=B'">Ambition</button><br>
<button onclick="location.href='/answer?choice=C'">Wisdom</button><br>
<button onclick="location.href='/answer?choice=D'">Kindness</button>

</body>
</html>
"""


# Initializes webserver and binds socket.
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(5)
print("Web server running at http://" + wifi.ifconfig()[0])

while True:
    conn, addr = s.accept()
    request = conn.recv(1024).decode()
    print("Client:", addr)
    print("Request:", request)

    # Parse answer
    match = ure.search(r"GET /answer\\?choice=([A-D])", request)
    if match:
        choice = match.group(1)
        print("User selected:", choice)

        conn.send("HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\n")
        conn.send("You selected: " + choice)
        conn.close()
        continue

    # Serve main page
    if "GET / " in request or "GET /HTTP" in request:
        conn.send("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n")
        conn.send(html)

    conn.close()