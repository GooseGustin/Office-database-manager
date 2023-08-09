from django.urls import path 
from .views import (
    # SaleCreateView, 
    SaleDetailView, 
    SaleConfirmDeleteView, 
    SaleListView, 
    saleDelete, 
    saleCreateView, 
    saleDetailView, 
    saleUpdateView
)

app_name = 'sale'
urlpatterns = [
    path('list/', SaleListView.as_view(), name='sale-list'), 
    # path('<int:id>/', SaleDetailView.as_view(), name='sale-detail'),
    path('<int:id>/', saleDetailView, name='sale-detail'), 
    path('<int:id>delete/', saleDelete, name='sale-delete'), 
    path('<int:id>/confirm_delete/', SaleConfirmDeleteView.as_view(), name='sale-confirm-delete'), 
    # path('create/', SaleCreateView.as_view(), name='sale-create'), 
    path('create/', saleCreateView, name='sale-create'), 
    path('<int:id>/update/', saleUpdateView, name='sale-update')
]