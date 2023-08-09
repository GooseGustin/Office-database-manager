from django import forms 
from .models import Job 
from staff.models import Staff 
from inventory.models import Inventory 

class JobCreateForm(forms.ModelForm):

    all_staff_names = [staff.name for staff in Staff.objects.all()]
    all_inv_names = [inv.name for inv in Inventory.objects.all()]
    all_job_statuses = ['Completed', 'Incompleted', 'Cancelled', 'Postponed']

    # Make some fields required and others not 
    staff_assigned = forms.ChoiceField(
        required=True, 
        widget=forms.SelectMultiple(
            attrs={
                'class': 'form-control', 
            },
            choices=all_staff_names
        )
    )
    date = forms.DateField() 
    location = forms.CharField(
        required=False, 
        widget=forms.TextInput(
            attrs={
                'class': 'form-control'
            }
        )
    )
    inventory_used = forms.ChoiceField(
        required=True, 
        widget=forms.SelectMultiple(
            attrs={
                'class': 'form-control', 
            },
            choices=all_inv_names
        )
    )
    other_items = forms.CharField(
        required=False, 
        widget=forms.TextInput(
            attrs={
                'class': 'form-control'
            }
        )
    )
    other_items_costs = forms.CharField(
        required=False, 
        widget=forms.TextInput(
            attrs={
                'class': 'form-control'
            }
        )
    )
    transportation_cost = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control'
            }
        )
    )
    total_expenses = forms.DecimalField(
        required=False, 
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control'
            }
        )
    )
    job_status = forms.ChoiceField(
        required=False, 
        widget=forms.Select(
            attrs={
                'class': 'form-class'
            },
            choices=all_job_statuses
        )
    )
    job_description = forms.CharField(
        required=False, 
        widget=forms.Textarea(
            attrs={
                'class': 'form-control' 
            }
        )
    )
    customer_charge = forms.DecimalField(
        required=False, 
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
    remark = forms.CharField(
        required=False, 
        widget=forms.Textarea(
            attrs={
                'class': 'form-control' 
            }
        )
    )

    class Meta: 
        model = Job 
        fields = [
            'staff_assigned', 
            'date', 
            'location', 
            'inventory_used', 
            # 'other_expenses', 
            'transportation_cost', 
            'total_expenses', 
            'job_status', 
            'job_description', 
            'customer_charge', 
            'customer_name', 
            'customer_phone', 
            'remark'
        ]
