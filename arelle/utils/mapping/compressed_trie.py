"""
See COPYRIGHT.md for copyright information.
"""

from typing import Union, Tuple
from json import JSONEncoder, JSONDecoder

# ─────────────────────────────────────────────────────────────────────
# Compressed Trie (Patricia / Radix trie – merge single-child chains)
# ─────────────────────────────────────────────────────────────────────

class CompressedNode:
    __slots__ = ('children', 'value')
    def __init__(self):
        # child maps an edge label (string) to a child node
        self.children: dict[str, CompressedNode] = {}
        self.value: Union[str,None] = None


class CompressedTrie:
    NAME = "Compressed Trie"

    def __init__(self):
        self.root = CompressedNode()

    def add(self, key: str, value: str) -> None:
        node = self.root
        i = 0
        while i < len(key):
            found = False
            for label, child in node.children.items():
                # Find the common prefix between the remaining key and this edge label
                common = 0
                while common < len(label) and i + common < len(key) and label[common] == key[i + common]:
                    common += 1

                if common == 0:
                    continue

                found = True
                if common == len(label):
                    # Full edge consumed, descend
                    node = child
                    i += common
                else:
                    # Partial match: split the edge
                    # label = common_part + remaining_label
                    mid = CompressedNode()
                    remaining_label = label[common:]
                    mid.children[remaining_label] = child

                    del node.children[label]
                    node.children[label[:common]] = mid

                    node = mid
                    i += common
                break

            if not found:
                # No matching edge, create a new one
                new_node = CompressedNode()
                new_node.value = value
                node.children[key[i:]] = new_node
                return

        node.value = value

    def remove(self, key: str) -> bool:
        # Collect path: (parent_node, edge_label, child_node)
        path: list[tuple[CompressedNode, str, CompressedNode]] = []
        node = self.root
        i = 0
        while i < len(key):
            found = False
            for label, child in node.children.items():
                if key[i:i + len(label)] == label:
                    path.append((node, label, child))
                    node = child
                    i += len(label)
                    found = True
                    break
            if not found:
                return False

        if node.value is None:
            return False
        node.value = None

        # Prune: remove childless valueless leaves, then merge single-child nodes
        for parent, label, child in reversed(path):
            if not child.children and child.value is None:
                del parent.children[label]
            elif len(child.children) == 1 and child.value is None:
                # Merge the child with its single grandchild
                sub_label, grandchild = next(iter(child.children.items()))
                del parent.children[label]
                parent.children[label + sub_label] = grandchild
                break
            else:
                break
        return True

    def clear(self) -> None:
        del self.root
        self.root = CompressedNode()

    def toDict(self) -> dict[str, str]:
        result = {}
        def traverse(node, prefix):
            if node.value is not None:
                result[prefix] = node.value
            for label, child in node.children.items():
                traverse(child, prefix + label)
        traverse(self.root, '')
        return result

    def addFromDict(self, d: dict[str, str], exclude_class_flag: bool = False) -> None:
        if exclude_class_flag:
            for key, value in d.items():
                if key != "__class__":
                    self.add(key, value)
        else:
            for key, value in d.items():
                self.add(key, value)

    def loadFromDict(self, d: dict[str, str], exclude_class_flag: bool = False) -> None:
        self.clear()
        self.addFromDict(d, exclude_class_flag=exclude_class_flag)

    def longest_prefix_match(self, s: str) -> Tuple[Union[str, None], Union[str, None]]:
        node = self.root
        match = None
        i = 0
        while i < len(s):
            found = False
            for label, child in node.children.items():
                label_length = len(label)
                if s[i:i + label_length] == label:
                    i += label_length
                    node = child
                    if node.value is not None:
                        match = node.value
                    found = True
                    break
            if not found:
                break
        longest_prefix = s[:i] if i > 0 else None
        return longest_prefix, match

    def get(self, key: str, default: Union[str, None] = None) -> Union[str, None]:
        result =default
        found_prefix, found_value = self.longest_prefix_match(key)
        if found_prefix and found_value and len(found_prefix) == len(key):
            result = found_value
        return result

    def is_prefix_matching(self, key: str) -> bool:
        found_prefix, found_value = self.longest_prefix_match(key)
        return found_prefix and found_value is not None

    def __len__(self) -> int:
        return len(self.toDict())

    def __setitem__(self, key: str, value: str) -> None:
        self.add(key, value)

    def __getitem__(self, key: str) -> Union[str, None]:
        return self.get(key)

    def __contains__(self, key: str) -> bool:
        found_prefix, found_value = self.longest_prefix_match(key)
        return found_prefix and found_value and len(found_prefix) == len(key)

class CompressedTrieEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, CompressedTrie):
            result = obj.toDict()
            result["__class__"] = CompressedTrie.NAME
        return super().default(obj)

class CompressedTrieDecoder(JSONDecoder):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, object_hook=self.object_hook, **kwargs)

    def object_hook(self, obj):
        if "__class__" in obj and obj["__class__"] == CompressedTrie.NAME:
            trie = CompressedTrie()
            trie.addFromDict(obj, exclude_class_flag=True)
            return trie
        return obj