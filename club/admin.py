from django.contrib import admin
from django.db.models import Count, Case, When, IntegerField
from .models import Cheval, Cavalier, Moniteur, Cours, Participation, Inscription
from datetime import date

# === Admin Cavalier ===
class CavalierAdmin(admin.ModelAdmin):
    list_display = ["prenom", "nom", "email", "nb_cours"]
    search_fields = ["prenom", "nom"]

    def nb_cours(self, obj):
        return obj.nb_cours()
    nb_cours.short_description = "Nombre de cours"


# === Admin Cheval ===
class ChevalAdmin(admin.ModelAdmin):
    list_display = ["nom", "race", "age", "seances_travail", "disponible"]
    search_fields = ["nom"]


# === Inline Participation dans Cours ===
class ParticipationInline(admin.TabularInline):
    model = Participation
    extra = 1
    autocomplete_fields = ["cavalier", "cheval"]

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        today = date.today()
        jour_str = today.strftime('%A').lower()

        if db_field.name == "cheval":
            chevaux_exclus = Participation.objects.filter(
                cours__jour=jour_str
            ).values('cheval').annotate(n=Count('id')).filter(n__gte=2).values_list('cheval', flat=True)
            kwargs["queryset"] = Cheval.objects.exclude(id__in=chevaux_exclus)

        if db_field.name == "cavalier":
            cavaliers_limite = Participation.objects.values('cavalier') \
                .annotate(n=Count('id')) \
                .filter(n__gte=4).values_list('cavalier', flat=True)
            inscrits_ids = Participation.objects.values_list('cavalier', flat=True).distinct()

            kwargs["queryset"] = Cavalier.objects.exclude(id__in=cavaliers_limite).annotate(
                inscrit=Case(
                    When(id__in=inscrits_ids, then=1),
                    default=0,
                    output_field=IntegerField()
                )
            ).order_by('inscrit', 'nom')

        return super().formfield_for_foreignkey(db_field, request, **kwargs)


# === Admin Cours ===
class CoursAdmin(admin.ModelAdmin):
    inlines = [ParticipationInline]
    list_display = ["niveau", "jour", "heure_debut", "heure_fin", "entraineur"]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "entraineur":
            kwargs["queryset"] = Moniteur.objects.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


# === Enregistrement dans admin ===
admin.site.register(Cavalier, CavalierAdmin)
admin.site.register(Cheval, ChevalAdmin)
admin.site.register(Moniteur)
admin.site.register(Cours, CoursAdmin)
admin.site.register(Participation)
admin.site.register(Inscription)
