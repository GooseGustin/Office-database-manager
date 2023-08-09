from django.contrib import admin
from .models import RefillReminder, WarrantyReminder, MaintenanceReminder

# Register your models here.
admin.site.register(RefillReminder)
admin.site.register(WarrantyReminder) 
admin.site.register(MaintenanceReminder)