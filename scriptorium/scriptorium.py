import scriptorium.camera as scriptorium_camera
import scriptorium.dictionary as scriptorium_dictionary
import cmd
import argparse
import readline
import time
from multiprocessing import Manager

# weird
# https://stackoverflow.com/questions/31952711/threading-pyqt-crashes-with-unknown-request-in-queue-while-dequeuing
# QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_X11InitThreads)

TITLE = "Welcome to the Scriptorium"


class Scriptorium(cmd.Cmd):
    def __init__(self, webcam_id, webcam_fps, word_queue, word_dict):
        self.dictionary_mgr = scriptorium_dictionary.DictionaryManager(
            word_queue, word_dict
        )
        self.dictionary_mgr.start()
        self.webcam_id = webcam_id
        self.webcam_fps = webcam_fps
        self.word_queue = word_queue
        super().__init__()

    def do_look(self, word_or_phrase):
        "Print lookup of word or phrase"
        if not word_or_phrase:
            return
        possible_worddata = self.dictionary_mgr.dictionary.get(word_or_phrase, None)
        if possible_worddata:
            print(possible_worddata)
        else:
            print("No definition found")

    def emptyline(self):
        pass

    def do_list(self, *args, **kwargs):
        "Print all words detected from OCR"
        for k in self.dictionary_mgr.dictionary.keys():
            print(k)

    def do_capture(self, *args, **kwargs):
        "Launch an opencv window to capture an image and run OCR on it"
        scriptorium_camera.capture_snapshot_and_ocr(
            self.webcam_id, self.webcam_fps, self.word_queue
        )

    def do_EOF(self, *args, **kwargs):
        print("")
        return True

    def do_exit(self, args):
        self.dictionary_mgr.join()
        return True


def main():
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument(
        "--webcam-id",
        default=0,
        type=int,
        help="integer index of your webam e.g. [/dev/video]N",
    )
    parser.add_argument("--webcam-fps", default=10, type=int, help="webcam fps")
    parser.add_argument(
        "--workdir",
        default=None,
        type=str,
        help="specify path to load and store Scriptorium data",
    )

    args = parser.parse_args()

    manager = Manager()
    # the dictionary and all camera instantiations share OCR words with a Queue
    word_queue = manager.Queue()
    word_dict = manager.dict()

    s = Scriptorium(args.webcam_id, args.webcam_fps, word_queue, word_dict)

    s.cmdloop(intro=TITLE)

    return 0
