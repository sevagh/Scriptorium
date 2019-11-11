import scriptorium.camera as sc
import scriptorium.dictionary as sd
import cmd
import argparse
import readline
import time
from multiprocessing import Manager

TITLE = "Welcome to the Scriptorium"


class Scriptorium(cmd.Cmd):
    def __init__(self, webcam_id, webcam_fps, workdir):
        m = Manager()
        q = m.Queue()
        d = m.dict()

        self.camera_mgr = sc.CameraManager((webcam_id, webcam_fps), q, workdir)
        self.dictionary_mgr = sd.DictionaryManager((q, d), workdir)

        self.dictionary_mgr.start()
        self.camera_mgr.start()
        super().__init__()

    def emptyline(self):
        pass

    def do_look(self, word_or_phrase):
        "Print lookup of word or phrase"
        if not word_or_phrase:
            return
        try:
            worddata = self.dictionary_mgr.look(word_or_phrase)
            print(worddata)
        except KeyError:
            print("Word is not in dictionary")

    def do_look_fuzzy(self, prefix):
        "Print stored words that match prefix"
        completion_dawg = self.dictionary_mgr.get_completion_dawg()
        print(" ".join(completion_dawg.keys(prefix)))

    def do_define(self, args):
        "Define word"
        try:
            args = args.split()
            word, definition = args[0], " ".join(args[1:])
            print(word)
            print(definition)
            self.dictionary_mgr.define(word, definition)
        except KeyError:
            print("Word is not in dictionary")

    def do_list(self, *args, **kwargs):
        "Print all words detected from OCR"
        print(" ".join(self.dictionary_mgr.list()))

    def do_EOF(self, *args, **kwargs):
        print("")
        return True

    def do_exit(self, args):
        self.dictionary_mgr.shutdown()
        self.dictionary_mgr.join()
        self.camera_mgr.shutdown()
        self.camera_mgr.join()
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

    s = Scriptorium(args.webcam_id, args.webcam_fps, args.workdir)
    s.cmdloop(intro=TITLE)

    return 0
