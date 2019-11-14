import sys
from typing import List

"""
Adapted from https://gist.github.com/stjepang/07fbf88afa824e11796e51ea2f68bd5a

Theoretical implementation are from Goodrich & Tamassia

Deletions not implemented because I won't use them
"""

NULL = sys.maxsize
_LEFT = 0
_RIGHT = 1


class _Node:
    def __init__(self, key: str):
        self.key = key
        self.children: List[str] = [NULL, NULL]
        self.parent = NULL

    def __repr__(self) -> str:
        return "(key: {0}, parent: {1}, children: {2})".format(
            str(self.key), self.parent, self.children
        )


class SplayTree:
    def __init__(self) -> None:
        self.nodes: List[_Node] = []
        self.root = NULL

    def link(self, parent: int, child: int, direction: int) -> None:
        self.nodes[parent].children[direction] = child
        if child != NULL:
            self.nodes[child].parent = parent

    def rotate(self, parent: int, curr: int) -> None:
        grandparent = self.nodes[parent].parent

        # direction of parent-child relationship
        direction = _RIGHT
        if self.nodes[parent].children[_LEFT] == curr:
            direction = _LEFT

        t = self.nodes[curr].children[1 - direction]
        self.link(parent, t, direction)
        self.link(curr, parent, 1 - direction)

        if grandparent == NULL:
            self.root = curr
            self.nodes[curr].parent = NULL
        else:
            direction = _RIGHT
            if self.nodes[grandparent].children[_LEFT] == parent:
                direction = _LEFT
            self.link(grandparent, curr, direction)

    def splay(self, curr: int) -> None:
        while True:
            parent = self.nodes[curr].parent
            if parent == NULL:
                break

            grandparent = self.nodes[parent].parent
            if grandparent == NULL:
                # zig
                self.rotate(parent, curr)
                break

            # check same-directionality of grandparent-parent and parent-curr
            if (self.nodes[grandparent].children[_LEFT] == parent) == (
                self.nodes[parent].children[_LEFT] == curr
            ):
                # zig-zig
                self.rotate(grandparent, parent)
                self.rotate(parent, curr)
            else:
                # zig-zag
                self.rotate(parent, curr)
                self.rotate(grandparent, curr)

    def insert(self, key: str) -> None:
        new = len(self.nodes)
        self.nodes.append(_Node(key))

        if self.root == NULL:
            self.root = new
        else:
            parent = self.root
            while True:
                direction = _RIGHT
                if self.nodes[new].key < self.nodes[parent].key:
                    direction = _LEFT
                curr = self.nodes[parent].children[direction]
                if curr == NULL:
                    self.link(parent, new, direction)
                    self.splay(new)
                    break
                parent = curr

    def recentk(self, k: int) -> List[str]:
        """do a little bfs to return k nodes at the top of the splay tree - no splaying, this shouldn't mutate the tree"""
        """unscientific as heck"""
        recentk = []
        q = [self.root]
        while q and len(recentk) < k:
            curr, q = q[0], q[1:]
            recentk.append(self.nodes[curr].key)
            for c in self.nodes[curr].children:
                if c != NULL:
                    q.append(c)
        return recentk

    def search(self, key: str) -> str:
        if self.root == NULL:
            raise ValueError(key + " is not in SplayTree".format(key))
        parent = self.root
        while True:
            direction = _RIGHT
            key_cmp = self.nodes[parent].key
            # Goodrich Tamassia - successful search = splay the found node
            if key == key_cmp:
                self.splay(parent)
                return key_cmp
            elif key < self.nodes[parent].key:
                direction = _LEFT

            curr = self.nodes[parent].children[direction]

            # Goodrich Tamassia - unsuccessful search = splay last parent
            # raise ValueError
            if curr == NULL:
                self.splay(parent)
                raise ValueError(key + " is not in SplayTree".format(key))
            parent = curr
