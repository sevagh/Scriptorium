import tkinter
import cv2
import PIL.Image, PIL.ImageTk
import time
import multiprocessing


# https://solarianprogrammer.com/2018/04/21/python-opencv-show-video-tkinter-window/
class UI(multiprocessing.Process):
    def __init__(self, window_title, video_source, fps):
        self.exit = multiprocessing.Event()

        self.window = tkinter.Tk()
        self.window.title(window_title)
        self.video_source = video_source

        self.vid = VidCap(self.video_source)

        self.canvas = tkinter.Canvas(
            self.window, width=self.vid.width, height=self.vid.height
        )
        self.canvas.pack()

        self.btn_snapshot = tkinter.Button(
            self.window, text="Snapshot", width=50, command=self.snapshot
        )
        self.btn_snapshot.pack(anchor=tkinter.CENTER, expand=True)

        self.delay_ms = int((1.0 / fps) * 1000.0)

        super().__init__(target=self.run)

    def run(self):
        self.update()
        self.window.mainloop()

    def shutdown(self):
        self.exit.set()

    def snapshot(self):
        ret, frame = self.vid.get_frame()
        if ret:
            cv2.imwrite(
                "frame-" + time.strftime("%d-%m-%Y-%H-%M-%S") + ".jpg",
                cv2.cvtColor(frame, cv2.COLOR_RGB2BGR),
            )

    def update(self):
        while not self.exit.is_set():
            ret, frame = self.vid.get_frame()

            if ret:
                self.photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame))
                self.canvas.create_image(0, 0, image=self.photo, anchor=tkinter.NW)

            self.window.after(self.delay_ms, self.update)


class VidCap:
    def __init__(self, video_source):
        self.vid = cv2.VideoCapture(video_source)
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)

        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)

    def get_frame(self):
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            if ret:
                return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            else:
                return (ret, None)
        else:
            return (ret, None)

    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()
