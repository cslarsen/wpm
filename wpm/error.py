class WpmError(RuntimeError):
    def __init__(self, *args, **kw):
        super(WpmError, self).__init__(*args, **kw)
