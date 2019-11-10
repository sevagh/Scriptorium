import multiprocessing
import pickle


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
        retstr = ""
        retstr += "{0}\n".format(self.word)
        retstr += "seen {0} times\n".format(len(self.img_paths))
        retstr += "looked up {0} times\n".format(self.lookups)
        retstr += "dict.org definition:\n{0}\n".format(self.auto_definition)
        retstr += "user definition:\n{0}\n".format(self.user_definition)
        return retstr

    @staticmethod
    def from_bytes(b):
        return pickle.loads(b)


class DictionaryManager(multiprocessing.Process):
    def __init__(self, word_queue, word_dict, dictd_host, dictd_port, dictd_db):
        # self.dawg = dawg.BytesDAWG() - we'll use this for future pickling
        self.word_queue = word_queue
        self.exit = False
        self.dictionary = word_dict
        super().__init__(target=self.run)

    def shutdown(self):
        self.exit = True
        super().join(self)

    def run(self):
        while not self.exit:
            next_word = self.word_queue.get()
            word, path = next_word

            # check dict.org, only store words with definitions
            if definition:
                existing = self.dictionary.get(word, None)
                if existing:
                    existing.seen_again(path)
                else:
                    self.dictionary[word] = WordData(word, definition, path)
