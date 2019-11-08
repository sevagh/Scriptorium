import multiprocessing
import dawg
import pickle
import cv2


class WordData:
    def __init__(self, word, auto_definition, img_path):
        self.word = word
        self.img_paths = [img_path]
        self.auto_definition = auto_definition
        self.user_definition = ""
        self.lookups = 0

    def seen_again(self, img_path):
        self.img_paths.append(img_path)

    def set_user_definition(self, user_definition):
        self.user_definition = user_definition

    def __bytes__(self):
        return pickle.dumps(self)

    def __repr__(self):
        self.lookups += 1
        print(self.word)
        print("seen {0} times".format(len(self.img_paths)))
        print("looked up {0} times".format(self.lookups))
        for img_path in self.img_path:
            cv2.imshow(self.img_path)
        if self.auto_definition:
            print(self.auto_definition)
        if self.user_definition:
            print(self.user_definition)

    @staticmethod
    def from_bytes(b):
        return pickle.loads(b)


# https://pymotw.com/2/multiprocessing/communication.html
class DictionaryManager(multiprocessing.Process):
    def __init__(self, word_queue):
        # self.dawg = dawg.BytesDAWG() - we'll use this for future pickling
        self.word_queue = word_queue
        self.exit = False
        self.dictionary = {}
        super().__init__(target=self.run)

    def shutdown(self):
        self.exit = True

    def run(self):
        while not self.exit:
            next_word = self.word_queue.get()
            word, path, definition = next_word
            existing = self.dictionary.get(word, None)
            if existing:
                existing.seen_again(path)
            else:
                self.dictionary[word] = WordData(word, definition, path)
            print(self.dictionary)
