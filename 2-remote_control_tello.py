import asyncio
from azure.iot.device.aio import IoTHubDeviceClient
from djitellopy import tello
import KeyPressModule as kp
from time import sleep

kp.init()
me = tello.Tello()
me.connect()


def getKeyboardInput():
    lr, fb, ud, yv = 0, 0, 0, 0
    speed = 15

    if kp.getKey("LEFT"):
        lr = -speed
    elif kp.getKey("RIGHT"):
        lr = speed

    if kp.getKey("UP"):
        fb = speed
    elif kp.getKey("DOWN"):
        fb = -speed

    if kp.getKey("w"):
        ud = speed
    elif kp.getKey("s"):
        ud = -speed

    if kp.getKey("a"):
        yv = speed
    elif kp.getKey("d"):
        yv = -speed

    if kp.getKey("q"):
        me.land()
    if kp.getKey("e"):
        me.takeoff()

    return [lr, fb, ud, yv]


# define behavior for receiving a message
# NOTE: this could be a function or a coroutine
def message_received_handler(message):
    lr, fb, ud, yv = 0, 0, 0, 0
    speed = 15
    print("the data in the message received was ")
    print(message.data)
    if message.data == b'left':
        lr = -speed
    elif message.data == b'right':
        lr = speed

    if message.data == b'forward':
        fb = speed
    elif message.data == b'back':
        fb = -speed

    if message.data == b'up':
        ud = speed
    elif message.data == b'down':
        ud = -speed

    if message.data == b'yaw':
        yv = speed
    elif message.data == b'roll':
        yv = -speed

    if message.data == b'land':
        me.land()
    if message.data == b'takeoff':
        me.takeoff()

    me.send_rc_control(lr, fb, ud, yv)


async def main():
    conn_str = "your connection string"
    # The client object is used to interact with your Azure IoT hub.
    device_client = IoTHubDeviceClient.create_from_connection_string(conn_str)

    # connect the client.
    await device_client.connect()

    # set the message received handler on the client
    device_client.on_message_received = message_received_handler

    while True:
        vals = getKeyboardInput()
        # me.send_rc_control(vals[0], vals[1], vals[2], vals[3])
        sleep(0.1)


if __name__ == "__main__":
    asyncio.run(main())
