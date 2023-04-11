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


THRESHOLD_DEFAULT = 40


def compare_images(impath, refpath, threshold = THRESHOLD_DEFAULT):
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


# Reference image for detecting bands of colour
reference_folder = r"C:\Users\hughr\BirdCam for git\media\images"
reference_image = "grab_2023_03_11_11_06_29.png"
reference_full = os.path.join(reference_folder, reference_image)


# Example image with bands
image_folder = r"C:\Users\hughr\AppData\Local\media\images"
image_file = "grab_2023_03_05_12_49_22.png"
image_full = os.path.join(image_folder, image_file)


if __name__ == "__main__":

    # Convert to np matrix then 1D array
    image = cv2.imread(image_full)
    arr = np.array(image)


    # Define sample range to exclude central area
    xblocks = [[0,100],[475,625]]
    yblocks = [[0,150],[450,475]]
    xrange = []
    _ = [xrange.extend(range(el[0],el[1])) for el in xblocks]
    #print(xrange)
    yrange = []
    _ = [yrange.extend(range(el[0],el[1])) for el in yblocks]
    #print(yrange)


    # Get H and V averages -> compressed into vectors
    #vh = arr[xrange],yrange].mean(axis=0)
    #vv = arr[xrange],yrange].mean(axis=1)
    vh = arr.mean(axis=0)
    vv = arr.mean(axis=1)
    vech = vecv = np.sqrt(np.sum(np.square(vh),axis=1))
    vecv = vecv = np.sqrt(np.sum(np.square(vv),axis=1))


    # Get peaks, troughs
    peak_args = {'width': 20,
                 'distance': 10,
    #             'height': 10,
                 'prominence': 1,
    #             'threshold': 5,
    #             'rel_height': 0.8,
                 }

    #ph = [el for el in find_peaks(vech, **peak_args)[0] if el in xrange]
    #th = [el for el in find_peaks(-vech, **peak_args)[0] if el in xrange]
    #pv = [el for el in find_peaks(vecv, **peak_args)[0] if el in yrange]
    #tv = [el for el in find_peaks(-vecv, **peak_args)[0] if el in yrange]
    ph = find_peaks(vech, **peak_args)[0]
    th = find_peaks(-vech, **peak_args)[0]
    pv = find_peaks(vecv, **peak_args)[0]
    tv = find_peaks(-vecv, **peak_args)[0]


    # Plot original image and overlay vectors and peaks/troughs to check it's working
    plt.imshow(image)

    plt.plot(vecv,range(len(vecv)),'k')
    plt.plot(vech,'k')

    plt.scatter(ph, vech[ph], marker="o", color="black")
    plt.scatter(th, vech[th], marker="o", color="black")
    plt.scatter(vecv[pv], pv, marker="o", color="black")
    plt.scatter(vecv[tv], tv, marker="o", color="black")

    print("h peaks:", len(ph))
    print("h troughs:", len(th))
    print("v peaks:", len(pv))
    print("v troughs:", len(tv))

    plt.show()


    # Look for areas of strong colour (greens and blacks seem common)

    
    # Reject if more than threshold amount of image -> reject or accept based on this

