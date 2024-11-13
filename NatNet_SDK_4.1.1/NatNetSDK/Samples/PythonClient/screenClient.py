import socket
import struct
import pygame
import time
import sys

def draw():
    pygame.init()

    window_size = (800, 500)
    screen = pygame.display.set_mode(window_size)
    pygame.display.set_caption("draw a 2d point")

    x, y = 200, 200

    

def receive():
    data, addr = sock.recvfrom(8)
    values = struct.unpack("!ff", data)
    print(f"Received message: {values} from {addr}")


if __name__ == "__main__":
    UDP_IP = "127.0.0.1"
    UDP_PORT = 5005

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))

    print(f"Listening on {UDP_IP}: {UDP_PORT}...")

    is_looping = True
    time.sleep(1)

    pygame.init()

    window_size = (800, 500)
    screen = pygame.display.set_mode(window_size)
    pygame.display.set_caption("draw a 2d point")

    x, y = 200, 200

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((0, 0, 0))

        point_color = (0, 0, 255)
        point_radius = 5

        pygame.draw.circle(screen, point_color, (x, y), point_radius)
        pygame.disply.flip()

    pygame.quit()
    sys.exit()

    # while True:
    #     data, addr = sock.recvfrom(8)
    #     values = struct.unpack("!ff", data)
    #     print(f"Received message: {values} from {addr}")
    #     if(input()):
    #         break
    #     else:
    #         continue

    # while is_looping:

    #     inchars = input('Enter q to quit')
    #     if len(inchars)>0:
    #         c1 = inchars[0].lower()
    #         if c1 == 'q' :
    #             is_looping = False
    #             sock.shutdown()
    #             break

        

