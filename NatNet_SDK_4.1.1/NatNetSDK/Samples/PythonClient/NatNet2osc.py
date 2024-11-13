from NatNetClient import NatNetClient
from pythonosc import udp_client


def receive_new_pos(rigid_body_list):
    #pass
    print(f"found rigid_body count: {len(rigid_body_list)}")
    for rigid_body in rigid_body_list:
       print(f"id: {rigid_body.id_num}")
       print(f"pos: {rigid_body.pos[0]}, {rigid_body.pos[1]}, {rigid_body.pos[2]}")
    
    # x, y, z = rigid_body_list[0].pos[0], rigid_body_list[0].pos[1], rigid_body_list[0].pos[2]
    # client.send_message("/track/1/xyz", tuple([x, y, z]))


if __name__ == "__main__":
    # holophonix client
    client = udp_client.SimpleUDPClient("10.255.255.60", 4003)

    # motive client
    streaming_client = NatNetClient()

    streaming_client.pos_listener = receive_new_pos
    streaming_client.run()