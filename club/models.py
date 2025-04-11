from django.db import models 
from django.core.exceptions import ValidationError



class Cheval(models.Model):
    nom = models.CharField(max_length=100)
    race = models.CharField(max_length=100)
    age = models.IntegerField()
    disponible = models.BooleanField(default=True)
    seances_travail = models.IntegerField(default=0)  # ← nombre de séances

    def __str__(self):
        return self.nom


class Cavalier(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    age = models.IntegerField()
    email = models.EmailField()
    cheval_possede = models.ForeignKey(Cheval, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.prenom} {self.nom}"


class Moniteur(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.EmailField()
    specialite = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.prenom} {self.nom}"

class Cours(models.Model):
    JOUR_CHOICES = [
        ('lundi', 'Lundi'),
        ('mardi', 'Mardi'),
        ('mercredi', 'Mercredi'),
        ('jeudi', 'Jeudi'),
        ('vendredi', 'Vendredi'),
        ('samedi', 'Samedi'),
    ]

    niveau = models.CharField(max_length=100)
    jour = models.CharField(max_length=10, choices=JOUR_CHOICES)
    heure_debut = models.TimeField()
    heure_fin = models.TimeField()
    entraineur = models.ForeignKey("Moniteur", on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.niveau} - {self.jour} {self.heure_debut.strftime('%H:%M')}"

    class Meta:
        ordering = ['jour', 'heure_debut']


class Participation(models.Model):
    cours = models.ForeignKey(Cours, on_delete=models.CASCADE, related_name="participations")
    cavalier = models.ForeignKey("Cavalier", on_delete=models.CASCADE)
    cheval = models.ForeignKey("Cheval", on_delete=models.CASCADE)

    def clean(self):
        # 1. Le cheval ne peut pas être dans plusieurs cours en même temps
        conflits_cheval = Participation.objects.filter(
            cheval=self.cheval,
            cours__jour=self.cours.jour,
            cours__heure_debut__lt=self.cours.heure_fin,
            cours__heure_fin__gt=self.cours.heure_debut
        ).exclude(pk=self.pk)
        if conflits_cheval.exists():
            raise ValidationError("Ce cheval est déjà utilisé dans un autre cours à ce créneau.")

        # 2. Le cavalier ne peut pas monter plus de 2 chevaux dans la même journée
        chevauchements = Participation.objects.filter(
            cavalier=self.cavalier,
            cours__jour=self.cours.jour
        ).exclude(pk=self.pk)
        if chevauchements.count() >= 2:
            raise ValidationError("Ce cavalier monte déjà 2 chevaux ce jour-là.")

        # 3. Maximum 5 cavaliers par cours
        nb_participants = Participation.objects.filter(cours=self.cours).exclude(pk=self.pk).count()
        if nb_participants >= 5:
            raise ValidationError("Ce cours contient déjà 5 cavaliers.")
# 4. Cavalier inscrit à un cours Débutant ne peut pas faire de Concours
        if self.cours.niveau.lower() == "concours":
            cours_debutant = Participation.objects.filter(
                cavalier=self.cavalier,
                cours__niveau__iexact="Débutant"
            ).exclude(pk=self.pk)
            if cours_debutant.exists():
                raise ValidationError("Ce cavalier est inscrit à un cours Débutant et ne peut pas participer à un Concours.")

        # 5. Cheval de moins de 6 ans → pas de concours et seulement moniteurs
        if self.cheval.age < 6:
                if self.cours.niveau.lower() == "concours":
                    raise ValidationError("Ce cheval a moins de 6 ans et ne peut pas participer à un concours.")
                # Le cheval < 6 ans ne peut être monté que par un moniteur
                if not Moniteur.objects.filter(
                    prenom=self.cavalier.prenom,
                    nom=self.cavalier.nom
                ).exists():
                    raise ValidationError("Ce cheval a moins de 6 ans et ne peut être monté que par un moniteur.")

    def __str__(self):
        return f"{self.cavalier} monte {self.cheval} dans {self.cours}"

class Inscription(models.Model):
    cavalier = models.ForeignKey(Cavalier, on_delete=models.CASCADE)
    cours = models.ForeignKey(Cours, on_delete=models.CASCADE)
    date_inscription = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.cavalier} inscrit à {self.cours}"
