import socket
import struct
import time
import threading
from pynput.mouse import Listener
import numpy as np
from pythonosc import udp_client


def map_range(value, old_min, old_max, new_min, new_max):
    return((value - old_min) / (old_max - old_min)) * (new_max - new_min) + new_min

def map_point_2_holophonix(x, y, z):
    x = -x
    y = z
    z = y
    return x, y, z

def receive():
    while True:
        data, addr = sock.recvfrom(1024)
        values = struct.unpack("ffff", data)
        # print(f"Received message: {values} from {addr}")

        send_2_holophonix(values)

def send_2_holophonix(values):
    global left_button_held
    if values == None:
        return
    
    x, y, z, dist = values[0], values[1], values[2], values[3]
    x, y, z = map_point_2_holophonix(x, y, z)

    # dist range: 0 - 1
    # reverb range: 0 - 10
    reverb = map_range(dist, 0, 1, 0, 15)
    holophonix_client.send_message("/reverb/2/tr0", reverb)

    if left_button_held:
        holophonix_client.send_message("/track/1/xyz", tuple([x, y, z]))
    else:
        holophonix_client.send_message("/track/1/xyz", tuple([0.1, 0.1, 0.1]))
        
def on_click(x, y, button, pressed):
    global left_button_held
    if pressed:
        if button.name == "left":
            left_button_held = True
            print(f"stream = {left_button_held}")

        elif button.name == "right":
            left_button_held = False
            print(f"stream = {left_button_held}")


if __name__ == "__main__":
    # init udp
    UDP_IP = "127.0.0.1"
    UDP_PORT = 12345
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    print(f"Listening on {UDP_IP}: {UDP_PORT}...")

    # holophonix client
    holophonix_client = udp_client.SimpleUDPClient("10.255.255.60", 4003)

    # receive udp
    receice_thread = threading.Thread(target=receive)
    receice_thread.start()

    # set up listener to for mouse click
    left_button_held = True
    listener = Listener(on_click=on_click)
    listener.start()


    # main thread
    running = True
    while running:
        print("running")
        user_input = input('Enter q to quit')
        if user_input == "q":
            sock.close()
            # receice_thread.join()
            running = False
            break



