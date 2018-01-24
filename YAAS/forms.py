from YAAS.models import Auction, Bid
from django import forms
from django.contrib.auth.models import User

'''
class EditForm(forms.Form):
    blogtitle = forms.charField(label='Blog title', max_length=100)
    content = forms.Textarea()
    '''


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)
    email = forms.EmailField(widget=forms.EmailInput)
    username = forms.CharField(widget=forms.TextInput, max_length=30)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2']


class EditPasswordForm(forms.ModelForm):
    old_password = forms.CharField(widget=forms.PasswordInput)
    new_password = forms.CharField(widget=forms.PasswordInput)
    new_password2 = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['old_password', 'new_password', 'new_password2']


class AuctionForm(forms.ModelForm):
    title = forms.CharField(max_length=50, min_length=3)
    description = forms.CharField(widget=forms.Textarea, max_length=10000, min_length=15)
    deadline = forms.IntegerField(min_value=72)
    price = forms.DecimalField(max_digits=8, decimal_places=2, min_value=1)

    class Meta:
        model = Auction
        fields = ['title', 'description', 'price']


class BidOnAuctionForm(forms.ModelForm):
    bid = forms.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        model = Bid
        fields = ['bid']

