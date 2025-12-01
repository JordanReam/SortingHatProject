import network
import socket
import ure
import time
from machine import UART, Pin, PWM

# WiFi Setup
ssid = "REDACTED_SSID"
password = "REDACTED_PASSWORD"

wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(ssid, password)

print("Connecting to WiFi...")
while not wifi.isconnected():
    time.sleep(0.3)
print("Connected:", wifi.ifconfig()[0])

# DFPlayer Setup
# DFPlayer on UART2 (TX=17, RX=16)
uart = UART(2, baudrate=9600, tx=17, rx=16)

def df_send(cmd, param, feedback=0x00):
    high = (param >> 8) & 0xFF
    low = param & 0xFF
    msg = bytearray([
        0x7E, 0xFF, 0x06, cmd, feedback, high, low, 0xEF
    ])
    uart.write(msg)

def set_volume(level):
    level = max(0, min(30, level))
    df_send(0x06, level)
    print("Volume set to:", level)

def play_mp3(track_number):
    df_send(0x03, track_number)
    print("Playing track:", track_number)

time.sleep(0.5)
set_volume(30)

# Servo Setup
# Servo on GPIO 15
servo = PWM(Pin(15), freq=50)

def set_servo_angle(angle):
    # Map 0–180° to ~0.5–2.5ms pulse (duty 26–128 on ESP32)
    duty = int((angle / 180.0) * 102 + 26)
    servo.duty(duty)

# Track 5 (Intro) Mouth Sync Routine for opening webpage
def speak_intro_mouth():
    CLOSED = 90
    OPEN = 130

    # Allow page to load and everything to settle
    PRELOAD_DELAY = 0.75
    set_servo_angle(CLOSED)
    time.sleep(PRELOAD_DELAY)

    # Start intro audio
    play_mp3(5)

    # Approximate peak windows from INTRO.mp3 analysis
    flap_windows = [
        (0.15, 0.35),
        (0.45, 0.70),
        (0.85, 1.05),
        (1.20, 1.45),
        (1.55, 1.80),
        (2.00, 2.25)
    ]

    AUDIO_LENGTH = 2.69
    start = time.ticks_ms()

    while True:
        t = (time.ticks_ms() - start) / 1000.0
        if t > AUDIO_LENGTH:
            break

        mouth_open = any(a <= t <= b for (a, b) in flap_windows)

        if mouth_open:
            set_servo_angle(OPEN)
        else:
            set_servo_angle(CLOSED)

        time.sleep(0.03)

    set_servo_angle(CLOSED)

# Servo and Audio Sync Routines for House Announcements

def speak_gryffindor_mouth():
    # Track 1
    CLOSED = 90
    OPEN = 130

    flap_windows = [
        (0.10, 0.28),
        (0.32, 0.48),
        (0.62, 0.82),
        (1.00, 1.22)
    ]

    AUDIO_LENGTH = 1.44
    start = time.ticks_ms()

    while True:
        t = (time.ticks_ms() - start) / 1000.0
        if t > AUDIO_LENGTH:
            break

        mouth_open = any(a <= t <= b for (a, b) in flap_windows)

        if mouth_open:
            set_servo_angle(OPEN)
        else:
            set_servo_angle(CLOSED)

        time.sleep(0.03)

    set_servo_angle(CLOSED)


def speak_hufflepuff_mouth():
    # Track 2
    CLOSED = 90
    OPEN = 130

    flap_windows = [
        (0.12, 0.32),
        (0.50, 0.75),
        (1.05, 1.32)
    ]

    AUDIO_LENGTH = 1.62
    start = time.ticks_ms()

    while True:
        t = (time.ticks_ms() - start) / 1000.0
        if t > AUDIO_LENGTH:
            break

        mouth_open = any(a <= t <= b for (a, b) in flap_windows)

        if mouth_open:
            set_servo_angle(OPEN)
        else:
            set_servo_angle(CLOSED)

        time.sleep(0.03)

    set_servo_angle(CLOSED)


def speak_ravenclaw_mouth():
    # Track 3
    CLOSED = 90
    OPEN = 130

    flap_windows = [
        (0.10, 0.27),
        (0.40, 0.63),
        (0.92, 1.15),
        (1.55, 1.85)
    ]

    AUDIO_LENGTH = 2.09
    start = time.ticks_ms()

    while True:
        t = (time.ticks_ms() - start) / 1000.0
        if t > AUDIO_LENGTH:
            break

        mouth_open = any(a <= t <= b for (a, b) in flap_windows)

        if mouth_open:
            set_servo_angle(OPEN)
        else:
            set_servo_angle(CLOSED)

        time.sleep(0.03)

    set_servo_angle(CLOSED)


def speak_slytherin_mouth():
    # Track 4
    CLOSED = 90
    OPEN = 130

    flap_windows = [
        (0.08, 0.22),
        (0.38, 0.55),
        (0.78, 1.00)
    ]

    AUDIO_LENGTH = 1.25
    start = time.ticks_ms()

    while True:
        t = (time.ticks_ms() - start) / 1000.0
        if t > AUDIO_LENGTH:
            break

        mouth_open = any(a <= t <= b for (a, b) in flap_windows)

        if mouth_open:
            set_servo_angle(OPEN)
        else:
            set_servo_angle(CLOSED)

        time.sleep(0.03)

    set_servo_angle(CLOSED)

# Questions and Answers Setup
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
     "D": ("Making someone's day better", "huff")},
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

scores = {"gryff": 0, "slyth": 0, "rav": 0, "huff": 0}
current_question = 0

# HTML Page Generation
def make_question_page(index):
    q = questions[index]
    html = f"""
    <html><head><title>Sorting Hat Quiz</title></head>
    <body style='text-align:center; font-family:Arial; margin-top:40px;'>
        <style>
        body {{
            background-color: #f5f5f5;
            font-family: Arial;
        }}
        button {{
            width: 260px;
            height: 55px;
            margin: 12px;
            font-size: 19px;
            border-radius: 10px;
            background-color: #FFD700;
            color: #8B0000;
            font-weight: bold;
            border: none;
            cursor: pointer;
        }}
        button:hover {{
            background-color: #FFA500;
            color: white;
        }}
        </style>
        <h2>{q['q']}</h2>
        <button onclick="location.href='/answer?choice=A'">{q['A'][0]}</button><br>
        <button onclick="location.href='/answer?choice=B'">{q['B'][0]}</button><br>
        <button onclick="location.href='/answer?choice=C'">{q['C'][0]}</button><br>
        <button onclick="location.href='/answer?choice=D'">{q['D'][0]}</button>
    </body></html>
    """
    return html

def final_result(winner):
    # Map houses to track numbers
    house_track = {"gryff": 1, "huff": 2, "rav": 3, "slyth": 4}
    html = "<html><body><h1>The Hat Shall Speak!</h1></body></html>"
    return html, house_track[winner]

# Web Server initialization
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(5)
print("Server running at http://" + wifi.ifconfig()[0])

# Main webpage loop
while True:
    conn, addr = s.accept()
    request = conn.recv(1024).decode()

    if "GET /favicon.ico" in request:
        conn.send("HTTP/1.1 404 Not Found\r\n\r\n")
        conn.close()
        continue

    # Matches quiz answers to servo and audio sync
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

            # Play house announcement
            play_mp3(track_num)

            # Mouth movement per house track
            if track_num == 1:
                speak_gryffindor_mouth()
            elif track_num == 2:
                speak_hufflepuff_mouth()
            elif track_num == 3:
                speak_ravenclaw_mouth()
            elif track_num == 4:
                speak_slytherin_mouth()

            # Reset quiz
            current_question = 0
            scores = {"gryff": 0, "slyth": 0, "rav": 0, "huff": 0}
            continue

        conn.send("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n")
        conn.send(make_question_page(current_question))
        conn.close()
        continue

    # Ensures webpage loads with intro audio and mouth movement and values are nulled at start
    if "GET /" in request:

        if current_question == 0:
            scores = {"gryff": 0, "slyth": 0, "rav": 0, "huff": 0}

        # Send landing page 
        conn.send("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n")
        conn.send(make_question_page(current_question))
        conn.close()

        # After sending page, play intro & move mouth
        speak_intro_mouth()

        continue

