from django.contrib import admin
from .models import Cheval, Cavalier, Moniteur, Cours, Inscription

admin.site.register(Cheval)
admin.site.register(Cavalier)
admin.site.register(Moniteur)
admin.site.register(Cours)
admin.site.register(Inscription)
