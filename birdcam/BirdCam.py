"""
BirdCam-2000: ALL BIRDS, ALL THE TIME
HPR 08/05/22
HPR 05/03/23 Updating environment setup and adding executable
"""


import cv2
import tkinter as tk
import tkinter.filedialog as fd
from PIL import Image, ImageTk
# import time
import datetime
import sys,os
#import numpy as np


# Grab path to file, depending on whether normal script or Pyinstaller executable
# Taken from here: https://stackoverflow.com/questions/404744/determining-application-path-in-a-python-exe-generated-by-pyinstaller
if getattr(sys, 'frozen', False):
    # If the application is run as a bundle, the PyInstaller bootloader
    # extends the sys module by a flag frozen=True and sets the app 
    # path into variable _MEIPASS'.
    APP_PATH = sys._MEIPASS
    print("\n## Running as executable, path to exe:", APP_PATH, "##\n")
else:
    APP_PATH = os.path.dirname(os.path.abspath(__file__))
    print("\n## Running as script, path:", APP_PATH, "##\n")


def get_filename():
    filename = "grab_" + str(datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S'))
    return filename


SAVE_FOLDER_DEFAULT = os.path.join(os.path.dirname(os.path.dirname(APP_PATH)), "media")
print(SAVE_FOLDER_DEFAULT)

FILE_FOLDER_DEFAULT = os.path.join(SAVE_FOLDER_DEFAULT, "files")
FILE_EXT_DEFAULT = '.txt'
FILE_FILE_DEFAULT = get_filename

IMAGE_FOLDER_DEFAULT = os.path.join(SAVE_FOLDER_DEFAULT, "images")
IMAGE_EXT_DEFAULT = '.png'
IMAGE_FILE_DEFAULT = get_filename

VIDEO_FOLDER_DEFAULT = os.path.join(SAVE_FOLDER_DEFAULT, "videos")
VIDEO_EXT_DEFAULT = '.avi'
VIDEO_FILE_DEFAULT = get_filename

FEED_INDEX_DEFAULT = 0
FRAME_RATE_DEFAULT = 10

INFO_BOX_MESSAGE_DEFAULT = ""
INFO_DISPLAY_TIME_DEFAULT = 2000 # Display info box messages for 2 seconds

VIDEO_STOP_DEFAULT = "Stop recording"
VIDEO_START_DEFAULT = "Start recording"

GRAB_IMAGE_DEFAULT = "Grab image"


def get_available_cameras(max_id = 5):
    ids_available = []

    for idx in range(max_id):
        print('Trying camera ', idx, 'of', max_id, '...')
        cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
        ''' Alternative ways to determine whether available;
            REQUIRES TESTING FOR SPEED AND FUNCTION '''
        # success,image = cap.read()
        # if success:
        if cap.isOpened():
            ids_available.append(idx)
        cap.release()
    return ids_available


''' Fetch all available cameras and create dialog with button for each;
    returns index corresponding to selected camera '''
class CameraSelector(tk.Toplevel):
    def __init__(self, parent, camera_list, text=None):
        # tk.Toplevel.__init__(self, parent)
        super().__init__(parent)

        if not text:
            text = 'Select camera'
        self.title(text)
        # self.label = tk.Label(self)

        ''' Default radio button to select is lowest of camera IDs '''
        #self.camera = min(camera_list)
        self.camera = tk.IntVar()
        #self.camera.set(min(camera_list))

        for i in camera_list:
            rb = tk.Radiobutton(self, text="Camera" + str(i), variable=self.camera, value=i)
            rb.pack(side = "top")
            #rb.bind("<Return>", self.OnOK)

        # self.label.pack(side = "top", fill = "x")
        self.ok_button = tk.Button(self, text = "OK", command = self.OnOK)
        self.ok_button.pack(side = "top")

    def OnOK(self, event = None):
        #print("Camera ID:", int(self.camera.get()))
        self.destroy()

    def show(self):
        #self.wm_deiconify()
        self.wait_window()
        return self.camera.get()


class BirdCam(tk.Tk):

    ''' Constructor '''
    def __init__(self, *args,
                       feed_index = FEED_INDEX_DEFAULT,
                       frame_rate = FRAME_RATE_DEFAULT,
                       file_folder = FILE_FOLDER_DEFAULT,
                       file_file = FILE_FILE_DEFAULT,
                       file_ext = FILE_EXT_DEFAULT,
                       image_folder = IMAGE_FOLDER_DEFAULT,
                       image_file = IMAGE_FILE_DEFAULT,
                       image_ext = IMAGE_EXT_DEFAULT,
                       video_folder = VIDEO_FOLDER_DEFAULT,
                       video_file = VIDEO_FILE_DEFAULT,
                       video_ext = VIDEO_EXT_DEFAULT,
                       video_start_text = VIDEO_START_DEFAULT,
                       video_stop_text = VIDEO_STOP_DEFAULT,
                       **kwargs):

        super().__init__(*args, **kwargs)
        self.args = args
        self.kwargs = kwargs

        self.title("BirdCam-2000: ALL BIRDS, ALL THE TIME")
        # self.config(background="#FFFFFF")


        self.file_folder = file_folder
        self.file_file = file_file
        self.file_ext = file_ext
        self.image_folder = image_folder
        self.image_file = image_file
        self.image_ext = image_ext
        self.video_folder = video_folder
        self.video_file = video_file
        self.video_ext = video_ext


        ''' Set up feed index etc. '''
        self.frame_rate = frame_rate
        # self.feed_index = feed_index
        if feed_index and type(feed_index) == int:
            self.feed_index = feed_index
        else:
            self.feed_index = FEED_INDEX_DEFAULT

        self._record = False
        self._connected = False

        self.frame_edge_col = 'black'
        self.frame_edge_thickness = 1

        ''' Create menu bar '''
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

        ''' Set up main frame into which everything goes '''
        self.grid_rowconfigure(0, weight = 1)
        self.grid_columnconfigure(0, weight = 1)

        self.main_frame = tk.Frame(self,
                           highlightbackground = self.frame_edge_col,
                           highlightthickness = self.frame_edge_thickness)
        self.main_frame.grid(column = 0, row = 0, sticky = "nsew")

        self.main_frame.grid_rowconfigure(0, weight = 10)
        self.main_frame.grid_rowconfigure(1, weight = 1)
        self.main_frame.grid_rowconfigure(2, weight = 1)
        self.main_frame.grid_columnconfigure(0, weight = 1)

        self.viewer_section = tk.Label(self.main_frame,
                           highlightbackground = self.frame_edge_col,
                           highlightthickness = self.frame_edge_thickness)
        self.info_section = tk.Label(self.main_frame,
                            highlightbackground = self.frame_edge_col,
                            highlightthickness = self.frame_edge_thickness)
        self.button_section = tk.Frame(self.main_frame,
                              highlightbackground = self.frame_edge_col,
                              highlightthickness = self.frame_edge_thickness)

        ''' Set up info box text '''
        self.info_text = tk.StringVar()
        #self.info_text.set("Info box")

        ''' View section '''
        self.viewer = tk.Label(self.viewer_section,
                                   text = 'Viewer section',
                                   background = 'white')

        self.viewer.grid(sticky = 'nsew')
        self.viewer_section.grid_columnconfigure(0, weight = 1)
        self.viewer_section.grid_rowconfigure(0, weight = 1)

        ''' Info section '''
        self.info_box = tk.Label(self.info_section,
                                   textvariable = self.info_text,
                                   background = 'white')

        self.info_box.grid(sticky = 'nsew')
        self.info_section.grid_columnconfigure(0, weight = 1)
        self.info_section.grid_rowconfigure(0, weight = 1)
        self.update_infobox(message = "Info box")

        ''' Button section'''
        self.button_record = tk.Button(self.button_section,
                                          text = VIDEO_START_DEFAULT,
                                          command = self.recording_actions)
        #self.button_stop = tk.Button(self.button_section,
        #                                  text = VIDEO_STOP_DEFAULT,
        #                                  command = self.stop)
        self.button_grab_frame = tk.Button(self.button_section,
                                              text = GRAB_IMAGE_DEFAULT,
                                              command = self.grab_frame)

        self.button_record.grid(row = 0, column = 0, sticky = 'nsew')
        #self.button_stop.grid(row = 0, column = 1, sticky = 'nsew')
        self.button_grab_frame.grid(row = 0, column = 2, sticky = 'nsew')

        self.button_section.grid_rowconfigure(0, weight = 1)
        self.button_section.grid_columnconfigure(0, weight = 1)
        self.button_section.grid_columnconfigure(1, weight = 1)
        #self.button_section.grid_columnconfigure(2, weight = 1)

        ''' Finally configure main grid '''
        self.viewer_section.grid(row = 0, column = 0, sticky = 'nesw')
        self.info_section.grid(row = 1, column = 0, sticky = 'nesw')
        self.button_section.grid(row = 2, column = 0, sticky = 'nesw')

        ''' Maximise app '''
        self.state('zoomed')
        ''' Override "close" action to release camera '''
        self.protocol("WM_DELETE_WINDOW", self.OnClose)

        ''' Try to connect to video feed '''
        try:
            self.update_infobox(['Trying to connect to camera', self.feed_index, '...'])
            self.connect()
        except Exception as e:
            self.update_infobox(['Could not connect to camera', self.feed_index, ', exception follows'])
            print(e)

        #self.bind("<FocusOut>", self.on_focus_out)
        #self.bind("<FocusIn>", self.on_focus_in)
        #self.bind('<Motion>', self.motion)


    def motion(self, event = None):
        x, y = event.x, event.y
        print('{}, {}'.format(x, y))


    def on_focus_out(self, event=None):
        print("## FOCUS OUT ##")


    def on_focus_in(self, event=None):
        print("## FOCUS IN ##")


    def update_infobox(self, message=INFO_BOX_MESSAGE_DEFAULT, t=INFO_DISPLAY_TIME_DEFAULT):
        if isinstance(message, list):
            message = ' '.join(str(a) for a in message)
        else:
            message = str(message)
        print(message)
        self.info_text.set(message)
        if message != INFO_BOX_MESSAGE_DEFAULT:
            self.after(t, self.update_infobox)


    def recording_actions(self, event=None):
        if self._record:
            # Stop recording and change text/icon of button
            self.stop()
            self.button_record.configure(text=VIDEO_START_DEFAULT)
        else:
            # Start recording and change text/icon of button
            self.record()
            self.button_record.configure(text=VIDEO_STOP_DEFAULT)


    def record(self, video_file=None):
        #if self._record:
        #    self.update_infobox('Already recording; stop current video first')
        #    return

        self.update_infobox('Starting video recording...')
        if not video_file:
            video_folder = self.video_folder
            if not os.path.exists(video_folder):
                os.makedirs(video_folder)
            file = os.path.join(video_folder, self.video_file() + self.video_ext)
            self.update_infobox(file)

        ''' Get video properties '''
        frame_rate = self.frame_rate
        w,h = self.get_frame_dimensions()
        if not w or not h:
            self.update_infobox('Could not get frame dimensions; aborting video save')
            return

        ''' Set up video writer object '''
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.update_infobox(['Starting video with frame rate and w,h:', frame_rate, w, h])
        self.video_out = cv2.VideoWriter(file, fourcc, frame_rate, (w,h))
        ''' Allow recording '''
        self._record = True
        self.write_video_frame()
        self._video_file = file


    def write_video_frame(self):
        if self._record:
            ''' Factor of 1000 b/c opencv measures delay in ms '''
            delay = round(1000/self.frame_rate)
            self.video_out.write(self.frame)
            self.viewer.after(delay, self.write_video_frame)


    def stop(self):
        if self._record:
            self.update_infobox('Stopping video recording...')
            ''' Disallow recording '''
            self._record = False
            ''' Dump video to file '''
            self.update_infobox(['Saving video to', self._video_file, "..."])
            self.video_out.release()
        else:
            self.update_infobox("Can't stop recording as not recording")


    def grab_frame(self, file = None):
        self.update_infobox('Grabbing video frame...')
        if not file:
            # print(self.image_file)
            file = self.image_file() + self.image_ext
        #if hasattr(self, 'img'):
        img_folder = self.image_folder
        if not os.path.exists(img_folder):
            os.makedirs(img_folder)
        file = os.path.join(img_folder, file)
        self.img.save(file)
        self.update_infobox(['Done saving image file:', file])


    ''' Get all available cameras and ask for user input '''
    def OnFindCamera(self):
        #self.update_infobox('Running OnFindCamera')
        ''' Get IDs of all available cameras and add to drop-down menu '''
        ids = get_available_cameras()
        self.update_infobox(['Found camera IDs:', ids])
        camera_id = CameraSelector(self, ids, text = "Select camera to connect").show()
        #camera_id = CameraSelector(self, ids, text = "Select camera to connect")
        self.update_infobox(['Camera', camera_id, 'selected; trying to connect...'])
        self.feed_index = camera_id
        self.connect()


    ''' Connect to camera by ID '''
    def connect(self):
        if self._connected:
            self.update_infobox("Releasing old feed...")
            self.feed.release()
        else:
            self._connected = True
        self.feed = cv2.VideoCapture(self.feed_index, cv2.CAP_DSHOW)
        self.update_infobox(['Got feed', self.feed_index])
        # self.timer = time.time()
        self.update_infobox("Running grab_feed from connect...")
        self.grab_feed()


    def get_frame_dimensions(self):
        try:
            w = self.feed.get(cv2.CAP_PROP_FRAME_WIDTH)
            h = self.feed.get(cv2.CAP_PROP_FRAME_HEIGHT)
        except:
            w = None
            h = None
        return round(w),round(h)


    def grab_feed(self, frame_rate = None):
        _, self.frame = self.feed.read()
        ''' Try to automatically reconnect if problem arises '''
        if self.frame is None:
            self.feed.release()
            self.feed = cv2.VideoCapture(self.feed_index, cv2.CAP_DSHOW)
            self.viewer.after(2, self.grab_feed)

            ''' Cut video recording short, if necessary '''
            if self._record:
                self.update_infobox('Connection to camera lost; stopping video recording and saving video')
                self._record = False
                self.video_out.release()
            return

        self.frame = cv2.flip(self.frame, 1)
        cv2image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGBA)
        self.img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image = self.img)
        self.viewer.imgtk = imgtk
        self.viewer.configure(image = imgtk)
        self.viewer.after(10, self.grab_feed)


    def OnSaveLocation(self):
        self.update_infobox('Running OnSaveLocation')
        new_path = fd.askdirectory(parent=self, initialdir=APP_PATH, title='Please select a directory for saving general files')
        if new_path:
            self.update_infobox(["New file save path selected:", new_path])
            self.file_folder = new_path
        else:
            self.update_infobox("New file save path not selected")


    def OnImageSettings(self):
        self.update_infobox('Running OnImageSettings')
        new_path = fd.askdirectory(parent=self, initialdir=APP_PATH, title='Please select a directory for saving images')
        if new_path:
            self.update_infobox(["New image save path selected:", new_path])
            self.image_folder = new_path
        else:
            self.update_infobox("New file save path not selected")


    def OnVideoSettings(self):
        self.update_infobox('Running OnVideoSettings')
        new_path = fd.askdirectory(parent=self, initialdir=APP_PATH, title='Please select a directory for saving videos')
        if new_path:
            self.update_infobox(["New video save path selected:", new_path])
            self.video_folder = new_path
        else:
            self.update_infobox("New video path not selected")


    def OnClose(self):
        try:
            self.feed.release()
        except Exception:
            pass
        cv2.destroyAllWindows()
        self.destroy()


if __name__ == "__main__":
    app = BirdCam(feed_index = 1)
    app.mainloop()
