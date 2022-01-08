from functools import update_wrapper


def get_model_fields(model):
    fields = {}
    options = model._meta
    for field in sorted(options.concrete_fields + options.many_to_many):
        fields[field.name] = field
    return fields


def wrap(view, self):
    def wrapper(*args, **kwds):
        kwds['admin'] = self  # Use a closure to pass this admin instance to our wizard
        return self.admin_site.admin_view(view)(*args, **kwds)

    return update_wrapper(wrapper, view)