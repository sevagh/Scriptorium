import scriptorium.camera as sc
import multiprocessing
import tempfile
import time


def test_scriptorium_camera():
    mgr = multiprocessing.Manager()
    queue = mgr.Queue()
    with tempfile.TemporaryDirectory(prefix="scriptorium-tests-") as workdir:
        cam_manager = sc.CameraManager(0, 10, queue, workdir)
        cam_manager.start()

        while cam_manager.is_alive():
            time.sleep(1)

        cam_manager.shutdown()
        cam_manager.join()
