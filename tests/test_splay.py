import scriptorium.splay as splay
import os
import random
import timeit
import pytest


@pytest.mark.skip(reason="this is a slow benchmark for manual running")
def test_bench_splay_tree():
    s = splay.SplayTree()
    num_elems = 1000000
    num_iters = 1000

    for r in random.sample(range(1, num_elems), num_elems - 1):
        s.insert(r)

    for r in random.sample(range(1, num_elems), num_iters):
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
        "Amoritzed over {0} elements - second search:third search ratio: {1:.2f}".format(
            r, search3 / search3
        )
    )
