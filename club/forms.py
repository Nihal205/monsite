from django import forms
from .models import Cours, Moniteur

class CoursForm(forms.ModelForm):
    class Meta:
        model = Cours
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ✅ C'est ici qu'on personnalise l'affichage de l'entraineur
        self.fields['entraineur'].label_from_instance = lambda obj: f"{obj.prenom} {obj.nom} ({obj.specialite})"
