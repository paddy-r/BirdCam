# HR 05/03/23 Image-related utils
# 1. To detect bands in images (as camera is analog and some images are sketchy)
# 2. To produce video of videos/images taken from user-defined time period

# Peaks and troughs code adapted from here: https://stackoverflow.com/questions/56620649/how-to-find-troughs-in-a-1-d-array


import cv2
import numpy as np
import sys,os
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from scipy.spatial.distance import euclidean
# from birdcam.BirdCam import create_filename as cf


THRESHOLD_DEFAULT = 40
ENDINGS_DEFAULT = [".png"]
# STARTINGS_DEFAULT = ["grab"]
FRAME_RATE_DEFAULT = 1
VIDEO_NAME_DEFAULT = "video_out.avi"


# HR 27/05/23 Adding functionality to create video from series of images
def create_video(image_fullpaths=None,
                 image_folder=None,
                 endings=ENDINGS_DEFAULT,
                 # startings=STARTINGS_DEFAULT,
                 output_folder=None,
                 video_name=VIDEO_NAME_DEFAULT,
                 frame_rate=FRAME_RATE_DEFAULT):

    if (not image_fullpaths) and (not image_folder):
        print("No images or image folder specified; aborting")
        return

    # Get all full paths to files if only folder passed
    if not image_fullpaths:
        all_files = os.listdir(image_folder)
        image_fullpaths = [os.path.join(image_folder, file) for file in all_files]

    if not output_folder:
        output_folder = image_folder
    video_fullpath = os.path.join(output_folder, video_name)

    # images = [file for file in os.listdir(image_folder) if file.endswith(tuple(endings))]
    # images = [file for file in os.listdir(image_folder) if file.startswith(tuple(startings))]
    images = [file for file in image_fullpaths if os.path.splitext(file)[-1] in endings]
    images.sort()
    print("Found {} valid images".format(len(images)))
    # for image in images:
    #     print(image)

    frame = cv2.imread(images[0]) # Get image dimensions, and assume all the same
    height, width, layers = frame.shape
    print("Image shape:", frame.shape)

    # Basic, trying to avi (from here: https://stackoverflow.com/questions/44947505/how-to-make-a-movie-out-of-images-in-python)
    # video = cv2.VideoWriter(video_fullpath, 0, 1, (width, height))
    # print("Video created")

    # Less basic b/c code above doesn't work: https://stackoverflow.com/questions/63925179/making-a-video-with-images-in-python-using-opencv-on-mac)
    fourcc = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')
    video = cv2.VideoWriter(video_fullpath, fourcc, frame_rate, (width, height), isColor=True)

    n_images = len(images)
    for i in range(n_images):
        print("Trying to add image {} of {} to video".format(i, n_images))
        video.write(cv2.imread(images[i]))
        print("Done")

    video.release()
    print("Saving video to:", video_fullpath)
    return video_fullpath


def compare_images(impath, refpath, threshold=THRESHOLD_DEFAULT):
    image1 = cv2.imread(impath)
    arr1 = np.array(image1)
    image2 = cv2.imread(refpath)
    arr2 = np.array(image2)
    
    vh1 = arr1.mean(axis=0)
    vv1 = arr1.mean(axis=1)
    vh2 = arr2.mean(axis=0)
    vv2 = arr2.mean(axis=1)

#    dist_h = euclidean(vh1,vh2)
#    dist_v = euclidean(vv1,vv2)

    dist_h = [euclidean(el1,el2) for el1,el2 in zip(vh1,vh2)]
    dist_v = [euclidean(el1,el2) for el1,el2 in zip(vv1,vv2)]

    dist_ht = [40 if el > threshold else 0 for el in dist_h]
    dist_vt = [40 if el > threshold else 0 for el in dist_v]
    
    plt.imshow(image1)
    plt.plot(dist_ht,'k')
    plt.plot(dist_vt,range(len(dist_vt)),'k')
    plt.show()

    return dist_h, dist_v


# if __name__ == "__main__":
#     im_folder = r"D:\_Back up to IOMEGA\_All BirdCam media\2023\images"
#     video_name = cf(stub="video_") + ".avi"
#     create_video(im_folder, frame_rate=5, video_name=video_name)
