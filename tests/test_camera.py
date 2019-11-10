import scriptorium.camera as sc
import multiprocessing
import queue
import tempfile
import time
import os


def test_scriptorium_camera():
    mgr = multiprocessing.Manager()
    q = mgr.Queue()

    with tempfile.TemporaryDirectory(prefix="scriptorium-tests-") as workdir:
        cam_manager = sc.CameraManager((0, 10), q, workdir)
        cam_manager.start()

        while cam_manager.is_alive():
            time.sleep(1)

        cam_manager.shutdown()
        cam_manager.join()


def test_scriptorium_camera_ocr_queue():
    mgr = multiprocessing.Manager()
    q = mgr.Queue()

    # a strange test that requires a functioning camera to be pointing at a printed excerpt of 'Brève histoire du Québec' - https://www.cfqlmc.org/articles-cfqlmc/breve-histoire-du-quebec
    some_examples = ["Anglo-Saxons", "partir", "conquéte"]
    count = 0

    with tempfile.TemporaryDirectory(prefix="scriptorium-tests-") as workdir:
        cam_manager = sc.CameraManager((5, 10), q, workdir)
        cam_manager.start()

        while cam_manager.is_alive():
            try:
                tup = q.get(timeout=1)
            except queue.Empty:
                continue
            if not tup:
                break
            word, im_path = tup
            if word in some_examples:
                count += 1
            assert os.path.isfile(im_path)

        cam_manager.shutdown()
        cam_manager.join()

    assert count >= len(some_examples)
