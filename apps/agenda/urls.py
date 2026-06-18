from django.urls import path
from . import views
app_name = 'agenda'
urlpatterns = [
    path('annoncer/', views.soumettre_evenement, name='soumettre_evenement'),
]
