class Column:
    pass


class TestClass:
    class InnerClass:
        pass

    def test_method(self):
        pass

    @classmethod
    def class_method(cls):
        pass

    @staticmethod
    def static_method():
        pass


def outer_func():
    def inner_func():
        pass

    return inner_func
