
from django.urls import path
from . import views

urlpatterns = [
    path('', views.accueil, name='accueil'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/statut/', views.statut, name='statut'),
    path('dashboard/inscription/', views.inscription, name='inscription'),
    path('dashboard/concours/', views.concours, name='concours'),
    path('dashboard/chevaux/', views.chevaux, name='chevaux'),
]

