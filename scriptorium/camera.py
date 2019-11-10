import cv2
import PIL.Image
import time
import numpy
from typing import List, Tuple
from types import ModuleType
import os
import multiprocessing
from .ocr import OCR


class CameraManager(multiprocessing.Process):
    title = "Press any key to scan - close window to exit"

    def __init__(
        self,
        cam_opts: Tuple[int, int],
        word_queue: multiprocessing.Queue,
        workdir: str,
        binarize: bool = False,
    ):
        video_source, fps = cam_opts

        vid = cv2.VideoCapture(video_source)
        if not vid.isOpened():
            raise ValueError("Unable to open video source", video_source)

        self.vid = vid
        self.delay_ms = int((1.0 / fps) * 1000.0)
        self.workdir = workdir
        self.word_queue = word_queue
        self.ocr = OCR(binarize)
        self.alive = multiprocessing.Event()
        self.alive.set()
        super().__init__(target=self.run)

    def _get_frame(self) -> Tuple[bool, numpy.ndarray]:
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                return (True, frame)
        return (False, None)

    def snapshot(self, frame: numpy.ndarray):
        pil_im = PIL.Image.fromarray(frame)
        filepath = os.path.join(
            self.workdir, "frame-" + time.strftime("%d-%m-%Y-%H-%M-%S") + ".jpg"
        )
        words, im = self.ocr.analyze(pil_im)
        if len(words) > 0:
            cv2.imwrite(filepath, numpy.array(im))
        for word in words:
            self.word_queue.put((word, filepath))
        self.word_queue.put(
            None
        )  # use a 'poison pill' simply to mark the end of a stream

    def run(self):
        cv2.namedWindow(CameraManager.title)
        ret, frame = self._get_frame()

        while self.alive.is_set():
            cv2.imshow(CameraManager.title, frame)
            ret, frame = self._get_frame()
            key = cv2.waitKey(self.delay_ms)
            if key != -1:  # any keypress, snapshot
                if ret:
                    self.snapshot(frame)
                    frame = 0  # 'flash' the webcam feed to indicate a capture
            elif (
                cv2.getWindowProperty(CameraManager.title, cv2.WND_PROP_VISIBLE) == 0
            ):  # esc
                break

        return

    def shutdown(self):
        self.alive.clear()
        time.sleep(3.0 * self.delay_ms / 1000.0)
        cv2.waitKey(0)
        try:
            cv2.destroyWindow(CameraManager.title)
        except cv2.error as e:
            pass
        except Exception as e:
            raise e
        cv2.destroyAllWindows()
        if self.vid.isOpened():
            self.vid.release()
