from django.urls import path 
from django.conf import settings 
from django.conf.urls.static import static 

from .views import (
    jobCreateView, 
    JobDeleteView, 
    JobDetailView, 
    JobListView, 
    JobUpdateView
)

app_name = 'job'
urlpatterns = [
    path('list/', JobListView.as_view(), name='job-list'), 
    path('<int:id>/', JobDetailView.as_view(), name='job-detail'), 
    path('<int:id>/delete/', JobDeleteView.as_view(), name='job-delete'), 
    path('create/', jobCreateView, name='job-create'), 
    path('<int:id>/update/', JobUpdateView.as_view(), name='job-update'),
] +  static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)