import PIL.Image
from kraken.binarization import nlbin
import pytesseract
from typing import List, Tuple
from types import ModuleType
import unicodedata


def sanitize_word(word: str) -> str:
    left_slice = 0
    while left_slice < len(word) and unicodedata.category(word[left_slice])[0] != "L":
        left_slice += 1
    right_slice = -1
    while (
        right_slice >= -len(word) and unicodedata.category(word[right_slice])[0] != "L"
    ):
        right_slice -= 1
    if right_slice == -1:
        return word[left_slice:]
    else:
        return word[left_slice : right_slice + 1]


class OCR:
    def __init__(self, binarize: bool = False):
        self.binarize = binarize

    def _ocr(self, pil_img: ModuleType) -> List[str]:
        text = pytesseract.image_to_string(pil_img)
        words = [sanitize_word(word) for word in text.split()]
        words = [w for w in words if w]
        return words

    def analyze(self, pil_img: ModuleType) -> Tuple[List[str], ModuleType]:
        if self.binarize:
            pil_img = nlbin(pil_img)
        return self._ocr(pil_img), pil_img
