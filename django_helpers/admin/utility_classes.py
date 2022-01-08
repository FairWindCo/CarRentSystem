class MyOpts:
    def __init__(self, title, app_label='admin', app_config=None):
        self.app_label = app_label
        self.app_config = app_config if app_config is not None else MyAppConfig(title)
        self.object_name = title


class MyCl:
    def __init__(self, title, opts=None, **kwarg):
        self.opts = opts if opts is not None else MyOpts(title)
        for k, v in kwarg.items():
            setattr(self, k, v)


class MyAppConfig:
    def __init__(self, verbose_name):
        self.verbose_name = verbose_name