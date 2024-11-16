from NatNetClient import NatNetClient
from compas.geometry import Frame, Quaternion, Transformation

from pythonosc import udp_client

T= Transformation.from_matrix([
	[0, 0, -1, 0],
    [-1, 0, 0, 0],
	[0, 1, 0, 0],
	[0, 0, 0, 1]
])

# holophonix client
client = udp_client.SimpleUDPClient("10.255.255.60", 4003)

# This is a callback function that gets connected to the
# NatNet client and called once per mocap frame.


def map_range(value, from_min, from_max, to_min, to_max):
    """Performs a linear interpolation of a value within the range of [from_min,
        from_max] to another range of [to_min, to_max].
    """
    from_range = from_max - from_min
    to_range = to_max - to_min
    value_scaled = (value - from_min) / float(from_range)
    return to_min + (value_scaled * to_range)


def clamp(value, min_value, max_value):
    return max(min(value, max_value), min_value)


def receiveNewFrame(frameNumber,
                    markerSetCount,
                    unlabeledMarkersCount,
                    rigidBodyCount,
                    skeletonCount,
                    labeledMarkerCount,
                    timecode,
                    timecodeSub,
                    timestamp,
                    isRecording,
                    trackedModelsChanged):
    # print("Received frame", frameNumber)
    pass

# This is a callback function that gets connected to the
# NatNet client. It is called once per rigid body per frame.


def receiveRigidBodyFrame(id, position, rotation):
    # Guitar
    if id == 1:
        x, y, z, w = rotation
        frame = Frame.from_quaternion(Quaternion(w, x, y, z), point=position)

        # transform frame to fit the coordinate system of holophonix
        frame_t = frame.transformed(T)
        # print(id, frame_t)
        
        print( "Received frame for rigid body", id, position, rotation)
        client.send_message("/track/1/xyz", tuple(list(frame_t.point)))
    # Vocal
    elif id==2:
        x, y, z, w = rotation
        frame = Frame.from_quaternion(Quaternion(w, x, y, z), point=position)

        # transform frame to fit the coordinate system of holophonix
        frame_t = frame.transformed(T)
        # print(id, frame_t)

        print( "Received frame for rigid body", id, position, rotation)
        client.send_message("/track/2/xyz", tuple(list(frame_t.point)))


def change_room_size(id, position, rotation):
    if id == 3:
        x, y, z, w = rotation
        frame = Frame.from_quaternion(Quaternion(w, x, y, z), point=position)

        # transform frame to fit the coordinate system of holophonix
        frame_t = frame.transformed(T)

        v = clamp(frame_t.point.x, -3.499, 2.771)

        room_size = map_range(v, -3.499, 2.771, 50, 1000)
        tr0 = map_range(v, -3.499, 2.771, 0.6, 3)
        print(room_size, tr0)

        client.send_message("/reverb/1/tr0", tr0)
        client.send_message("/reverb/1/roomsize", room_size)

    # /reverb/1/tr0
    # /reverb/1/roomsize
    # Frame(Point(-3.499, 0.383, -0.006), Vector(0.881, -0.473, -0.014), Vector(0.473, 0.881, -0.020))
    # Frame(Point(2.771, 0.175, 0.014), Vector(-0.873, -0.487, -0.019), Vector(0.486, -0.873, 0.031))


"""
for x in range(10):
    client.send_message("/track/1/xyz", (x, 0, 1))
    time.sleep(1)
"""


# This will create a new NatNet client
streamingClient = NatNetClient()
# streamingClient.print_level = 0

# Configure the streaming client to call our rigid body handler
# on the emulator to send data out.
streamingClient.newFrameListener = receiveNewFrame

# change between position streaming and room size change
#===============================================================
streamingClient.rigidBodyListener = receiveRigidBodyFrame
#streamingClient.rigidBodyListener = change_room_size
#===============================================================

# Start up the streaming client now that the callbacks are set up.
# This will run perpetually, and operate on a separate thread.
streamingClient.run()
