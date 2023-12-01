import json

class Foo:
    class Node:
        def __init__(self, val):
            self.val = val
    def __init__(self):
        self.left = Foo.Node(1)
        self.right = Foo.Node(2)



a = Foo()
s = json.dumps(a.__dict__)

b = json.loads(s)
print(b)
