from abc import ABC, abstractmethod

class Node(ABC):

    def __init__(self, value=None):
        self.value = value
        self.children = []

    @abstractmethod
    def evaluate():
        pass


class BinOp(Node):

    def evaluate(self):
        if self.value == '+':
            return self.children[0].evaluate() + self.children[1].evaluate()
        elif self.value == '-':
            return self.children[0].evaluate() - self.children[1].evaluate()
        elif self.value == '*':
            return self.children[0].evaluate() * self.children[1].evaluate()
        elif self.value == '/':
            return self.children[0].evaluate() // self.children[1].evaluate()


class UnOp(Node):

    def evaluate(self):
        if self.value == '+':
            return self.children[0].evaluate()
        elif self.value == '-':
            return -self.children[0].evaluate()


class IntVal(Node):

    def evaluate(self):
        return int(self.value)


class NoOp(Node):
    pass