import tkinter
from tkinter.messagebox import showinfo
import cv2
import PIL.Image, PIL.ImageTk
import time
import numpy
import multiprocessing
from kraken.binarization import nlbin
import pytesseract
import wordbook
import asyncio
import re


# https://github.com/tomplus/wordbook/blob/83c470a1c8bf1d38322442de4a79dece26626652/example/word-search-cli.py
def format_dictd_line(line):
    line, numr = re.subn(r"^\[(.*)\]\s*$", "\n\x1b[1;33m\\1\x1b[0m\n", line)
    if numr > 0:
        print(line)
        return

    line = re.sub(r"(\[[^\]]+\])", "\x1b[0;33m\\1\x1b[0m", line)
    line = re.sub(r"({[^}]+})", "\x1b[0;36m\\1\x1b[0m", line)
    return line


# https://solarianprogrammer.com/2018/04/21/python-opencv-show-video-tkinter-window/
class UI(multiprocessing.Process):
    def __init__(
        self,
        window_title,
        video_source,
        fps,
        word_queue,
        dictd_host,
        dictd_port,
        dictd_db,
    ):
        self.word_queue = word_queue
        self.window = tkinter.Tk()
        self.window.title(window_title)
        self.video_source = video_source

        self.vid = VidCap(self.video_source)

        self.canvas = tkinter.Canvas(
            self.window, width=self.vid.width, height=self.vid.height
        )
        self.canvas.pack()

        self.btn_snapshot = tkinter.Button(
            self.window, text="SCAN", width=50, command=self.snapshot
        )
        self.btn_snapshot.pack(anchor=tkinter.CENTER, expand=True)

        self.delay_ms = int((1.0 / fps) * 1000.0)

        self.asyncio_loop = asyncio.new_event_loop()
        self.wb = wordbook.WordBook(host=dictd_host, port=dictd_port, database=dictd_db)
        self.asyncio_loop.run_until_complete(self.wb.connect())

        super().__init__(target=self.run)

    def run(self):
        self.update()
        self.window.mainloop()

    def shutdown(self):
        self.window.quit()
        time.sleep(1)
        self.window.destroy()
        self.asyncio_loop.run_until_complete(self.asyncio_loop.shutdown_asyncgens())
        self.asyncio_loop.close()

    def snapshot(self):
        ret, frame = self.vid.get_frame()
        if ret:
            pil_img = PIL.Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
            pil_img = nlbin(pil_img)
            text = pytesseract.image_to_string(pil_img)

            filepath = "frame-" + time.strftime("%d-%m-%Y-%H-%M-%S") + ".jpg"
            # store the binarized file for future lookups
            cv2.imwrite(filepath, numpy.array(pil_img))

            # split on whitespace to get whole words
            for word in text.split():
                # check dict.org, store words with definitions
                definition = self.asyncio_loop.run_until_complete(self.wb.define(word))
                if definition:
                    self.word_queue.put((word, filepath, definition))

            showinfo("SAVED!")

    def update(self):
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
