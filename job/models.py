from django.db import models
from staff.models import Staff 
from inventory.models import Inventory 

# Create your models here.
class Job(models.Model):
    status_options = [
        ('Completed', 'completed'), 
        ('Incompleted', 'incompleted'), 
        ('Cancelled', 'cancelled'), 
        ('Postponed', 'postponed')
    ]
    staff_assigned = models.CharField(max_length=300, blank=False, null=False, default='')
    date = models.DateField(auto_now=False, default=None) 
    location = models.CharField(max_length=200, blank=False, null=False) 
    inventory_used = models.CharField(max_length=300, blank=True) 
    prices = models.CharField(max_length=200, blank=True)
    quantities = models.CharField(max_length=100, blank=True)
    battery_serials = models.CharField(max_length=400, default='{}', blank=True, null=True)
    inverter_serials = models.CharField(max_length=300, default='{}', blank=True, null=True) 
    other_items = models.CharField(max_length=500, blank=True, null=True) 
    other_items_expenses = models.CharField(max_length=500, blank=True, null=True) 
    transportation_cost = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    total_expenses = models.DecimalField(max_digits=20, decimal_places=2, default=0.00) 
    job_status = models.CharField(choices=status_options, max_length=20, default='Completed')
    job_description = models.TextField(blank=True, null=True) 
    customer_charge = models.DecimalField(max_digits=20, decimal_places=2, default=0.00) 
    customer_name = models.CharField(max_length=50, blank=True) 
    customer_phone = models.CharField(max_length=20, blank=True) 
    remark = models.TextField(blank=True, null=True) 

    has_refill_reminder = models.BooleanField(default=False) 
    has_maintenance_reminder = models.BooleanField(default=False) 
    battery_serials_done = models.CharField(max_length=400, default='', blank=True, null=True)
    inverter_serials_done = models.CharField(max_length=300, default='', blank=True, null=True) 

    def __str__(self):
        return str(self.date) 
