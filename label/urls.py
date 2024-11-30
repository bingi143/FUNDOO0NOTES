from .views import LabelView , LabelViewMainu ,RawQueryView,RawQueryViewMain
# from rest_framework.routers import DefaultRouter
from django.urls import path, include

urlpatterns = [
    path('label/', LabelView.as_view(), name='label'),
    path('label/<int:pk>/',LabelViewMainu.as_view(), name='label_main'),
    path('rawquery/', RawQueryView.as_view(), name='rawquery'),
    path('rawquery/<int:pk>/', RawQueryViewMain.as_view(), name='rawquery-main'),
    
    
    
]



