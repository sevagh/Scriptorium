import scriptorium.dictionary as sd
import multiprocessing
import queue
import tempfile
import time
import os
import itertools
from pathlib import Path
from resource import getpagesize

PAGESIZE = getpagesize()
STATM_PATH = Path("/proc/self/statm")


def get_resident_set_size() -> int:
    """Return the current resident set size in MB."""
    # statm columns are: size resident shared text lib data dt
    statm = STATM_PATH.read_text()
    fields = statm.split()
    return (int(fields[1]) * PAGESIZE) / 1000000.0


def test_dictionary():
    mgr = multiprocessing.Manager()
    q = mgr.Queue()
    d = mgr.dict()

    test_words = ["test1", "test2", "test3"]

    with tempfile.TemporaryDirectory(prefix="scriptorium-tests-") as workdir:
        dict_manager = sd.DictionaryManager((q, d), workdir)
        dict_manager.start()

        for word in test_words:
            try:
                q.put((word, "fakepath.jpg"), 1)
            except queue.Full:
                continue
        q.put(("test1", "fakepath2.jpg"))

        time.sleep(1)

        assert d["test1"].paths == ["fakepath.jpg", "fakepath2.jpg"]
        assert d["test1"].lookups == 0
        assert d["test2"].paths == ["fakepath.jpg"]
        assert d["test3"].paths == ["fakepath.jpg"]

        val = dict_manager.look("test1")
        assert val.paths == ["fakepath.jpg", "fakepath2.jpg"]
        assert val.word == "test1"
        assert val.lookups == 1
        assert val.definition == ""

        # mutate a word
        dict_manager.define("test1", "test_def")

        val = dict_manager.look("test1")
        assert val.lookups == 2
        assert val.definition == "test_def"

        bytes_dawg_path = os.path.join(
            dict_manager.workdir, sd.DictionaryManager.persist_name
        )

        completion = dict_manager.get_completion_dawg()
        test_words_from_dawg = completion.keys("test")
        assert test_words_from_dawg == test_words

        dict_manager.shutdown()
        dict_manager.join()

        assert os.path.isfile(bytes_dawg_path)

        # load one from the previous
        d.clear()

        dict_manager2 = sd.DictionaryManager((q, d), workdir)
        dict_manager2.start()

        time.sleep(1)

        words = dict_manager2.list()
        assert words == test_words

        val = dict_manager.look("test1")

        assert val.paths == ["fakepath.jpg", "fakepath2.jpg"]
        assert val.word == "test1"
        assert val.lookups == 3
        assert val.definition == "test_def"

        # mutate a word again
        dict_manager.define("test1", "test_def2")

        val = dict_manager.look("test1")
        assert val.lookups == 4
        assert val.definition == "test_def2"

        dict_manager2.shutdown()
        dict_manager2.join()


def test_dictionary_memory_big():
    _test_dictionary_memory()


def test_dictionary_memory_typical():
    _test_dictionary_memory(num_words=100000)


def _test_dictionary_memory(num_words=-1):
    mgr = multiprocessing.Manager()
    q = mgr.Queue()
    d = mgr.dict()

    with tempfile.TemporaryDirectory(prefix="scriptorium-tests-") as workdir:
        start_memory = get_resident_set_size()

        dict_manager = sd.DictionaryManager((q, d), workdir)
        dict_manager.start()

        word_count = 0
        for word in itertools.permutations("abcdefghij"):
            q.put(("".join(word), ""))
            word_count += 1
            if num_words > 0 and word_count >= num_words:
                break
        time.sleep(2)

        print(
            "{0}MB after storing {1} words".format(
                get_resident_set_size() - start_memory, word_count
            )
        )

        cd = dict_manager.get_completion_dawg()
        print(
            "{0}MB after getting completion dawg".format(
                get_resident_set_size() - start_memory
            )
        )

        dict_manager._persist_bytes_dawg()
        print(
            "{0}MB after persisting bytes dawg".format(
                get_resident_set_size() - start_memory
            )
        )

        bytes_dawg_path = os.path.join(
            dict_manager.workdir, sd.DictionaryManager.persist_name
        )

        print(
            "{0}MB bytes dawg size on disk".format(
                os.path.getsize(bytes_dawg_path) / 1000000.0
            )
        )

        dict_manager.shutdown()
        dict_manager.join()

        d.clear()

        print(
            "{0}MB after shutdown + clear old DictionaryManager".format(
                get_resident_set_size() - start_memory
            )
        )

        dict_manager2 = sd.DictionaryManager((q, d), workdir)
        dict_manager2.start()

        time.sleep(1)

        print(
            "{0}MB after load new DictionaryManager from previous bytes dawg".format(
                get_resident_set_size() - start_memory
            )
        )

        dict_manager2.shutdown()
        dict_manager2.join()

    print(
        "{0}MB after the end of everything".format(
            get_resident_set_size() - start_memory
        )
    )
