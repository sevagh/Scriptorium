import scriptorium.camera as sc
import multiprocessing
import queue
import tempfile
import time
import os


def test_camera(webcam_id):
    print("interactive exit/clean shutdown test - click x to close the cam window")
    mgr = multiprocessing.Manager()
    e = multiprocessing.Event()
    q = mgr.Queue()

    with tempfile.TemporaryDirectory(prefix="scriptorium-tests-") as workdir:
        cam_manager = sc.CameraManager((int(webcam_id), 10), q, e, workdir)
        cam_manager.start()

        while cam_manager.is_alive():
            time.sleep(1)

        cam_manager.shutdown()
        cam_manager.join()


def test_camera_ocr_queue(webcam_id):
    print(
        "interactive ocr test - point the camera at a piece of text, press any key to take a snapshot, and click x to close the cam window"
    )

    mgr = multiprocessing.Manager()
    e = multiprocessing.Event()
    q = mgr.Queue()

    # a strange test that requires a functioning camera to be pointing at any kind of text
    count = 0

    with tempfile.TemporaryDirectory(prefix="scriptorium-tests-") as workdir:
        cam_manager = sc.CameraManager((int(webcam_id), 10), q, e, workdir)
        cam_manager.start()

        while cam_manager.is_alive():
            try:
                tup = q.get(timeout=1)
            except queue.Empty:
                continue
            if not tup:
                break
            word, im_path = tup
            count += 1
            assert os.path.isfile(im_path)

        cam_manager.shutdown()
        cam_manager.join()

    assert count > 0
