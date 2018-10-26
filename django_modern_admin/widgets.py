from django import forms
from django.forms.widgets import ChoiceWidget
from django.utils.translation import gettext as _


class ModernTextInputWidget(forms.TextInput):
    def __init__(self, attrs=None):
        final_attrs = {'class': 'vTextField2'}
        if attrs is not None:
            final_attrs.update(attrs)
        super().__init__(attrs=final_attrs)


class _ModernDateWidget(forms.DateInput):

    def __init__(self, attrs=None, format=None):
        attrs = {'class': 'datepicker', 'size': '10', **(attrs or {})}
        super().__init__(attrs=attrs, format=format)


class _ModernTimeWidget(forms.TimeInput):

    def __init__(self, attrs=None, format=None):
        attrs = {'class': 'timepicker', 'size': '8', **(attrs or {})}
        super().__init__(attrs=attrs, format=format)


class ModernSplitDateTime(forms.SplitDateTimeWidget):

    template_name = 'admin/widgets/split_datetime.html'

    def __init__(self, attrs=None):
        widgets = [_ModernDateWidget, _ModernTimeWidget]
        forms.MultiWidget.__init__(self, widgets, attrs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['date_label'] = _('Date:')
        context['time_label'] = _('Time:')
        return context


class ModernSelect(ChoiceWidget):
    input_type = 'select'
    template_name = 'admin/customSelect.html'
    option_template_name = 'admin/customSelectOption.html'
    add_id_index = False
    checked_attribute = {'selected': True}
    option_inherits_attrs = False

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        if self.allow_multiple_selected:
            context['widget']['attrs']['multiple'] = True
        return context

    @staticmethod
    def _choice_has_empty_value(choice):
        """Return True if the choice's value is empty string or None."""
        value, _ = choice
        return value is None or value == ''

    def use_required_attribute(self, initial):
        """
        Don't render 'required' if the first <option> has a value, as that's
        invalid HTML.
        """
        use_required_attribute = super().use_required_attribute(initial)
        # 'required' is always okay for <select multiple>.
        if self.allow_multiple_selected:
            return use_required_attribute

        first_choice = next(iter(self.choices), None)
        return use_required_attribute and first_choice is not None and self._choice_has_empty_value(first_choice)


class ModernSelectMultiple(ModernSelect):
    template_name = 'admin/customMultipleSelect.html'
    allow_multiple_selected = True

    def value_from_datadict(self, data, files, name):
        try:
            getter = data.getlist
        except AttributeError:
            getter = data.get
        return getter(name)

    def value_omitted_from_data(self, data, files, name):
        # An unselected <select multiple> doesn't appear in POST data, so it's
        # never known if the value is actually omitted.
        return False