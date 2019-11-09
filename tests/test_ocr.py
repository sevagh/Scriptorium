import scriptorium.ocr as so
import os
import pytesseract
import PIL.Image, PIL.ImageChops


TESTS_DIR = os.path.dirname(os.path.abspath(__file__))


def test_sanitize_word():
    test_words = ["rencontres.", "&", "ans."]
    expected_words = ["rencontres", "", "ans"]
    for i, word in enumerate(test_words):
        assert so.sanitize_word(word) == expected_words[i]


def is_greyscale(im):
    im = im.convert("RGB")
    w, h = im.size
    for i in range(w):
        for j in range(h):
            r, g, b = im.getpixel((i, j))
            if r != g != b:
                return False
    return True


def test_scriptorium_ocr():
    im = PIL.Image.open(os.path.join(TESTS_DIR, "histoire_du_quebec.jpg"))

    smart_ocr_bin = so.OCR(binarize=True)
    smart_ocr_nobin = so.OCR()

    words_ocr_basic = [w for w in pytesseract.image_to_string(im).split()]
    words_ocr_scriptorium_bin, bin_im = smart_ocr_bin.analyze(im)
    words_ocr_scriptorium_nobin, nobin_im = smart_ocr_nobin.analyze(im)

    # i know the test image has at least 100 words on my laptop
    # if it doesn't, maybe it means your OCR setup is messed up
    assert (
        len(words_ocr_basic) > 100
        and len(words_ocr_scriptorium_bin) > 100
        and len(words_ocr_scriptorium_nobin) > 100
    )

    assert (
        im.mode == nobin_im.mode
        and PIL.ImageChops.difference(im, nobin_im).getbbox() is None
    )
    assert (
        im.mode != bin_im.mode
        or PIL.ImageChops.difference(im, bin_im).getbbox() is not None
    )
    assert not is_greyscale(im)
    assert not is_greyscale(nobin_im)
    assert is_greyscale(bin_im)

    words_ocr_basic_san = [so.sanitize_word(word) for word in words_ocr_basic]
    words_ocr_basic_san = [w for w in words_ocr_basic_san if w]

    assert len(words_ocr_basic_san) == len(words_ocr_scriptorium_nobin) and sorted(
        words_ocr_basic_san
    ) == sorted(words_ocr_scriptorium_nobin)

    # assert that binarization changes results... bad idea?
    assert (
        len(words_ocr_scriptorium_nobin) != len(words_ocr_scriptorium_bin)
        and sorted(words_ocr_scriptorium_nobin) != sorted(words_ocr_scriptorium_bin)
    ) or sorted(words_ocr_scriptorium_nobin) != sorted(words_ocr_scriptorium_bin)
