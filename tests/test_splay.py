import scriptorium.splay as splay
import os
import random
import timeit
import hypothesis.strategies as st
from hypothesis.stateful import Bundle, RuleBasedStateMachine, rule


def test_bench_splay_tree():
    s = splay.SplayTree()
    num_elems = 1000000
    num_iters = 1000

    for r in random.sample(range(1, num_elems), num_elems - 1):
        s.insert(r)

    random_searches = []
    for r in random.sample(range(1, num_elems), num_iters):
        random_searches.append(r)
        search1 = 0.0
        search2 = 0.0
        search3 = 0.0

        start_time = timeit.default_timer()
        s.search(r)
        search1 = timeit.default_timer() - start_time

        start_time = timeit.default_timer()
        s.search(r)
        search2 = timeit.default_timer() - start_time

        start_time = timeit.default_timer()
        s.search(r)
        search3 = timeit.default_timer() - start_time

    search1 /= num_iters
    search2 /= num_iters
    search3 /= num_iters

    assert search1 > search2
    assert search1 > search3
    print(
        "Amortized over {0} elements - first search:second search ratio: {1:.2f}".format(
            r, search1 / search2
        )
    )
    print(
        "Amortized over {0} elements - second search:third search ratio: {1:.2f}".format(
            r, search3 / search3
        )
    )


def test_splay_tree():
    s = splay.SplayTree()

    s.insert(1)

    assert s.nodes[s.root].key == 1
    assert s.nodes[s.root].children == [splay.NULL, splay.NULL]
    assert s.nodes[s.root].parent == splay.NULL

    s.insert(2)
    assert s.nodes[s.root].key == 2
    assert s.nodes[s.root].children == [0, splay.NULL]
    assert s.nodes[s.root].parent == splay.NULL
    assert s.nodes[s.nodes[s.root].children[0]].key == 1
    assert s.nodes[s.nodes[s.root].children[0]].parent == s.root

    s.insert(3)
    assert s.nodes[s.root].key == 3
    assert s.nodes[s.root].children == [1, splay.NULL]
    assert s.nodes[s.root].parent == splay.NULL
    assert s.nodes[s.nodes[s.root].children[0]].key == 2
    assert s.nodes[s.nodes[s.root].children[0]].children == [0, splay.NULL]
    assert s.nodes[s.nodes[s.root].children[0]].parent == s.root
    assert s.nodes[s.nodes[s.nodes[s.root].children[0]].children[0]].key == 1
    assert s.nodes[s.nodes[s.nodes[s.root].children[0]].children[0]].parent == 1


class SplayTreeComparison(RuleBasedStateMachine):
    def __init__(self):
        super(SplayTreeComparison, self).__init__()
        self.model = splay.SplayTree()
        self.control = []

    keys = Bundle("keys")

    @rule(target=keys, k=st.characters())
    def add_key(self, k):
        return k

    @rule(k=keys)
    def save(self, k):
        self.model.insert(k)
        self.control.append(k)

    @rule(k=keys)
    def values_agree(self, k):
        try:
            assert self.control[self.control.index(k)] == self.model.search(k)
        except ValueError as e:
            first_v_e = None
            second_v_e = None
            try:
                self.control[self.control.index(k)]
            except ValueError as e:
                first_v_e = e
            try:
                self.model.search(k)
            except ValueError as e:
                second_v_e = e
            assert " is not in list" in str(first_v_e)
            assert " is not in SplayTree" in str(second_v_e)


TestSplayTreeComparison = SplayTreeComparison.TestCase
