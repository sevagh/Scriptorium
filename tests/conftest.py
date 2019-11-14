def pytest_addoption(parser):
    parser.addoption(
        "--webcam-id", action="append", default=[], type=int, help="specify webcam id"
    )


def pytest_generate_tests(metafunc):
    defined_cam = metafunc.config.getoption("webcam_id")
    if "webcam_id" in metafunc.fixturenames and defined_cam:
        metafunc.parametrize("webcam_id", defined_cam)
