from djitellopy import tello
from azure.iot.device.aio import IoTHubDeviceClient
from azure.iot.device import Message
import asyncio
import time
import uuid

me = tello.Tello()
me.connect()

async def send_tello_telemetry(device_client):
    # Connect the client.
    await device_client.connect()

    # Send tello telemetry
    while True:
        msg = Message(str(me.get_current_state()))
        msg.message_id = uuid.uuid4()
        msg.correlation_id = "correlation-1234"
        msg.custom_properties["tornado-warning"] = "yes"
        msg.content_encoding = "utf-8"
        msg.content_type = "application/json"
        print("sending message: " + str(me.get_current_state()))
        await device_client.send_message(msg)
        time.sleep(5)


def main():
    # The connection string for a device.
    conn_str = "your connection string "
    # The client object is used to interact with your Azure IoT hub.
    device_client = IoTHubDeviceClient.create_from_connection_string(conn_str)

    print("IoTHub Device Client Sending Tello Telemetry")
    print("Press Ctrl+C to exit")
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(send_tello_telemetry(device_client))
    except KeyboardInterrupt:
        print("User initiated exit")
    except Exception:
        print("Unexpected exception!")
        raise
    finally:
        loop.run_until_complete(device_client.shutdown())
        loop.close()


if __name__ == "__main__":
    main()
