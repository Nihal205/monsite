from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Count
from datetime import date


class Cheval(models.Model):
    nom = models.CharField(max_length=100)
    race = models.CharField(max_length=100)
    age = models.IntegerField()
    disponible = models.BooleanField(default=True)
    seances_travail = models.IntegerField(default=0)

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
    entraineur = models.ForeignKey(Moniteur, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.niveau} - {self.jour} {self.heure_debut.strftime('%H:%M')}"

    class Meta:
        ordering = ['jour', 'heure_debut']


class Participation(models.Model):
    cours = models.ForeignKey(Cours, on_delete=models.CASCADE, related_name="participations")
    cavalier = models.ForeignKey(Cavalier, on_delete=models.CASCADE)
    cheval = models.ForeignKey(Cheval, on_delete=models.CASCADE)

    def clean(self):
        if not self.cours_id:
            return  # Ne pas exécuter les règles si le cours n’est pas encore sauvegardé

        # 1️⃣ Même cheval déjà utilisé dans CE cours
        doublon_cheval = Participation.objects.filter(
            cours=self.cours,
            cheval=self.cheval
        ).exclude(pk=self.pk)
        if doublon_cheval.exists():
            raise ValidationError(f"{self.cheval.nom} est déjà monté dans ce cours par un autre cavalier.")

        # 2️⃣ Même cheval dans un autre cours avec horaires qui se chevauchent
        chevauchement = Participation.objects.filter(
            cheval=self.cheval,
            cours__jour=self.cours.jour,
            cours__heure_debut__lt=self.cours.heure_fin,
            cours__heure_fin__gt=self.cours.heure_debut
        ).exclude(pk=self.pk, cours_id=self.cours.id)
        if chevauchement.exists():
            raise ValidationError(f"{self.cheval.nom} est déjà prévu dans un autre cours à ce créneau.")

        # 3️⃣ Cheval utilisé + de 2 fois dans la journée
        nb_utilisations = Participation.objects.filter(
            cheval=self.cheval,
            cours__jour=self.cours.jour
        ).exclude(pk=self.pk).count()
        if nb_utilisations >= 2:
            raise ValidationError(f"{self.cheval.nom} a déjà été monté 2 fois ce jour-là.")

        # 4️⃣ Cavalier monte + de 2 chevaux dans la même journée
        chevauchements = Participation.objects.filter(
            cavalier=self.cavalier,
            cours__jour=self.cours.jour
        ).exclude(pk=self.pk)
        if chevauchements.count() >= 2:
            raise ValidationError(f"{self.cavalier.prenom} {self.cavalier.nom} monte déjà 2 chevaux ce jour-là.")

        # 5️⃣ Maximum 5 cavaliers par cours
        nb_participants = Participation.objects.filter(
            cours=self.cours
        ).exclude(pk=self.pk).count()
        if nb_participants >= 5:
            raise ValidationError("Ce cours contient déjà 5 cavaliers.")

        # 6️⃣ Cheval < 6 ans → interdit concours, moniteur obligatoire
        if self.cheval.age < 6:
            if self.cours.niveau.lower() == "concours":
                raise ValidationError(f"{self.cheval.nom} a moins de 6 ans et ne peut pas participer à un concours.")
            if not Moniteur.objects.filter(nom=self.cavalier.nom, prenom=self.cavalier.prenom).exists():
                raise ValidationError(f"{self.cheval.nom} a moins de 6 ans et doit être monté par un moniteur.")

        # 7️⃣ Cavalier inscrit à un cours Débutant → pas de concours
        if self.cours.niveau.lower() == "concours":
            debutant = Participation.objects.filter(
                cavalier=self.cavalier,
                cours__niveau__iexact="débutant"
            ).exclude(pk=self.pk)
            if debutant.exists():
                raise ValidationError(
                    f"{self.cavalier.prenom} {self.cavalier.nom} suit un cours Débutant et ne peut pas faire de concours."
                )

        # 8️⃣ Cavalier ne doit pas dépasser 4 cours dans la semaine
        semaine = Participation.objects.filter(
            cavalier=self.cavalier
        ).exclude(pk=self.pk).count()
        if semaine >= 4:
            raise ValidationError(
                f"{self.cavalier.prenom} {self.cavalier.nom} ne peut pas participer à plus de 4 cours par semaine."
            )

    def __str__(self):
        return f"{self.cavalier} monte {self.cheval} dans {self.cours}"


class Inscription(models.Model):
    cavalier = models.ForeignKey(Cavalier, on_delete=models.CASCADE)
    cours = models.ForeignKey(Cours, on_delete=models.CASCADE)
    date_inscription = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.cavalier} inscrit à {self.cours}"

