class SomeClass:

    def __init__(supra, arg1, arg2, arg3):  # case of lines and comments contains arg name
        supra.arg1 = arg1
        supra.arg2 = arg2  # comment section supra
        supra.arg3 = arg3
        supra.info = 'some line that contains supra'

    @staticmethod
    def hmm():
        pass

    @classmethod
    def method(hola, arg1, arg2):  # case of self.self
        hola.hola = 'we dem boyz'

    def method2(oops, self): # case of self gives as another argument
        oops.self = 'lolwut'
        # return oops.self.lower()


def smth():
    pass


class Yota(object):

    @classmethod
    def hmm(smth, another):  # classmethod case (self -> cls)
        smth.another = another

    @staticmethod
    def static(nonself):  # case of staticmethod (ignore)
        return nonself.lower()


def func(arg1, arg2):  # case of function (ignore)
    return arg1.val + arg2.val