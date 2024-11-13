import socket
import struct
import pygame
import time
import sys
import threading

def draw():
    x, y = 200, 200
    screen.fill((0, 0, 0))

    point_color = (0, 0, 255)
    point_radius = 5

    pygame.draw.circle(screen, point_color, (x, y), point_radius)
    pygame.display.flip()

def receive():
    data, addr = sock.recvfrom(8)
    values = struct.unpack("!ff", data)
    print(f"Received message: {values} from {addr}")

def listen_for_input():
    global user_input
    user_input = None
    while True:
        user_input = input('Enter any key to quit')

def main_loop():
    global user_input

    input_thread = threading.Thread(target=listen_for_input)
    input_thread.daemon = True
    input_thread.start()

    running = True
    while running:
        if user_input:
            user_input = None

            # quit
            sock.shutdown()
            pygame.quit()
            sys.exit()
            break

        else:
            # receive motive 
            receive()
            draw()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False


if __name__ == "__main__":
    
    # init udp
    UDP_IP = "127.0.0.1"
    UDP_PORT = 5005
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    print(f"Listening on {UDP_IP}: {UDP_PORT}...")

    # init draw
    pygame.init()
    window_size = (800, 500)
    screen = pygame.display.set_mode(window_size)
    pygame.display.set_caption("draw a 2d point")

    main_loop()

