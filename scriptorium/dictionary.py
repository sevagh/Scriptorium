import multiprocessing
import pickle
import queue
import dawg
import os
from typing import List, Tuple, Dict
import time


class WordData:
    def __init__(self, word: str, paths: List[str], lookups: int, definition: str):
        self.word = word
        self.paths = paths
        self.lookups = lookups
        self.definition = definition

    def __bytes__(self) -> bytes:
        return pickle.dumps(self)

    def __repr__(self) -> str:
        retstr = ""
        retstr += "{0}\n".format(self.word)
        retstr += "  seen {0} times\n".format(len(self.paths))
        retstr += "  looked up {0} times\n".format(self.lookups)
        if self.definition:
            retstr += "  definition:  {0}\n".format(self.definition)
        if any([p for p in self.paths]):
            retstr += "\nappears in:\n"
        for p in self.paths:
            if p:
                retstr += "\t{0}\n".format(p)
        return retstr[:-1]

    @staticmethod
    def frombytes(b: bytes) -> "WordData":
        return pickle.loads(b)


class DictionaryManager(multiprocessing.Process):
    persist_name = "scriptorium.dawg"

    def __init__(
        self,
        word_structs: Tuple[multiprocessing.Queue, Dict[str, WordData]],
        workdir: str,
    ):
        self.word_queue, self.word_dict = word_structs
        self.alive = multiprocessing.Event()
        self.alive.set()
        self.workdir = workdir
        self._load_bytes_dawg()

        super().__init__(target=self.run)

    def _load_bytes_dawg(self) -> None:
        if self.workdir and os.path.isdir(self.workdir):
            bytes_dawg_path = os.path.join(self.workdir, DictionaryManager.persist_name)
            if os.path.isfile(bytes_dawg_path):
                bytes_dawg = dawg.BytesDAWG()
                bytes_dawg.load(bytes_dawg_path)
                for k, v in bytes_dawg.iteritems():
                    self.word_dict[k] = WordData.frombytes(v)
                self.completion_dawg = dawg.CompletionDAWG(self.word_dict.keys())

    def _persist_bytes_dawg(self) -> None:
        if self.workdir and len(self.word_dict) > 0:
            if not os.path.isdir(self.workdir):
                print(
                    "[BytesDAWG] Are you sure {0} is a directory? Not persisting dictionary.".format(
                        self.workdir
                    )
                )
                return
            bytes_dawg_path = os.path.join(self.workdir, DictionaryManager.persist_name)
            bytes_dawg = dawg.BytesDAWG(
                [(k, bytes(v)) for k, v in self.word_dict.items()]
            )
            try:
                bytes_dawg.save(bytes_dawg_path)
            except FileNotFoundError:
                print(
                    "[BytesDAWG] Couldn't persist dictionary to path {0}, are you sure the workdir exists and is writeable?".format(
                        bytes_dawg_path
                    )
                )

    def shutdown(self) -> None:
        self._persist_bytes_dawg()
        self.alive.clear()

    def get_completion_dawg(self) -> dawg.CompletionDAWG:
        return dawg.CompletionDAWG(self.word_dict.keys())

    def run(self) -> None:
        while self.alive.is_set():
            next_word = None
            try:
                next_word = self.word_queue.get(timeout=1)
                word, path = next_word
                exist = self.word_dict.get(word, None)
                if exist:
                    self.word_dict[word] = WordData(
                        exist.word,
                        exist.paths + [path],
                        exist.lookups,
                        exist.definition,
                    )
                else:
                    self.word_dict[word] = WordData(word, [path], 0, "")
                self.word_queue.task_done()
            except queue.Empty:
                continue

    def look(self, word: str) -> WordData:
        exist = self.word_dict.get(word, None)
        if exist:
            self.word_dict[word] = WordData(
                exist.word, exist.paths, exist.lookups + 1, exist.definition
            )
            return self.word_dict[word]
        raise KeyError

    def list(self) -> List[str]:
        return list(self.word_dict.keys())

    def define(self, word: str, definition: str) -> None:
        exist = self.word_dict.get(word, None)
        if exist:
            self.word_dict[word] = WordData(
                exist.word, exist.paths, exist.lookups, definition
            )
            return
        raise KeyError
