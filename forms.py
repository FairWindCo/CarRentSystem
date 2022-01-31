from ajax_select.fields import AutoCompleteSelectMultipleField, AutoCompleteSelectField
from django import forms

from car_management.models import Investor, Car, CarModel


class NewCarForm(forms.ModelForm):
    car_investor = forms.ModelChoiceField(label='Инвестор', queryset=Investor.objects.all())
    model = forms.ModelChoiceField(label='Модель', queryset=CarModel.objects.all())
    car_plate = forms.CharField(label='Государственный номер', max_length=20)
    year = forms.IntegerField(label='Год выпуска', max_value=2100, min_value=1900)
    mileage_at_start = forms.IntegerField(label='Пробег', min_value=0)
    start_amount = forms.IntegerField(label='Стоимость инвестиции', min_value=0)

    class Meta:
        model = Car
        fields = ['car_investor', 'model', 'car_plate', 'year', 'mileage_at_start', 'start_amount']
