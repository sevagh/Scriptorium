import cv2
import PIL.Image
import time
import numpy
from kraken.binarization import nlbin
import pytesseract
import wordbook
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


TITLE = "Press any key to scan, OCR, and exit"


def capture_snapshot_and_ocr(video_source, fps, word_queue):
    vid = cv2.VideoCapture(video_source)
    if not vid.isOpened():
        raise ValueError("Unable to open video source", video_source)

    video_source = video_source

    width = vid.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = vid.get(cv2.CAP_PROP_FRAME_HEIGHT)

    delay_ms = int((1.0 / fps) * 1000.0)

    def get_frame(vid):
        if vid.isOpened():
            ret, frame = vid.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                return (True, frame)
        return (False, None)

    def snapshot(frame):
        pil_img = PIL.Image.fromarray(frame)
        pil_img = nlbin(pil_img)
        text = pytesseract.image_to_string(pil_img)

        filepath = "frame-" + time.strftime("%d-%m-%Y-%H-%M-%S") + ".jpg"
        # store the binarized file for future lookups
        cv2.imwrite(filepath, numpy.array(pil_img))

        # split on whitespace to get whole words
        for word in text.split():
            word_queue.put((word, filepath))

    cv2.namedWindow(TITLE)
    ret, frame = get_frame(vid)

    while ret:
        cv2.imshow(TITLE, frame)
        ret, frame = get_frame(vid)
        key = cv2.waitKey(delay_ms)
        if key != -1:  # any keypress, snapshot + exit
            if ret:
                snapshot(frame)
            break

    cv2.destroyWindow(TITLE)
    if vid.isOpened():
        vid.release()
