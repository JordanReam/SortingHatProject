import network
import socket
import ure
import time
from machine import UART

# ---- WIFI ----
ssid = "ThisSaysWithPulp"
password = "0r@ng3ju1c3"

# Connect to WiFi
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(ssid, password)

# Wait for connection
print("Connecting to WiFi...")
while not wifi.isconnected():
    time.sleep(0.3)

#Print Connection Info
print("Connected:", wifi.ifconfig()[0])

# ---- DFPLAYER SETUP (UART2 on GPIO17/16) ----
uart = UART(2, baudrate=9600, tx=17, rx=16)

def df_send(cmd, param, feedback=0x00):
    high = (param >> 8) & 0xFF
    low = param & 0xFF
    msg = bytearray([
        0x7E, 0xFF, 0x06, cmd, feedback, high, low, 0xEF
    ])
    uart.write(msg)

# DFPlayer Volume Control
def set_volume(level):
    if level < 0: level = 0
    if level > 30: level = 30
    df_send(0x06, level)
    print("Volume set to:", level)

# DFPlayer Play Command
def play_mp3(track_number):
    df_send(0x03, track_number)
    print("Playing track:", track_number)

# ---- Set volume at startup ----
time.sleep(0.5)
set_volume(30)

# Questions and Scoring
questions = [
    {"q": "When faced with something new, what motivates you most?",
     "A": ("The thrill of trying it", "gryff"),
     "B": ("The chance to get ahead", "slyth"),
     "C": ("Understanding how it works", "rav"),
     "D": ("Helping someone through it", "huff")},
    {"q": "What do you value most in others?",
     "A": ("Courage to be honest", "gryff"),
     "B": ("Drive to improve", "slyth"),
     "C": ("Thoughtful insight", "rav"),
     "D": ("Reliability and warmth", "huff")},
    {"q": "When making a decision, you rely mostly on:",
     "A": ("Gut instinct", "gryff"),
     "B": ("Strategy and advantage", "slyth"),
     "C": ("Logic and evidence", "rav"),
     "D": ("What feels kind and fair", "huff")},
    {"q": "In a group project, you usually:",
     "A": ("Take charge without fear", "gryff"),
     "B": ("Organize for best results", "slyth"),
     "C": ("Study details and refine ideas", "rav"),
     "D": ("Make sure everyone gets along", "huff")},
    {"q": "Which situation feels most rewarding?",
     "A": ("Standing up for someone", "gryff"),
     "B": ("Achieving something difficult", "slyth"),
     "C": ("Solving a puzzle", "rav"),
     "D": ("Making someones day better", "huff")},
    {"q": "What bothers you the most?",
     "A": ("Seeing unfairness ignored", "gryff"),
     "B": ("Wasted potential", "slyth"),
     "C": ("Misinformation", "rav"),
     "D": ("People feeling excluded", "huff")},
    {"q": "How do you face challenges?",
     "A": ("Head-on, no hesitation", "gryff"),
     "B": ("Plan, adapt, push forward", "slyth"),
     "C": ("Analyze and break it down", "rav"),
     "D": ("Stay patient and steady", "huff")},
    {"q": "What type of success feels best?",
     "A": ("One that took bravery", "gryff"),
     "B": ("One that built your future", "slyth"),
     "C": ("One that taught you something", "rav"),
     "D": ("One that helped someone else", "huff")},
    {"q": "Your ideal role in a group is:",
     "A": ("The one who steps up", "gryff"),
     "B": ("The one who makes things happen", "slyth"),
     "C": ("The one who solves problems", "rav"),
     "D": ("The one who keeps things steady", "huff")},
    {"q": "What do you wish people noticed about you?",
     "A": ("Your willingness to act", "gryff"),
     "B": ("Your inner drive", "slyth"),
     "C": ("Your insightfulness", "rav"),
     "D": ("Your caring nature", "huff")}
]

scores = {"gryff":0, "slyth":0, "rav":0, "huff":0}
current_question = 0

# HTML Generation
def make_question_page(index):
    q = questions[index]
    html = f"""
    <html><head><title>Sorting Hat Quiz</title></head>
    <body style='text-align:center; font-family:Arial; margin-top:40px;'>
	    <style>
    body {{
        font-family: Arial; 
        text-align: center; 
        margin-top: 40px;
        background-color: #f5f5f5;
    }}
    button {{
        width: 260px; 
        height: 55px; 
        margin: 12px;
        font-size: 19px; 
        border: none; 
        border-radius: 10px;
        background-color: #FFD700; /* Gold */
        color: #8B0000;           /* Dark Red */
        font-weight: bold;
        transition: 0.3s;
        cursor: pointer;
    }}
    button:hover {{
        background-color: #FFA500; /* Darker gold */
        color: white;
    }}
    </style>
    </head><body>
        <h2>{q['q']}</h2>
        <button onclick="location.href='/answer?choice=A'">{q['A'][0]}</button><br>
        <button onclick="location.href='/answer?choice=B'">{q['B'][0]}</button><br>
        <button onclick="location.href='/answer?choice=C'">{q['C'][0]}</button><br>
        <button onclick="location.href='/answer?choice=D'">{q['D'][0]}</button>
    </body></html>
    """
    return html
#Page displayed at the end of the quiz
def final_result(winner):
    house_track = {"gryff":1, "huff":2, "rav":3, "slyth":4}
    html = "<html><body><h1>The Hat Shall Speak!</h1>"
    return html, house_track[winner]

addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(5)
print("Server running at http://" + wifi.ifconfig()[0])

while True:
    conn, addr = s.accept()
    request = conn.recv(1024).decode()

    if "GET /favicon.ico" in request:
        conn.send("HTTP/1.1 404 Not Found\r\n\r\n")
        conn.close()
        continue

    # ANSWER HANDLING 
    match = ure.search("GET /answer\\?choice=([A-D])", request)
    if match:
        choice = match.group(1)
        house_key = questions[current_question][choice][1]
        scores[house_key] += 1
        current_question += 1

        if current_question >= len(questions):
            winner = max(scores, key=scores.get)
            html_page, track_num = final_result(winner)

            conn.send("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n")
            conn.send(html_page)
            conn.close()

            play_mp3(track_num)

            current_question = 0
            scores = {"gryff":0,"slyth":0,"rav":0,"huff":0}
            continue

        conn.send("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n")
        conn.send(make_question_page(current_question))
        conn.close()
        continue

    # MAIN PAGE
    if "GET /" in request:

        # Introduction Track is played when webpage is opened!
        play_mp3(5)
        time.sleep(0.2)

        if current_question == 0:
            scores = {"gryff":0,"slyth":0,"rav":0,"huff":0}

        conn.send("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n")
        conn.send(make_question_page(current_question))
        conn.close()
        continue
