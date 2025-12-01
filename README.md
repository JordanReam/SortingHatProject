Using V4 of the SortingHatProject code will provide a rough but functional interactive sorting hat. Utilize Thonny IDE and an ESP-32 running MicroPython to implement the script. 
Wire GPIO 16 and 17 to be configured as the RX and TX output for the DFPlayer mini.
Wire 5V directly to the DFPlayer and wire both the ESP-32 GND and the DFPlayer GND to the breadboard GND.
The SPK1 and SPK2 pins on the DFPlayer should be wired to two seperate rails.
The speaker power and ground should be wired on the same rail as their counterpart. (Repeat this process for a second speaker)
The SG90 Servo motor should be wired to GPIO 15 and the power and ground rails.
The power and ground rails will be powered by an MB102 Power Supply. This can be plugged in using a wall power connector.
Modify the WiFi setup section to match your network SSID and password. 
You can then use USB-C power from either your laptop or from a power bank to power the hat. 
To do the sorting quiz, check the Thonny REPL for the link to the webserver and use that to connect.
