from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

# === CHEVAL ===
class Cheval(models.Model):
    nom = models.CharField(max_length=100)
    race = models.CharField(max_length=100)
    age = models.IntegerField()
    disponible = models.BooleanField(default=True)
    seances_travail = models.IntegerField(default=0)
    test_champ = models.BooleanField(default=False)  # Champ temporaire

    def __str__(self):
        return self.nom


# === CAVALIER ===
class Cavalier(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    age = models.IntegerField()
    email = models.EmailField()
    cheval_possede = models.ForeignKey(Cheval, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.prenom} {self.nom}"


# === MONITEUR ===
class Moniteur(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.EmailField()
    specialite = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.prenom} {self.nom} ({self.specialite})"


# === COURS ===
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


# === PARTICIPATION ===
class Participation(models.Model):
    cours = models.ForeignKey(Cours, on_delete=models.CASCADE, related_name="participations")
    cavalier = models.ForeignKey(Cavalier, on_delete=models.CASCADE)
    cheval = models.ForeignKey(Cheval, on_delete=models.CASCADE)

    def clean(self):
        # ⚠️ Si un champ est vide, ne pas continuer la validation
        if not self.cheval or not self.cours or not self.cavalier:
            return

        # 1️⃣ Le même cheval ne peut pas être monté plusieurs fois dans un même cours
        conflits_cheval = Participation.objects.filter(
            cheval=self.cheval,
            cours=self.cours
        ).exclude(pk=self.pk)
        if conflits_cheval.exists():
            raise ValidationError(f"🐴 {self.cheval.nom} est déjà monté pendant ce créneau.")

        # 2️⃣ Cheval ne peut pas être monté + de 2 fois dans la journée
        count_today = Participation.objects.filter(
            cheval=self.cheval,
            cours__jour=self.cours.jour
        ).exclude(pk=self.pk).count()
        if count_today >= 2:
            raise ValidationError(f"🐴 {self.cheval.nom} est déjà monté 2 fois ce jour-là.")

        # 3️⃣ Le cavalier ne peut pas faire plus de 4 cours par semaine
        semaine = Participation.objects.filter(
            cavalier=self.cavalier
        ).exclude(pk=self.pk).count()
        if semaine >= 4:
            raise ValidationError(f"🧍 {self.cavalier.prenom} {self.cavalier.nom} a déjà atteint 4 cours cette semaine.")

        # 4️⃣ Cavalier inscrit à "Débutant" ne peut pas participer à un cours "Concours"
        if self.cours.niveau.lower() == "concours":
            debutant = Participation.objects.filter(
                cavalier=self.cavalier,
                cours__niveau__iexact="débutant"
            ).exclude(pk=self.pk)
            if debutant.exists():
                raise ValidationError("❌ Ce cavalier suit un cours Débutant et ne peut pas participer à un Concours.")

        # 5️⃣ Cheval < 6 ans → pas concours & monté seulement par un moniteur
        if self.cheval.age < 6:
            if self.cours.niveau.lower() == "concours":
                raise ValidationError(f"🚫 {self.cheval.nom} a moins de 6 ans et ne peut pas faire de concours.")
            if not Moniteur.objects.filter(nom=self.cavalier.nom, prenom=self.cavalier.prenom).exists():
                raise ValidationError(f"🚫 {self.cheval.nom} a moins de 6 ans et ne peut être monté que par un moniteur.")

    def __str__(self):
        return f"{self.cavalier} monte {self.cheval} dans {self.cours}"


# === INSCRIPTION ===
class Inscription(models.Model):
    cavalier = models.ForeignKey(Cavalier, on_delete=models.CASCADE)
    cours = models.ForeignKey(Cours, on_delete=models.CASCADE)
    date_inscription = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.cavalier} inscrit à {self.cours}"


# === PARTICIPATION ===
class Participation(models.Model):
    cours = models.ForeignKey(Cours, on_delete=models.CASCADE, related_name="participations")
    cavalier = models.ForeignKey(Cavalier, on_delete=models.CASCADE)
    cheval = models.ForeignKey(Cheval, on_delete=models.CASCADE)

    def clean(self):
        # 1️⃣ Le même cheval ne peut pas être monté plusieurs fois dans un même cours
        conflits_cheval = Participation.objects.filter(
            cheval=self.cheval,
            cours=self.cours
        ).exclude(pk=self.pk)
        if conflits_cheval.exists():
            raise ValidationError(f"{self.cheval.nom} est déjà monté pendant ce créneau.")

        # 2️⃣ Cheval ne peut pas être monté + de 2 fois dans la journée
        count_today = Participation.objects.filter(
            cheval=self.cheval,
            cours__jour=self.cours.jour
        ).exclude(pk=self.pk).count()
        if count_today >= 2:
            raise ValidationError(f"{self.cheval.nom} est déjà monté 2 fois ce jour-là.")

        # 3️⃣ Le cavalier ne peut pas faire plus de 4 cours par semaine
        semaine = Participation.objects.filter(
            cavalier=self.cavalier
        ).exclude(pk=self.pk).count()
        if semaine >= 4:
            raise ValidationError(f"{self.cavalier.prenom} {self.cavalier.nom} a déjà atteint 4 cours cette semaine.")

        # 4️⃣ Cavalier inscrit à "Débutant" ne peut pas participer à un cours "Concours"
        if self.cours.niveau.lower() == "concours":
            debutant = Participation.objects.filter(
                cavalier=self.cavalier,
                cours__niveau__iexact="débutant"
            ).exclude(pk=self.pk)
            if debutant.exists():
                raise ValidationError("Ce cavalier suit un cours Débutant et ne peut pas participer à un Concours.")

        # 5️⃣ Cheval < 6 ans → pas concours & monté seulement par un moniteur
        if self.cheval.age < 6:
            if self.cours.niveau.lower() == "concours":
                raise ValidationError(f"{self.cheval.nom} a moins de 6 ans et ne peut pas faire de concours.")
            if not Moniteur.objects.filter(nom=self.cavalier.nom, prenom=self.cavalier.prenom).exists():
                raise ValidationError(f"{self.cheval.nom} a moins de 6 ans et ne peut être monté que par un moniteur.")

    def __str__(self):
        return f"{self.cavalier} monte {self.cheval} dans {self.cours}"


# === INSCRIPTION ===
class Inscription(models.Model):
    cavalier = models.ForeignKey(Cavalier, on_delete=models.CASCADE)
    cours = models.ForeignKey(Cours, on_delete=models.CASCADE)
    date_inscription = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.cavalier} inscrit à {self.cours}"

