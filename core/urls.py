from django.urls import path 
from django.conf import settings 
from django.conf.urls.static import static 
from .views import (
    homeView,
    reportView, 
    filterView, 
    reminderCreateView, 
    reminderHandleView, 
    helpView, 
)

app_name = 'core'
urlpatterns = [
    path('', homeView, name='home'), 
    path('report/', reportView, name='report'), 
    path('filter/', filterView, name='filter'), 
    path('reminders/', reminderCreateView, name='reminder'), 
    path('reminder-handle/', reminderHandleView, name='reminder-handle'), 
    path('help/', helpView, name='help'), 
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)