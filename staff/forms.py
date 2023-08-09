from django import forms
from .models import Staff 

class StaffCreateForm(forms.ModelForm):
    name = forms.CharField(
                required=True, 
                widget=forms.TextInput(
                    attrs={
                        'class': 'form-control', 
                        'id': 'name', 
                        'placeholder': 'Name' 
                    }
                )
                ) 
    date_of_birth = forms.DateField(
                widget=forms.DateInput(
                    attrs={
                        'class': 'form-control',
                        'placeholder': 'Date of Birth'
                    }
                )
    )
    state_of_origin = forms.CharField(
                widget=forms.TextInput(
                    attrs={
                        'class': 'form-control', 
                        'id': 'state_of_origin', 
                        'placeholder': 'State of origin'
                    }
                )
    )
    phone = forms.CharField(
                widget=forms.TextInput(
                    attrs={
                        'class': 'form-control', 
                        'id': 'phone', 
                        'placeholder': 'Phone number'
                    }
                )
    )
    email = forms.EmailField(
                widget=forms.EmailInput(
                    attrs={
                        'class': 'form-control', 
                        'id': 'email', 
                        'placeholder': 'Email' 
                    }
                )
            )
    home_residence = forms.CharField(
                widget=forms.TextInput(
                    attrs={
                        'class': 'form-control', 
                        'id': 'home_residence', 
                        'placeholder': 'Home residence' 
                    }
                )
            )
    date_of_employment = forms.DateField(
                # label='Date employed', 
                widget=forms.DateInput(
                    attrs={
                        'class': 'form-control', 
                        'id': 'date_of_employment', 
                        'placeholder': 'Date of Employment'
                    }
                )
            )
    active = forms.BooleanField(
                # label='Is active',
                required=False,
                widget=forms.CheckboxInput(
                    attrs={
                        'id': 'date_of_employment', 
                    }
                )
            )
    
    class Meta: 
        model = Staff 
        fields = '__all__'
