from django.shortcuts import render
from rest_framework.generics import (
    ListCreateAPIView, 
    RetrieveAPIView, 
    DestroyAPIView, 
    UpdateAPIView
)

from staff.models import Staff 
from inventory.models import Inventory, InventoryType
from sale.models import Sale 
from job.models import Job 

from .serializers import (
    StaffSerializer,     
    InventorySerializer, 
    InventoryTypeSerializer, 
    JobSerializer, 
    SaleSerializer, 
)

class StaffListCreateAPIView(ListCreateAPIView):
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer

class StaffDetailAPIView(RetrieveAPIView):
    queryset = Staff.objects.all() 
    serializer_class = StaffSerializer 
    lookup_field = 'pk' 

class StaffUpdateAPIView(UpdateAPIView):
    queryset = Staff.objects.all() 
    serializer_class = StaffSerializer 
    lookup_field = 'pk' 

class StaffDestroyAPIView(DestroyAPIView):
    pass 

class InventoryListCreateAPIView(ListCreateAPIView):
    queryset = Inventory.objects.all() 
    serializer_class = InventorySerializer 

class InventoryDetailAPIView(RetrieveAPIView):
    queryset = Inventory.objects.all() 
    serializer_class = InventorySerializer
    lookup_field = 'pk'
    
class InventoryDestroyAPIView(DestroyAPIView):
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer
    lookup_field = 'pk'

class SaleListCreateAPIView(ListCreateAPIView):
    queryset = Sale.objects.all() 
    serializer_class = SaleSerializer 

class SaleDetailAPIView(RetrieveAPIView):
    queryset = Sale.objects.all() 
    serializer_class = SaleSerializer
    lookup_field = 'pk'
    
class SaleDestroyAPIView(DestroyAPIView):
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer
    lookup_field = 'pk'


class JobListCreateAPIView(ListCreateAPIView):
    queryset = Job.objects.all() 
    serializer_class = JobSerializer 

class JobDetailAPIView(RetrieveAPIView):
    queryset = Job.objects.all() 
    serializer_class = JobSerializer
    lookup_field = 'pk'
    
class JobDestroyAPIView(DestroyAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    lookup_field = 'pk'

class InventoryTypeListCreateAPIView(ListCreateAPIView):
    queryset = InventoryType.objects.all() 
    serializer_class = InventoryTypeSerializer 

class InventoryTypeDetailAPIView(RetrieveAPIView):
    queryset = InventoryType.objects.all() 
    serializer_class = InventoryTypeSerializer
    lookup_field = 'pk'
    
class InventoryTypeDestroyAPIView(DestroyAPIView):
    queryset = InventoryType.objects.all()
    serializer_class = InventoryTypeSerializer
    lookup_field = 'pk'

