import matplotlib.pyplot as plt
import os


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
    xblocks = [[0, 100], [475, 625]]
    yblocks = [[0, 150], [450, 475]]
    xrange = []
    _ = [xrange.extend(range(el[0], el[1])) for el in xblocks]
    # print(xrange)
    yrange = []
    _ = [yrange.extend(range(el[0], el[1])) for el in yblocks]
    # print(yrange)

    # Get H and V averages -> compressed into vectors
    # vh = arr[xrange],yrange].mean(axis=0)
    # vv = arr[xrange],yrange].mean(axis=1)
    vh = arr.mean(axis=0)
    vv = arr.mean(axis=1)
    vech = vecv = np.sqrt(np.sum(np.square(vh), axis=1))
    vecv = vecv = np.sqrt(np.sum(np.square(vv), axis=1))

    # Get peaks, troughs
    peak_args = {'width': 20,
                 'distance': 10,
                 #             'height': 10,
                 'prominence': 1,
                 #             'threshold': 5,
                 #             'rel_height': 0.8,
                 }

    # ph = [el for el in find_peaks(vech, **peak_args)[0] if el in xrange]
    # th = [el for el in find_peaks(-vech, **peak_args)[0] if el in xrange]
    # pv = [el for el in find_peaks(vecv, **peak_args)[0] if el in yrange]
    # tv = [el for el in find_peaks(-vecv, **peak_args)[0] if el in yrange]
    ph = find_peaks(vech, **peak_args)[0]
    th = find_peaks(-vech, **peak_args)[0]
    pv = find_peaks(vecv, **peak_args)[0]
    tv = find_peaks(-vecv, **peak_args)[0]

    # Plot original image and overlay vectors and peaks/troughs to check it's working
    plt.imshow(image)

    plt.plot(vecv, range(len(vecv)), 'k')
    plt.plot(vech, 'k')

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

