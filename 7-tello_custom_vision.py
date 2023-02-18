from djitellopy import tello
import KeyPressModule as kp
import time
import cv2
from PIL import Image
from PIL import ImageDraw
from azure.storage.blob import ContentSettings, BlobClient
from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
from msrest.authentication import ApiKeyCredentials

kp.init()
me = tello.Tello()
me.connect()
print(me.get_battery())
me.streamon()

global img
# connection string for Azure Blob storage
conn_str = "your connection string"
container_name = "raspberrypic"
blob_name = "capture"
# custom vision api
credentials = ApiKeyCredentials(in_headers={"Prediction-key": "your prediction key"})
predictor = CustomVisionPredictionClient("your endpoint", credentials)
projectID = "your project id"
publish_iteration_name="your iteration name"


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
        time.sleep(0.1)
        target = 0
        # open and detect the captured image
        with open(f'Resources/Images/capture.jpg', mode="rb") as captured_image:
            results = predictor.detect_image(projectID, publish_iteration_name, captured_image)
        # Display the results.
        for prediction in results.predictions:
            if prediction.probability > 0.6:
                target = 1
                print("\t" + prediction.tag_name + ": {0:.2f}%".format(prediction.probability * 100))
                bbox = prediction.bounding_box
                im = Image.open(f'Resources/Images/capture.jpg')
                draw = ImageDraw.Draw(im)
                draw.rectangle([int(bbox.left * 1280), int(bbox.top * 720), int((bbox.left + bbox.width) * 1280),
                                int((bbox.top + bbox.height) * 720)], outline='red', width=5)
                im.save(f'Resources/Images/results.jpg')
        if target == 1:
            img = cv2.imread(f'Resources/Images/results.jpg', cv2.IMREAD_COLOR)
            cv2.imshow("results", img)
            cv2.waitKey(1000)
            cv2.destroyWindow("results")
        else:
            img = cv2.imread(f'Resources/Images/capture.jpg', cv2.IMREAD_COLOR)
            cv2.imshow("capture", img)
            cv2.waitKey(1000)
            cv2.destroyWindow("capture")
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
    print("Tello Image Custom Vision Demo")
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
