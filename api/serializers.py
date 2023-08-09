from rest_framework import serializers 
from staff.models import Staff 
from inventory.models import Inventory, InventoryType
from sale.models import Sale
from job.models import Job 

class StaffSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Staff 
        fields = '__all__'


class InventorySerializer(serializers.ModelSerializer):
    class Meta: 
        model = Inventory
        fields = '__all__' 

class InventoryTypeSerializer(serializers.ModelSerializer):
    class Meta: 
        model = InventoryType
        fields = '__all__' 
        
class SaleSerializer(serializers.ModelSerializer): 
    class Meta: 
        model = Sale
        fields = '__all__' 

class JobSerializer(serializers.ModelSerializer): 
    class Meta: 
        model = Job
        fields = '__all__' 