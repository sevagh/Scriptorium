import scriptorium.camera as scriptorium_camera
import wordbook
import cmd
import argparse
import readline
import asyncio
import re
import time

TITLE = "Welcome to the Scriptorium"


# https://github.com/tomplus/wordbook/blob/83c470a1c8bf1d38322442de4a79dece26626652/example/word-search-cli.py
def print_line(line):
    line, numr = re.subn(r"^\[(.*)\]\s*$", "\n\x1b[1;33m\\1\x1b[0m\n", line)
    if numr > 0:
        print(line)
        return

    line = re.sub(r"(\[[^\]]+\])", "\x1b[0;33m\\1\x1b[0m", line)
    line = re.sub(r"({[^}]+})", "\x1b[0;36m\\1\x1b[0m", line)
    print(line)


class Scriptorium(cmd.Cmd):
    def __init__(self, *args, **kwargs):
        self.asyncio_loop = asyncio.new_event_loop()
        self.wb = wordbook.WordBook(host=args[0], port=args[1], database=args[2])
        self.asyncio_loop.run_until_complete(self.wb.connect())
        super().__init__()

    def do_look(self, word_or_phrase):
        "Print lookup of word or phrase"
        if not word_or_phrase:
            return
        defines = self.asyncio_loop.run_until_complete(self.wb.define(word_or_phrase))
        if defines:
            for define in defines:
                print_line(define)
            print()
        else:
            print("No definition found")

    def do_EOF(self, *args, **kwargs):
        print("")
        return True

    def cleanup(self):
        self.asyncio_loop.run_until_complete(self.asyncio_loop.shutdown_asyncgens())
        self.asyncio_loop.close()


def main():
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument(
        "--webcam-id",
        default=0,
        type=int,
        help="integer index of your webam e.g. [/dev/video]N",
    )
    parser.add_argument("--webcam-fps", default=15, type=int, help="webcam fps")
    parser.add_argument("--dictd-host", default="dict.org", type=str, help="dictd host")
    parser.add_argument("--dictd-port", default=2628, type=int, help="dictd port")
    parser.add_argument(
        "--dictd-db", default="fd-fra-eng", type=str, help="dictd db to use"
    )
    parser.add_argument(
        "--workdir",
        default=None,
        type=str,
        help="specify path to load and store Scriptorium data",
    )

    args = parser.parse_args()

    ui = scriptorium_camera.UI(TITLE, args.webcam_id, args.webcam_fps)
    ui.start()

    s = Scriptorium(args.dictd_host, args.dictd_port, args.dictd_db)

    s.cmdloop(intro=TITLE)
    s.cleanup()

    ui.shutdown()
    while ui.is_alive():
        print("Waiting 1s to verify clean shutdown of the webcam process...")
        time.sleep(1)
    ui.join()

    return 0
