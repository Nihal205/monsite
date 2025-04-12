from django.contrib import admin
from .models import Cheval, Cavalier, Moniteur, Cours, Participation, Inscription
from django.db.models import Count, Case, When, IntegerField
from datetime import date

# ========== ADMIN CAVALIER ==========
class CavalierAdmin(admin.ModelAdmin):
    list_display = ["prenom", "nom", "est_inscrit_quelque_part"]
    search_fields = ["prenom", "nom"]

    def est_inscrit_quelque_part(self, obj):
        participations = Participation.objects.filter(cavalier=obj)
        return "✅ Oui" if participations.exists() else "❌ Non"
    est_inscrit_quelque_part.short_description = "Inscrit à un cours ?"

# ========== ADMIN CHEVAL ==========
class ChevalAdmin(admin.ModelAdmin):
    search_fields = ["nom"]

# ========== INLINE PARTICIPATION ==========
class ParticipationInline(admin.TabularInline):
    model = Participation
    extra = 1
    autocomplete_fields = ["cavalier", "cheval"]

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        today = date.today()
        jour_str = today.strftime('%A').lower()

        # === Restrictions cheval ===
        if db_field.name == "cheval":
            # 🐴 Chevaux déjà montés 2 fois aujourd’hui
            chevaux_jour = Participation.objects.filter(
                cours__jour=jour_str
            ).values('cheval').annotate(n=Count('id')).filter(n__gte=2).values_list('cheval', flat=True)

            # 🐴 Chevaux déjà utilisés dans ce cours (pas 2 cavaliers sur même cheval)
            cours_id = request.resolver_match.kwargs.get('object_id')
            deja_utilises = Participation.objects.filter(
                cours_id=cours_id
            ).values_list('cheval', flat=True) if cours_id else []

            kwargs["queryset"] = Cheval.objects.exclude(id__in=list(chevaux_jour) + list(deja_utilises))

        # === Restrictions cavalier ===
        if db_field.name == "cavalier":
            cavaliers_limite = Participation.objects.values('cavalier') \
                .annotate(n=Count('id')) \
                .filter(n__gte=4).values_list('cavalier', flat=True)

            inscrits = Participation.objects.values_list('cavalier', flat=True).distinct()

            kwargs["queryset"] = Cavalier.objects.exclude(id__in=cavaliers_limite).annotate(
                inscrit=Case(
                    When(id__in=inscrits, then=1),
                    default=0,
                    output_field=IntegerField()
                )
            ).order_by('inscrit', 'nom')

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

# ========== ADMIN COURS ==========
class CoursAdmin(admin.ModelAdmin):
    inlines = [ParticipationInline]
    list_display = ["niveau", "jour", "heure_debut", "heure_fin", "entraineur"]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Affichage spécialité dans choix de moniteur
        if db_field.name == "entraineur":
            kwargs["queryset"] = Moniteur.objects.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

# ========== ENREGISTREMENT ==========
admin.site.register(Cavalier, CavalierAdmin)
admin.site.register(Cheval, ChevalAdmin)
admin.site.register(Moniteur)
admin.site.register(Cours, CoursAdmin)
admin.site.register(Participation)
admin.site.register(Inscription)
