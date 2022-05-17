"""
BirdCam-2000: ALL BIRDS, ALL THE TIME
HPR 08/05/22
"""
import cv2
import tkinter as tk
from PIL import Image, ImageTk

def get_available_cameras(max_id = 5):
    ids_available = []

    for idx in range(max_id):
        print('Trying camera ',idx, 'of', max_id, '...')
        cap = cv2.VideoCapture(idx)
        ''' Alternative ways to determine whether available;
            REQUIRES TESTING FOR SPEED AND FUNCTION '''
        # success,image = cap.read()
        # if success:
        if cap.isOpened():
            ids_available.append(idx)
        cap.release()
    return ids_available



''' Fetch all available cameras and create dialog with button for each;
    returns index corresponding  '''
class CameraSelector(tk.Toplevel):
    def __init__(self, parent, camera_list, text = None):
        # tk.Toplevel.__init__(self, parent)
        super().__init__(parent)

        if not text:
            text = 'Select camera'
        self.title(text)
        # self.label = tk.Label(self)

        ''' Default radio button to select is lowest of camera IDs '''
        self.camera = tk.IntVar(min(camera_list))

        for i in camera_list:
            rb = tk.Radiobutton(self, text = "Camera" + str(i), variable = self.camera, value = i)
            rb.pack(side = "top")
            rb.bind("<Return>", self.OnOK)

        # self.label.pack(side = "top", fill = "x")
        self.ok_button = tk.Button(self, text = "OK", command = self.OnOK)
        self.ok_button.pack(side = "top")

    def OnOK(self, event = None):
        self.destroy()

    def show(self):
        self.wm_deiconify()
        self.wait_window()
        return self.camera.get()



class BirdCam(tk.Tk):

    ''' Constructor '''
    def __init__(self, feed_index = None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.wm_title("BIRDCAM-2000: ALL BIRDS, ALL THE TIME")
        # self.config(background="#FFFFFF")

        ''' Set up feed index etc. '''
        self.FEED_INDEX_DEFAULT = 1
        self.FRAME_RATE_DEFAULT = 24
        self.feed_index = feed_index
        if feed_index and type(feed_index) == int:
            self.feed_index = feed_index
        else:
            self.feed_index = self.FEED_INDEX_DEFAULT

        ''' Create GUI elements '''
        self._create_menubar()
        self._create_viewer()

        # ''' Try and start feed '''
        # self.start_feed()

    def _create_menubar(self):
        self.menubar = tk.Menu(self)
        self.configure(menu = self.menubar)

        # Settings menu
        settingsMenu = tk.Menu(self.menubar)
        self.menubar.add_cascade(label = "Settings", menu = settingsMenu)
        settingsMenu.add_command(label = "File save location", command = self.OnSaveLocation)
        settingsMenu.add_command(label = "Image save settings", command = self.OnImageSettings)
        settingsMenu.add_command(label = "Video save settings", command = self.OnVideoSettings)

        # Camera connect menu
        connectMenu = tk.Menu(self.menubar)
        self.menubar.add_cascade(label = "Connect", menu = connectMenu)
        connectMenu.add_command(label = "Find camera", command = self.OnFindCamera)

    def _create_viewer(self):
        ''' Initialise video viewer '''
        # width, height = self.VIEWER_DIMENSIONS_DEFAULT
        # self.viewerFrame = tk.Frame(self, width = 500, height = 500)
        # self.viewerFrame.grid(row = 0, column = 0, padx = 10, pady = 10)

        # self.viewer = tk.Label(self.viewerFrame, width = 25)
        self.viewer = tk.Label(self)
        self.viewer.pack(side = "top", fill = "both", expand = True, padx = 10, pady = 10)
        # self.viewer.grid(row = 0, column = 0)

        # ''' Set up text output box '''
        # self.texter = tk.Text(self.viewerFrame)

        # ''' Set up video/image record/save buttons'''
        # self.btn_video_start = tk.Button(self.viewerFrame)
        # self.btn_video_stop = tk.Button(self.viewerFrame)
        # self.btn_image_grab = tk.Button(self.viewerFrame)

    def grab_feed(self, frame_rate = None):
        _, frame = self.feed.read()
        # print('Grabbed frame')
        frame = cv2.flip(frame, 1)
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image = img)
        self.viewer.imgtk = imgtk
        self.viewer.configure(image = imgtk)
        
        # ''' Set frame rate and update '''
        # if not frame_rate:
        #     frame_rate = self.FRAME_RATE_DEFAULT
        self.viewer.after(10, self.grab_feed)

    def OnSaveLocation(self):
        print('Running OnSaveLocation')

    def OnImageSettings(self):
        print('Running OnImageSettings')

    def OnVideoSettings(self):
        print('Running OnImageSettings')

    def OnFindCamera(self):
        print('Running OnFindCamera')
        ''' Get IDs of all available cameras and add to drop-down menu '''
        ids = get_available_cameras()
        print('Found camera IDs:', ids)
        camera_id = CameraSelector(self, ids, text = "Select camera to connect").show()
        print('Camera', camera_id, 'selected; trying to connect...')

        self.feed_index = camera_id
        self.feed = cv2.VideoCapture(self.feed_index)
        print('Got feed', self.feed_index)
        self.grab_feed()

    ''' Print text to output box for user info '''
    def output_text(self, text):
        self.texter.delete(0, "end")
        self.texter.insert(tk.END, text)



if __name__ == "__main__":

    # birdcam = tk.Tk()  #Makes main window
    # birdcam.wm_title("Birdcam BC-2000")
    # birdcam.config(background="#FFFFFF")

    # # menubar =

    # #Graphics window
    # imageFrame = tk.Frame(birdcam, width=600, height=500)
    # imageFrame.grid(row=0, column=0, padx=10, pady=2)

    # #Capture video frames
    # lmain = tk.Label(imageFrame)
    # lmain.grid(row=0, column=0)
    # cap = cv2.VideoCapture(1)

    # def show_frame():
    #     _, frame = cap.read()
    #     frame = cv2.flip(frame, 1)
    #     cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
    #     img = Image.fromarray(cv2image)
    #     imgtk = ImageTk.PhotoImage(image=img)
    #     lmain.imgtk = imgtk
    #     lmain.configure(image=imgtk)
    #     lmain.after(10, show_frame)

    # show_frame()  #Display 2
    # birdcam.mainloop()  #Starts GUI

    bc = BirdCam()
    bc.mainloop()