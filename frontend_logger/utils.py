
class Cascade(object):

    def __init__(self, *funcs):
        self.funcs = funcs

    def __call__(self, *args, **kwargs):
        funcs = list(self.funcs)
        funcs.reverse()
        result = funcs.pop()(*args, **kwargs)
        while funcs:
            result = funcs.pop()(result)
        return result


class FuncWrapper(object):

    def __init__(self, func, arg_num=0, *f_args, **f_kwargs):
        self.func = func
        self.arg_num = arg_num
        if f_args:
            self.f_args = f_args
        else:
            self.f_args = []
        if f_kwargs:
            self.f_kwargs = f_kwargs
        else:
            self.f_kwargs = {}

    def __call__(self, o):
        args = list(self.f_args)
        args.insert(self.arg_num, o)
        kwargs = self.f_kwargs
        return self.func(*args, **kwargs)
