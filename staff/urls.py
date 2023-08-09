from django.urls import path 
from django.conf import settings 
from django.conf.urls.static import static 
from .views import (
    staffCreateView, 
    StaffDeleteView, 
    StaffDetailView, 
    StaffListView, 
    StaffUpdateView,
    staffListView, 
)

app_name = 'staff'
urlpatterns = [
    path('list/', StaffListView.as_view(), name='staff-list'), 
    path('<int:pk>/', StaffDetailView.as_view(), name='staff-detail'), 
    # path('create/', StaffCreateView.as_view(), name='staff-create'), 
    path('create/', staffCreateView, name='staff-create'), 
    path('<int:pk>/update/', StaffUpdateView.as_view(), name='staff-update'), 
    path('<int:pk>/delete/', StaffDeleteView.as_view(), name='staff-delete')

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)