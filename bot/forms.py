from django.forms import ModelForm
from django import forms
from .models import Ad, LocalUser
from django.contrib.admin import widgets
from django.contrib.auth.models import User


# Create the form class.
class HorizontalForm(ModelForm):
    class Meta:
        model = Ad
        fields = ['min_price', 'max_price', 'step', 'max_amount', 'price_limit', 'amount_limit', 'is_updated']


class CreateBot(ModelForm):
    class Meta:
        model = Ad

        fields = ['ad_id',
                  'direction',
                  'online_provider',
                  'currency',
                  'bank_name',
                  'min_price',
                  'max_price',
                  'max_amount',
                  'account_info',
                  'msg',
                  'price_limit',
                  'amount_limit',
                  'min_amount_filter',
                  'ad_creation_time_filter',
                  'delta_amount_filter',
                  'phone_number',
                  'step',
                  'steps_quantity',
                  'ignored_logins',
                  'invisible_trade_ids',
                  'price_rollback',
                  'rollback_time',
                  'call_frequency',
                  'start_msg',
                  'finish_msg',
                  'is_top_fifteen',
                  'is_updated', ]

        widgets = {
            'ad_creation_time_filter': forms.DateInput(attrs={'class': 'datepicker'}),
        }

    def save_with_user(self, user, commit=True):
        new_bot = ModelForm.save(self, commit=False)
        new_bot.user = user
        if commit:
            new_bot.save()
        return new_bot


class HmacForm(ModelForm):
    class Meta:
        model = LocalUser
        fields = ['login', 'hmac_key', 'hmac_secret']

    def save_with_user(self, user, commit=True):
        new_key = ModelForm.save(self, commit=False)
        new_key.user = user
        if commit:
            new_key.save()
        return new_key
