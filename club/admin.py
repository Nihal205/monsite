from django.contrib import admin
from .models import Cheval, Cavalier, Moniteur, Cours, Participation, Inscription

class CavalierAdmin(admin.ModelAdmin):
    list_display = ["prenom", "nom", "est_inscrit_quelque_part"]
    search_fields = ["prenom", "nom"]

    def est_inscrit_quelque_part(self, obj):
        participations = Participation.objects.filter(cavalier=obj)
        if participations.exists():
            return "✅ Oui"
        return "❌ Non"
    est_inscrit_quelque_part.short_description = "Inscrit à un cours ?"

class ChevalAdmin(admin.ModelAdmin):
    search_fields = ["nom"]

class ParticipationInline(admin.TabularInline):
    model = Participation
    extra = 1
    autocomplete_fields = ["cavalier", "cheval"]

class CoursAdmin(admin.ModelAdmin):
    inlines = [ParticipationInline]
    list_display = ["niveau", "jour", "heure_debut", "heure_fin", "entraineur"]

admin.site.register(Cavalier, CavalierAdmin)
admin.site.register(Cheval, ChevalAdmin)
admin.site.register(Moniteur)
admin.site.register(Cours, CoursAdmin)
admin.site.register(Participation)
admin.site.register(Inscription)

