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

    def est_inscrit_quelque_part(self, obj):
        participations = Participation.objects.filter(cavalier=obj)
        return "✅ Oui" if participations.exists() else "❌ Non"
    est_inscrit_quelque_part.short_description = "Inscrit à un cours ?"

# === Admin Cheval ===
class ChevalAdmin(admin.ModelAdmin):
    search_fields = ["nom"]

# === Inline pour les participations ===
class ParticipationInline(admin.TabularInline):
    model = Participation
    extra = 0  # ✅ Plus de ligne vide automatiquement
    autocomplete_fields = ["cavalier", "cheval"]
    can_delete = True
    min_num = 0
    validate_min = False
    validate_max = True

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        today = date.today()
        jour_str = today.strftime('%A').lower()

        if db_field.name == "cheval":
            chevaux_exclus_jour = Participation.objects.filter(
                cours__jour=jour_str
            ).values('cheval').annotate(n=Count('id')).filter(n__gte=2).values_list('cheval', flat=True)

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

# === Admin Cours personnalisé ===
class CoursAdmin(admin.ModelAdmin):
    inlines = [ParticipationInline]
    list_display = ["niveau", "jour", "heure_debut", "heure_fin", "entraineur"]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "entraineur":
            kwargs["queryset"] = Moniteur.objects.all()
            return db_field.formfield(**kwargs)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        messages.success(request, f"✅ Le cours '{obj}' a été enregistré avec succès.")

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if hasattr(instance, "is_empty") and instance.is_empty():
                continue
            instance.full_clean()
            instance.save()
        formset.save_m2m()

# === Ajout d'une méthode pour ignorer les lignes vides ===
def participation_is_empty(self):
    return not self.cavalier_id and not self.cheval_id
Participation.is_empty = participation_is_empty

# === Admin personnalisé avec page de rapport (optionnel) ===
class CustomAdminSite(admin.AdminSite):
    site_header = "Administration Centre Équestre"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("club/rapport/", self.admin_view(self.rapport_view), name="club-rapport"),
        ]
        return custom_urls + urls

    def rapport_view(self, request):
        cours = Cours.objects.prefetch_related("participations__cavalier", "participations__cheval", "entraineur")
        context = dict(
            self.each_context(request),
            cours=cours
        )
        return TemplateResponse(request, "admin/club/rapport.html", context)

# === Enregistrement dans admin Django ===
admin.site.register(Cavalier, CavalierAdmin)
admin.site.register(Cheval, ChevalAdmin)
admin.site.register(Moniteur)
admin.site.register(Cours, CoursAdmin)
admin.site.register(Participation)
admin.site.register(Inscription)
