from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NoteViewSet,CollaboratorView,LabelsAddRemove

router = DefaultRouter()
router.register(r'notes', NoteViewSet ,basename="note")
router.register(r'collabs', CollaboratorView ,basename="collab")
router.register(r'labels', LabelsAddRemove ,basename="labels")


urlpatterns = [
    path('', include(router.urls)),
    # path('collab/', include(router.urls)),
    
]
