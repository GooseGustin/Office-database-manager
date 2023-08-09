from django.db import models
from django.utils.timezone import now 

from sale.models import Sale 
from job.models import Job

from datetime import datetime as dt

thisDay = dt.today

class RefillReminder(models.Model):
    # For every sale or job 
    job = models.ForeignKey(Job, on_delete=models.CASCADE, blank=True, null=True) 
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, blank=True, null=True) 
    alert = models.BooleanField(default=False) 
    last_refill_date = models.DateField(default=thisDay)
    months_passed = models.IntegerField(default=0) 
    forget = models.BooleanField(default=False) 

    def __str__(self):
        return 'RefillReminder' + str(self.id) + ' ' + str(self.last_refill_date)

class WarrantyReminder(models.Model):
    # For every battery or inverter
    serial_no = models.CharField(max_length=20, default='')  # string of dict mapping battery name to serial numbers
    product = models.CharField(max_length=100, default='')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, blank=True, null=True) 
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, blank=True, null=True) 
    alert = models.BooleanField(default=False) 
    months_passed = models.IntegerField(default=0) 
    is_sale = models.BooleanField(default=True) 
    forget = models.BooleanField(default=False) 

class MaintenanceReminder(models.Model):
    # For every job
    job = models.ForeignKey(Job, on_delete=models.CASCADE, blank=True, null=True) 
    alert = models.BooleanField(default=False) 
    last_maintenance_date = models.DateField(default=thisDay) 
    months_passed = models.IntegerField(default=0) 
    forget = models.BooleanField(default=False)

    def __str__(self):
        return 'MaintenanceReminder' + str(self.id) + ' ' + str(self.last_maintenance_date)
