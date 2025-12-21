import cv2
import numpy as np
import os
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;udp"
vcap = cv2.VideoCapture("rtsp://192.168.1.222:8554/main", cv2.CAP_FFMPEG)
while(1):
    ret, frame = vcap.read()
    if ret == False:
        print("Frame is empty")
        break
    else:
        scaled = cv2.resize(frame, (600, 400))
        cv2.imshow('VIDEO', scaled)
        cv2.waitKey(1)
