from django import forms 
from .models import Sale
from inventory.models import Inventory 

class SaleCreationForm(forms.ModelForm):

    goods_choices = [
        (inv, inv.name) for inv in Inventory.objects.all()
    ]
    goods_sold = forms.MultipleChoiceField(
        choices=goods_choices, 
        widget=forms.CheckboxSelectMultiple(), 
        required=True
    )
    profit = forms.DecimalField(
        required=True, 
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control' 
            }
        )
    )
    customer_name = forms.CharField(
        required=False, 
        widget=forms.TextInput(
            attrs={
                'class': 'form-control' 
            }
        )
    )
    customer_phone = forms.CharField(
        required=False, 
        widget=forms.TextInput(
            attrs={
                'class': 'form-control' 
            }
        )
    )
    date = forms.DateField(
        required=False, 
        widget=forms.DateInput(
            attrs={
                'class': 'form-control'
            }
        )
    )
    remark = forms.CharField(
        required=False, 
        widget=forms.Textarea(
            attrs={
                'class': 'form-control'
            }
        )
    )

    class Meta:
        model = Sale 
        fields = '__all__' 

