from djitellopy import tello
from azure.iot.device import IoTHubDeviceClient, Message, MethodResponse
import asyncio
import time
import uuid

me = tello.Tello()
me.connect()
# interval for sending messages
interval = 5
# The connection string for a device.
conn_str = "your connection string "


def create_client():
    # The client object is used to interact with your Azure IoT hub.
    device_client = IoTHubDeviceClient.create_from_connection_string(conn_str)

    # Define behavior for handling methods
    def method_request_handler(method_request):
        # Determine how to respond to the method request based on the method name
        if method_request.name == "SetTelemetryInterval":
            try:
                global interval
                interval = int(method_request.payload)
                print("The time interval is set to " + str(method_request.payload))
            except ValueError:
                response_payload = {"Response": "Invalid parameter"}
                response_status = 400
            else:
                response_payload = {"Response": "Executed direct method {}".format(method_request.name)}
                response_status = 200
        else:
            response_payload = {"Response": "Direct method {} not defined".format(method_request.name)}
            response_status = 404

        # Send the response
        method_response = MethodResponse.create_from_method_request(method_request, response_status, response_payload)
        device_client.send_method_response(method_response)

    try:
        # Attach the method request handler
        device_client.on_method_request_received = method_request_handler
    except ValueError:
        # Clean up in the event of failure
        device_client.shutdown()
        raise

    return device_client


# Define behavior for telemetry sending
def send_tello_telemetry(device_client):
    # Connect the client.
    device_client.connect()

    # Send tello telemetry
    while True:
        msg = Message(str(me.get_current_state()))
        msg.message_id = uuid.uuid4()
        msg.correlation_id = "correlation-1234"
        msg.custom_properties["tornado-warning"] = "yes"
        msg.content_encoding = "utf-8"
        msg.content_type = "application/json"
        print("sending message: " + str(me.get_current_state()))
        device_client.send_message(msg)
        time.sleep(interval)


def main():
    print("IoTHub Device Client Sending Tello Telemetry")
    print("Press Ctrl+C to exit")
    # Instantiate the client. Use the same instance of the client for the duration of
    # your application
    client = create_client()
    # Send telemetry
    try:
        send_tello_telemetry(client)
    except KeyboardInterrupt:
        print("IoTHubClient Device Client stopped by user")
    finally:
        print("Shutting down IoTHubClient")
        client.shutdown()


if __name__ == "__main__":
    main()
