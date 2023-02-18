from djitellopy import tello
import KeyPressModule as kp
import cv2
import requests
import time
import json
from PIL import Image
from PIL import ImageDraw


kp.init()
me = tello.Tello()
me.connect()
print(me.get_battery())
me.streamon()

global img
Local_Custom_Vision_ENDPOINT = "http://172.31.59.150:23114/image" (make sure the IP is your local custom vision endpoint)


# Send an image to the image classifying server
# Return the JSON response from the server with the prediction result
def sendFrameForProcessing(imagePath, imageProcessingEndpoint):
    headers = {'Content-Type': 'application/octet-stream'}

    with open(imagePath, mode="rb") as test_image:
        try:
            response = requests.post(imageProcessingEndpoint, headers = headers, data = test_image)
            print("Response from custom vision service: (" + str(response.status_code) + ") " + json.dumps(response.json()) + "\n")
        except Exception as e:
            print(e)
            print("No response from custom vision service")
            return None

    return json.dumps(response.json())


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
        target = 0
        start_time = time.time()
        # open and detect the captured image
        results = sendFrameForProcessing(f'Resources/Images/capture.jpg', Local_Custom_Vision_ENDPOINT)
        fps = time.time() - start_time
        print('Time:'+str(fps))
        for index in range(len(results['predictions'])):
            if(results['predictions'][index]['probability'] > 0.5):
                target = 1
                print("\t" + results['predictions'][index]['tagName'] + ": {0:.2f}%".format(results['predictions'][index]['probability'] * 100))
                bbox = results['predictions'][index]['boundingBox']
                im = Image.open(f'Resources/Images/capture.jpg')
                draw = ImageDraw.Draw(im)
                draw.rectangle([int(bbox['left'] * 1280), int(bbox['top'] * 720), int((bbox['left'] + bbox['width']) * 1280),
                                int((bbox['top'] + bbox['height']) * 720)], outline='red', width=5)
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

    return [lr, fb, ud, yv]


# Send an image to the custom vision server
# Return the JSON response from the server with the prediction result
def sendFrameForProcessing(imagePath, imageProcessingEndpoint):
    headers = {'Content-Type': 'application/octet-stream'}

    with open(imagePath, mode="rb") as test_image:
        try:
            response = requests.post(imageProcessingEndpoint, headers = headers, data = test_image)
            print("Response from local custom vision service: (" + str(response.status_code) + ") " + json.dumps(response.json()) + "\n")
        except Exception as e:
            print(e)
            print("No response from custom vision service")
            return None

    return response.json()


def main():
    print("Tello Custom Vision IoT Edge Demo")
    while True:
        vals = getKeyboardInput()
        me.send_rc_control(vals[0], vals[1], vals[2], vals[3])
        global img
        img = me.get_frame_read().frame
        img = cv2.resize(img, (1280, 720))
        cv2.putText(img, 'Battery:'+str(me.get_battery()), (10, 60), cv2.FONT_HERSHEY_PLAIN, 0.9, (255, 0, 255), 1)
        cv2.imshow("image", img)
        cv2.waitKey(1)


if __name__ == "__main__":
    main()
