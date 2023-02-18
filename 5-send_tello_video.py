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

conn_str = "your connection string"
container_name = "raspberrypic"
blob_name = "tellovideo.mp4"

vid_cod = cv2.VideoWriter_fourcc(*'XVID')
vid_output = cv2.VideoWriter("Resources/Videos/cam_video.mp4", vid_cod, 20.0, (640,480))


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
        # stop recording
        global vid_output
        vid_output.release()
        # upload the image to Azure Blob Storage, Overwrite if it already exists!
        blob = BlobClient.from_connection_string(conn_str, container_name, blob_name)
        image_content_setting = ContentSettings(content_type='video/mp4')
        with open(f'Resources/Videos/cam_video.mp4', "rb") as data:
            try:
                blob.upload_blob(data, overwrite=True, content_settings=image_content_setting)
                print("Blob storage uploading completed")
            except ValueError:
                print("Blob storage uploading error")
        # start new recording
        global vid_cod
        vid_output = cv2.VideoWriter("Resources/Videos/cam_video.mp4", vid_cod, 20.0, (640, 480))

    return [lr, fb, ud, yv]


def main():
    print("Capture and send Tello video to Azure Blob Storage")
    while True:
        start_time = time.time()
        print("battery: " + str(me.get_battery()))

        vals = getKeyboardInput()
        me.send_rc_control(vals[0], vals[1], vals[2], vals[3])

        try:
            img = me.get_frame_read().frame
            img = cv2.resize(img, (640, 480))

            if (time.time() - start_time) > 0:
                fpsInfo = "FPS: " + str(1.0 / (time.time() - start_time))  # FPS = 1 / time to process loop
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(img, fpsInfo, (10, 20), font, 0.4, (255, 255, 255), 1)

            cv2.imshow('DJI Tello Camera', img)
            global vid_output
            vid_output.write(img)
        except Exception as e:
            print(f'exc: {e}')
            pass

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # close the already opened camera, and the video file
    vid_output.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
