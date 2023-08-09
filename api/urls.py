from django.urls import path 
from .views import (
    StaffListCreateAPIView, 
    StaffDetailAPIView, 
    StaffDestroyAPIView, 
    InventoryListCreateAPIView, 
    InventoryDetailAPIView, 
    InventoryDestroyAPIView, 
    SaleListCreateAPIView, 
    SaleDetailAPIView, 
    SaleDestroyAPIView, 
    JobListCreateAPIView, 
    JobDetailAPIView, 
    JobDestroyAPIView, 
    InventoryTypeListCreateAPIView, 
    InventoryTypeDetailAPIView, 
    InventoryTypeDestroyAPIView
)

app_name = 'api'
urlpatterns = [
    path('staff_list/', StaffListCreateAPIView.as_view()), 
    path('staff_detail/<int:pk>/', StaffDetailAPIView.as_view()), 
    path('staff_delete/<int:pk>/', StaffDestroyAPIView.as_view()), 

    path('inventory_list/', InventoryListCreateAPIView.as_view()), 
    path('inventory_detail/<int:pk>/', InventoryDetailAPIView.as_view()), 
    path('inventory_delete/<int:pk>/', InventoryDestroyAPIView.as_view()), 

    path('sale_list/', SaleListCreateAPIView.as_view()), 
    path('sale_detail/<int:pk>/', SaleDetailAPIView.as_view()), 
    path('sale_delete/<int:pk>/', SaleDestroyAPIView.as_view()), 
    
    path('job_list/', JobListCreateAPIView.as_view()), 
    path('job_detail/<int:pk>/', JobDetailAPIView.as_view()), 
    path('job_delete/<int:pk>/', JobDestroyAPIView.as_view()), 

    path('inv_type_list/', InventoryTypeListCreateAPIView.as_view()), 
    path('inv_type_detail/<int:pk>/', InventoryTypeDetailAPIView.as_view()), 
    path('inv_type_delete/<int:pk>/', InventoryTypeDestroyAPIView.as_view()), 

]