from pythonosc import udp_client
holophonix_client = udp_client.SimpleUDPClient("10.255.255.60", 4003)
holophonix_client.send_message("/reverb/2/tr0", 1)