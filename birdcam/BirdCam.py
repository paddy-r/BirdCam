"""
BirdCam-2000: ALL BIRDS, ALL THE TIME
HPR 08/05/22
HPR 05/03/23 Updating environment setup and adding executable
"""


import cv2
import tkinter as tk
from PIL import Image, ImageTk
# import time
import datetime

def get_available_cameras(max_id = 5):
    ids_available = []

    for idx in range(max_id):
        print('Trying camera ',idx, 'of', max_id, '...')
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
        self.args = args
        self.kwargs = kwargs

        self.title("BirdCam-2000: ALL BIRDS, ALL THE TIME")
        # self.config(background="#FFFFFF")

        self.IMAGE_FILE_DEFAULT = self.get_filename
        self.IMAGE_EXT_DEFAULT = '.png'
        self.VIDEO_FILE_DEFAULT = self.get_filename
        self.VIDEO_EXT_DEFAULT = '.avi'

        ''' Set up feed index etc. '''
        self.FEED_INDEX_DEFAULT = 1
        self.FRAME_RATE_DEFAULT = 10
        self.feed_index = feed_index
        if feed_index and type(feed_index) == int:
            self.feed_index = feed_index
        else:
            self.feed_index = self.FEED_INDEX_DEFAULT

        self._record = False

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
        self.info_text.set("Info box")

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

        ''' Button section'''
        self.button_record = tk.Button(self.button_section,
                                          text = 'Record',
                                          command = self.record)
        self.button_stop = tk.Button(self.button_section,
                                          text = 'Stop',
                                          command = self.stop)
        self.button_grab_frame = tk.Button(self.button_section,
                                              text = 'Grab frame',
                                              command = self.grab_frame)

        self.button_record.grid(row = 0, column = 0, sticky = 'nsew')
        self.button_stop.grid(row = 0, column = 1, sticky = 'nsew')
        self.button_grab_frame.grid(row = 0, column = 2, sticky = 'nsew')

        self.button_section.grid_rowconfigure(0, weight = 1)
        self.button_section.grid_columnconfigure(0, weight = 1)
        self.button_section.grid_columnconfigure(1, weight = 1)
        self.button_section.grid_columnconfigure(2, weight = 1)

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
            print('Trying to connect to camera ', self.feed_index, '...')
            self.connect()
        except Exception as e:
            print('Could not connect to camera', self.feed_index, ', exception follows')
            print(e)



    def record(self, video_file = None):
        if self._record:
            print('Already recording; stop current video first')
            return

        print('Starting video recording...')
        if not video_file:
            video_file = self.VIDEO_FILE_DEFAULT() + self.VIDEO_EXT_DEFAULT

        ''' Get video properties '''
        frame_rate = self.FRAME_RATE_DEFAULT
        w,h = self.get_frame_dimensions()
        if not w or not h:
            print('Could not get frame dimensions; aborting video save')
            return

        ''' Set up video writer object '''
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        print('frame rate:', frame_rate)
        print('w,h:', w,h)
        self.video_out = cv2.VideoWriter(video_file, fourcc, frame_rate, (w,h))
        ''' Allow recording '''
        self._record = True
        self.write_video_frame()


    def write_video_frame(self):
        if self._record:
            ''' Factor of 1000 b/c opencv measures delay in ms '''
            delay = round(1000/self.FRAME_RATE_DEFAULT)
            self.video_out.write(self.frame)
            self.viewer.after(delay, self.write_video_frame)


    def stop(self):
        print('Stopping video recording...')
        ''' Disallow recording '''
        self._record = False
        ''' Dump video to file '''
        print('Saving video...')
        self.video_out.release()



    def grab_frame(self, file = None):
        if not file:
            file = self.IMAGE_FILE_DEFAULT() + self.IMAGE_EXT_DEFAULT
        print('Grabbing video frame...')
        if hasattr(self, 'img'):
            self.img.save(file)
            print('Done')

    def get_filename(self):
        filename = "grab_" + str(datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S'))
        return filename

    ''' Get all available cameras and ask for user input '''
    def OnFindCamera(self):
        print('Running OnFindCamera')
        ''' Get IDs of all available cameras and add to drop-down menu '''
        ids = get_available_cameras()
        print('Found camera IDs:', ids)
        camera_id = CameraSelector(self, ids, text = "Select camera to connect").show()
        print('Camera', camera_id, 'selected; trying to connect...')
        self.feed_index = camera_id
        self.connect()

    ''' Connect to camera by ID '''
    def connect(self):
        self.feed = cv2.VideoCapture(self.feed_index, cv2.CAP_DSHOW)
        print('Got feed', self.feed_index)
        # self.timer = time.time()
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
            self.viewer.after(10, self.grab_feed)

            ''' Cut video recording short, if necessary '''
            if self._record:
                print('Connection to camera lost; stopping video recording and saving video')
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
        print('Running OnSaveLocation')

    def OnImageSettings(self):
        print('Running OnImageSettings')

    def OnVideoSettings(self):
        print('Running OnImageSettings')

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
