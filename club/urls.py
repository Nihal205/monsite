<<<<<<< HEAD

=======
>>>>>>> 36545bc832983f4c6bf3d7723a6a96910bae9619
from django.urls import path
from . import views

urlpatterns = [
<<<<<<< HEAD
    path('', views.accueil, name='accueil'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/statut/', views.statut, name='statut'),
    path('dashboard/inscription/', views.inscription, name='inscription'),
    path('dashboard/concours/', views.concours, name='concours'),
    path('dashboard/chevaux/', views.chevaux, name='chevaux'),
]

=======
    path('inscription/', views.inscription_cavalier, name='inscription_cavalier'),
]
>>>>>>> 36545bc832983f4c6bf3d7723a6a96910bae9619
