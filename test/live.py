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
fps = 20  #can change for higher fps
output_file = "output_video.mp4"

fourcc = cv2.VideoWriter_fourcc(*'mp4v')  #mp4v for MP4 files
video_writer = cv2.VideoWriter(output_file, fourcc, fps, (frame_width, frame_height))


def generate_frames():
    camera = cv2.VideoCapture(IP_CAMERA_URL)  #open phone camera stream

    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            video_writer.write(frame)
            _, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            
# these next app routes need to implemented on the website, its kind of clunky rn for the sake of testing
@app.route('/')
def index():
    return "<h1>Go to <a href='/video_feed'>/video_feed</a> to view the stream.</h1>"

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/stop_recording') 
def stop_recording():
    """Stops the recording and releases the video writer"""
    global video_writer
    video_writer.release()
    return "Recording stopped and saved as output_video.mp4"


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")  #allows access from other devices
