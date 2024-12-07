from django import forms
from letters.models import Mailing, Message, Customer


class MailingForm(forms.ModelForm):
    class Meta:
        model = Mailing
        fields = '__all__'
        exclude = ['creator', 'attemtps']  # Исключаем поле creator из формы


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = '__all__'


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = '__all__'
