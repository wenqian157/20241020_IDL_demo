import socket
import struct
import pygame
import time
import sys
import threading
from pynput.mouse import Listener
import numpy as np
from pythonosc import udp_client

def receive():
    while True:
        data, addr = sock.recvfrom(1024)
        values = struct.unpack("!ffff", data)
        print(f"Received message: {values} from {addr}")

        send_2_holophonix(values)

def send_2_holophonix(values):
    if values == None:
        return
    
    x, y, z, dist = values[0], values[1], values[2], values[3]
    
    holophonix_client.send_message("/track/1/xyz", tuple([x, y, z]))
    # holophonix_client.send_message("track", dist)
    # holophonix_client.send_message("track", dist)
    

if __name__ == "__main__":
    # init udp
    UDP_IP = "127.0.0.1"
    UDP_PORT = 5006
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    print(f"Listening on {UDP_IP}: {UDP_PORT}...")

    # holophonix client
    holophonix_client = udp_client.SimpleUDPClient("10.255.255.60", 4003)

