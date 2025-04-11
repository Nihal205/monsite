from django import forms
from .models import Cours, Moniteur

class CoursForm(forms.ModelForm):
    entraineur = forms.ModelChoiceField(
        queryset=Moniteur.objects.all(),
        label="Entraîneur",
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ce qui s'affiche dans la liste déroulante
        self.fields['entraineur'].label_from_instance = lambda obj: f"{obj.prenom} {obj.nom} ({obj.specialite})"

    class Meta:
        model = Cours
        fields = "__all__"
