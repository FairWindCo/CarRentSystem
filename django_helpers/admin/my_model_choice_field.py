from django.forms import ModelChoiceField


class MyModelChoiceField(ModelChoiceField):

    def __init__(self, queryset, *, empty_label="---------", required=True, widget=None, label=None, initial=None,
                 help_text='', to_field_name=None, limit_choices_to=None, blank=False, **kwargs):
        self._mquery_set = None
        super().__init__(queryset, empty_label=empty_label, required=required, widget=widget, label=label,
                         initial=initial, help_text=help_text, to_field_name=to_field_name,
                         limit_choices_to=limit_choices_to, blank=blank, **kwargs)

    def _get_queryset(self):
        return self._mquery_set() if callable(self._mquery_set) else self._mquery_set

    def _set_queryset(self, queryset):
        if queryset is None:
            self._mquery_set = None
        elif callable(queryset):
            self._mquery_set = queryset
        else:
            queryset.all()

        self.widget.choices = self.choices

    queryset = property(_get_queryset, _set_queryset)