import scriptorium.dictionary as sd
import multiprocessing
import queue
import tempfile
import time
import os


def test_scriptorium_dictionary():
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
