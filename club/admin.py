from django.contrib import admin
from .models import Cheval, Cavalier, Moniteur, Cours, Participation, Inscription
from .forms import CoursForm
from django.db.models import Count, Case, When, IntegerField
from datetime import date

# === Admin Cavalier ===
class CavalierAdmin(admin.ModelAdmin):
    list_display = ["prenom", "nom", "est_inscrit_quelque_part"]
    search_fields = ["prenom", "nom"]

    def est_inscrit_quelque_part(self, obj):
        participations = Participation.objects.filter(cavalier=obj)
        return "✅ Oui" if participations.exists() else "❌ Non"
    est_inscrit_quelque_part.short_description = "Inscrit à un cours ?"

# === Admin Cheval ===
class ChevalAdmin(admin.ModelAdmin):
    search_fields = ["nom"]

# === Inline Participation personnalisé ===
class ParticipationInline(admin.TabularInline):
    model = Participation
    extra = 1
    autocomplete_fields = ["cavalier", "cheval"]

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        today = date.today()
        jour_str = today.strftime('%A').lower()

        if db_field.name == "cheval":
            # 🐴 Chevaux montés 2x max dans la journée
            chevaux_exclus_jour = Participation.objects.filter(
                cours__jour=jour_str
            ).values('cheval').annotate(n=Count('id')).filter(n__gte=2).values_list('cheval', flat=True)

            # 🐴 Chevaux déjà utilisés dans ce cours
            cours_id = request.resolver_match.kwargs.get('object_id')
            chevaux_deja_utilises = []
            if cours_id:
                chevaux_deja_utilises = Participation.objects.filter(
                    cours__id=cours_id
                ).values_list('cheval', flat=True)

            kwargs["queryset"] = Cheval.objects.exclude(
                id__in=list(chevaux_exclus_jour) + list(chevaux_deja_utilises)
            )

        if db_field.name == "cavalier":
            # 🧍 Cavaliers ayant dépassé 4 cours dans la semaine
            cavaliers_limite = Participation.objects.values('cavalier') \
                .annotate(n=Count('id')) \
                .filter(n__gte=4).values_list('cavalier', flat=True)

            # 🧍 Cavaliers déjà inscrits à au moins un cours
            inscrits_ids = Participation.objects.values_list('cavalier', flat=True).distinct()

            kwargs["queryset"] = Cavalier.objects.exclude(id__in=cavaliers_limite).annotate(
                inscrit=Case(
                    When(id__in=inscrits_ids, then=1),
                    default=0,
                    output_field=IntegerField()
                )
            ).order_by('inscrit', 'nom')

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

# === Admin Cours personnalisé ===
class CoursAdmin(admin.ModelAdmin):
    form = CoursForm
    inlines = [ParticipationInline]
    list_display = ["niveau", "jour", "heure_debut", "heure_fin", "entraineur"]

# === Enregistrement dans l’admin ===
admin.site.register(Cavalier, CavalierAdmin)
admin.site.register(Cheval, ChevalAdmin)
admin.site.register(Moniteur)
admin.site.register(Cours, CoursAdmin)
admin.site.register(Participation)
admin.site.register(Inscription)
