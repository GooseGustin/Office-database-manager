from django.urls import reverse 
from django.db import models

# Create your models here.
class Staff(models.Model):
    name = models.CharField(max_length=120)
    state_of_origin = models.CharField(max_length=50)
    phone = models.CharField(max_length=11) 
    email = models.EmailField(max_length=50)
    home_residence = models.CharField(max_length=200)
    date_of_employment = models.DateField(auto_now=False)
    date_of_leave = models.DateField(auto_now=False) 
    active = models.BooleanField(default=False) 

    has_left = models.BooleanField(default=False) 
    is_employed = models.BooleanField(default=False) 

    def get_absolute_url(self):
        return reverse('staff:staff-detail', kwargs={'id': self.id})

    def __str__(self) -> str:
        return self.name 