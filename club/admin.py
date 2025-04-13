from django.contrib import admin, messages
from django.db.models import Count, Case, When, IntegerField
from django.urls import path
from django.template.response import TemplateResponse
from datetime import date
from .models import Cheval, Cavalier, Moniteur, Cours, Participation, Inscription

# === Admin Cavalier ===
class CavalierAdmin(admin.ModelAdmin):
    list_display = ["prenom", "nom", "est_inscrit_quelque_part"]
    search_fields = ["prenom", "nom"]

    # Vérifie si le cavalier est inscrit à un cours
    def est_inscrit_quelque_part(self, obj):
        participations = Participation.objects.filter(cavalier=obj)
        return "✅ Oui" if participations.exists() else "❌ Non"
    est_inscrit_quelque_part.short_description = "Inscrit à un cours ?"

# === Admin Cheval ===
class ChevalAdmin(admin.ModelAdmin):
    search_fields = ["nom"]

# === Inline des participations dans le formulaire Cours ===
class ParticipationInline(admin.TabularInline):
    model = Participation
    extra = 1
    autocomplete_fields = ["cavalier", "cheval"]

    # Personnalise les listes déroulantes pour filtrer les cavaliers et chevaux
    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        today = date.today()
        jour_str = today.strftime('%A').lower()

        # 🐴 Empêche de sélectionner les chevaux déjà montés 2 fois aujourd'hui
        if db_field.name == "cheval":
            chevaux_exclus_jour = Participation.objects.filter(
                cours__jour=jour_str
            ).values('cheval').annotate(n=Count('id')).filter(n__gte=2).values_list('cheval', flat=True)

            # 🐴 Empêche aussi de prendre le même cheval 2 fois dans le même cours
            cours_id = request.resolver_match.kwargs.get('object_id')
            chevaux_deja_utilises = []
            if cours_id:
                chevaux_deja_utilises = Participation.objects.filter(
                    cours__id=cours_id
                ).values_list('cheval', flat=True)

            kwargs["queryset"] = Cheval.objects.exclude(
                id__in=list(chevaux_exclus_jour) + list(chevaux_deja_utilises)
            )

        # �� Trie les cavaliers :
        #  - exclut ceux ayant dépassé 4 cours
        #  - affiche les non inscrits d'abord
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

# === Admin personnalisé pour les Cours ===
class CoursAdmin(admin.ModelAdmin):
    inlines = [ParticipationInline]
    list_display = ["niveau", "jour", "heure_debut", "heure_fin", "entraineur"]

    # Affiche la spécialité des moniteurs dans le menu déroulant
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "entraineur":
            kwargs["queryset"] = Moniteur.objects.all()
            return db_field.formfield(**kwargs)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    # Message de succès lors de la sauvegarde d’un cours
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        messages.success(request, f"✅ Le cours '{obj}' a été enregistré avec succès.")

# === Admin personnalisé avec une page de rapport ===
class CustomAdminSite(admin.AdminSite):
    site_header = "Administration Centre Équestre"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("club/rapport/", self.admin_view(self.rapport_view), name="club-rapport"),
        ]
        return custom_urls + urls

    # Page de rapport personnalisé pour voir tous les cours
    def rapport_view(self, request):
        cours = Cours.objects.prefetch_related("participations__cavalier", "participations__cheval", "entraineur")
        context = dict(
            self.each_context(request),
            cours=cours
        )
        return TemplateResponse(request, "admin/club/rapport.html", context)

# === Enregistrement des modèles dans Django Admin ===

# Interface personnalisée
admin_site = CustomAdminSite(name='customadmin')
admin_site.register(Cavalier, CavalierAdmin)
admin_site.register(Cheval, ChevalAdmin)
admin_site.register(Moniteur)
admin_site.register(Cours, CoursAdmin)
admin_site.register(Participation)
admin_site.register(Inscription)

# Interface classique (si tu accèdes à /admin/)
admin.site.register(Cavalier, CavalierAdmin)
admin.site.register(Cheval, ChevalAdmin)
admin.site.register(Moniteur)
admin.site.register(Cours, CoursAdmin)
admin.site.register(Participation)
admin.site.register(Inscription)

