from django.db import models
from django.urls import reverse
# from inventory.models import Inventory 

from datetime import date 

# Create your models here.
class Sale(models.Model):
    goods_sold = models.CharField(max_length=200, default='', null=False) 
    prices = models.CharField(max_length=200, default='', null=False) 
    quantities = models.CharField(max_length=100, blank=False, null=True) 
    total = models.DecimalField(max_digits=20, decimal_places=2, null=True) 
    customer_name = models.CharField(max_length=200, blank=True, null=True) 
    customer_phone = models.CharField(max_length=15, blank=True, null=True) 
    date = models.DateField(default=date.today) 
    details = models.TextField(blank=True, null=True) 
    
    battery_serials = models.CharField(max_length=400, default='{}') # string of dict mapping battery name to serial numbers
    inverter_serials = models.CharField(max_length=400, default='{}') # string of dict mapping inverter name to serial numbers
    battery_serials_done = models.CharField(max_length=400, default='', blank=True, null=True)
    inverter_serials_done = models.CharField(max_length=300, default='', blank=True, null=True) 

    has_refill_reminder = models.BooleanField(default=False) 

    def get_absolute_url(self):
        return reverse('sale:sale-detail', kwargs={'pk': self.id})

    def __str__(self):
        return str(self.date)

