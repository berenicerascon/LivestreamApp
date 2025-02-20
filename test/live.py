# Using the DroidCam app on an iphone (I believe its also compatible with android)
#       DroidCam basically turns phone camera into a webcam and gives IP address for the program to pick up
# This test demonstrates DroidCam connection and displays camera stream on a simple http server
# Once the recording is over, the stream is then saved in the directory under 'output_video.mp4'
#  :)

from flask import Flask, Response
import cv2

app = Flask(__name__)

IP_CAMERA_URL = "http://192.168.1.64:4747/video"  #replace with phone's IP given on the app

# for video writer
frame_width = 640
frame_height = 480
fps = 20  