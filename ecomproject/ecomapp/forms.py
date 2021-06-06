from django import forms
from .models import Order, Customer, Category, Product, Admin
from django.contrib.auth.models import User


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['ordered_by', 'shipping_address', 'mobile', 'email', ]


class CustomerRegistrationForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput())
    password = forms.CharField(widget=forms.PasswordInput())
    email = forms.CharField(widget=forms.EmailInput())

    class Meta:
        model = Customer
        fields = ["username", "full_name", "password",
                  "email", "address"]

    def clean_username(self):
        uname = self.cleaned_data.get('username')
        # if user with uname exists
        if User.objects.filter(username=uname).exists():
            raise forms.ValidationError("Customer with the username already exists.")

        return uname

    def clean_email(self):
        uemail = self.cleaned_data.get('email')
        # if user with uname exists
        if User.objects.filter(email=uemail).exists():
            raise forms.ValidationError("Customer with the email already exists.")

        return uemail

    # def clean_password(self):
    #     upwd = self.cleaned_data.get('password')
    #     # if user with uname exists
    #     if len(upwd) >= 8 and (upwd.contains('%', '*', '!')):
    #         pass
    #     else:
    #         raise forms.ValidationError("Password must be greater than 8 characters.")
    #
    #     return upwd


class CustomerLoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput())
    password = forms.CharField(widget=forms.PasswordInput())


# admin section
class AdminCreateCategoryForm(forms.ModelForm):

    class Meta:
        model = Category
        fields = ['title', 'slug']

class AdminCreateProductForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = "__all__"

class AdminProfileUpdateForm(forms.ModelForm):

    class Meta:
        model = Admin
        fields = "__all__"

class AdminCategoryUpdateForm(forms.ModelForm):

    class Meta:
        model = Category
        fields = "__all__"
