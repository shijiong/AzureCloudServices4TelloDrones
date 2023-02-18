from djitellopy import tello
import KeyPressModule as kp
import time
import cv2
from azure.storage.blob import ContentSettings, BlobClient

kp.init()
me = tello.Tello()
me.connect()
print(me.get_battery())
me.streamon()

global img
conn_str = "your connection string"
container_name = "raspberrypic"
blob_name = "capture"


def getKeyboardInput():
    lr, fb, ud, yv = 0, 0, 0, 0
    speed = 50

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

    if kp.getKey("q"): me.land()
    if kp.getKey("e"): me.takeoff()

    if kp.getKey("z"):
        global img
        cv2.imwrite(f'Resources/Images/capture.jpg', img)
        time.sleep(0.3)
        # upload the image to Azure Blob Storage, Overwrite if it already exists!
        blob = BlobClient.from_connection_string(conn_str, container_name, blob_name)
        image_content_setting = ContentSettings(content_type='image/jpeg')
        with open(f'Resources/Images/capture.jpg', "rb") as data:
            try:
                blob.upload_blob(data, overwrite=True, content_settings=image_content_setting)
                print("Blob storage uploading completed")
            except ValueError:
                print("Blob storage uploading error")
    return [lr, fb, ud, yv]


def main():
    print("Capture and send Tello image to Azure Blob Storage")
    while True:
        vals = getKeyboardInput()
        me.send_rc_control(vals[0], vals[1], vals[2], vals[3])
        global img
        img = me.get_frame_read().frame
        img = cv2.resize(img, (1280, 720))
        cv2.putText(img, str(me.get_current_state()), (10, 60), cv2.FONT_HERSHEY_PLAIN, 0.9, (255, 0, 255), 1)
        cv2.imshow("image", img)
        cv2.waitKey(50)


if __name__ == "__main__":
    main()
