import scriptorium.camera as sc
import scriptorium.dictionary as sd
import cmd
import argparse
import readline
import time
import sys
import cv2
import signal
from typing import Dict
import multiprocessing

TITLE = "Welcome to the Scriptorium"


class Scriptorium(cmd.Cmd):
    def __init__(self, webcam_id: int, webcam_fps: int, workdir: str):
        original_sigint_handler = signal.getsignal(signal.SIGINT)
        signal.signal(signal.SIGINT, signal.SIG_IGN)

        self.q = multiprocessing.JoinableQueue()
        d: Dict[str, sd.WordData] = multiprocessing.Manager().dict()

        self.camera_mgr = sc.CameraManager((webcam_id, webcam_fps), self.q, workdir)
        self.dictionary_mgr = sd.DictionaryManager((self.q, d), workdir)
        self.dictionary_mgr.start()
        self.camera_mgr.start()

        signal.signal(signal.SIGINT, handler=original_sigint_handler)

        super().__init__()

    def emptyline(self) -> bool:
        pass

    def do_show(self, word: str) -> None:
        "Show word info"
        if not word:
            return
        try:
            worddata = self.dictionary_mgr.look(word)
            print(worddata)
        except KeyError:
            print("Word is not in dictionary")

    def do_fuzzy(self, prefix: str) -> None:
        "Print stored words that match prefix"
        completion_dawg = self.dictionary_mgr.get_completion_dawg()
        print(" ".join(completion_dawg.keys(prefix)))

    def do_define(self, args: str) -> None:
        "Define word"
        try:
            args_split = args.split()
            word, definition = args_split[0], " ".join(args_split[1:])
            self.dictionary_mgr.define(word, definition)
        except KeyError:
            print("Word is not in dictionary")

    def do_list(self, args: str) -> None:
        "Print all words detected from OCR"
        print(" ".join(self.dictionary_mgr.list()))

    def do_EOF(self, args: str) -> bool:
        print("")
        return self.do_exit(args)

    def do_exit(self, args: str) -> bool:
        self.camera_mgr.shutdown()
        self.camera_mgr.join()
        self.q.join()
        self.q.close()
        self.q.join_thread()
        self.dictionary_mgr.shutdown()
        self.dictionary_mgr.join()
        return True

    def cmdloop_with_keyboard_interrupt(self, intro: str) -> None:
        quit = False
        self.intro = intro
        while not quit:
            try:
                self.cmdloop()
                quit = True
            except KeyboardInterrupt:
                sys.stdout.write("\n")
                self.intro = None


def main() -> int:
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

    s = Scriptorium(args.webcam_id, args.webcam_fps, args.workdir)
    s.cmdloop_with_keyboard_interrupt(TITLE)

    return 0
