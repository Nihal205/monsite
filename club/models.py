from django.db import models
from django.core.exceptions import ValidationError

# === CHEVAL ===
class Cheval(models.Model):
    nom = models.CharField(max_length=100)
    race = models.CharField(max_length=100)
    age = models.IntegerField()
    disponible = models.BooleanField(default=True)
    seances_travail = models.IntegerField(default=0)

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

    def is_empty(self):
        """Ignore les lignes vides dans le formulaire admin"""
        return not self.cavalier_id and not self.cheval_id

    def clean(self):
        # 1️⃣ Cheval déjà dans le même cours ?
        conflit_cours = Participation.objects.filter(
            cheval=self.cheval,
            cours=self.cours
        ).exclude(pk=self.pk)
        if conflit_cours.exists():
            raise ValidationError(f"{self.cheval.nom} est déjà monté pendant ce créneau.")

        # 2️⃣ Cheval utilisé plus de 2 fois le même jour ?
        total_jour = Participation.objects.filter(
            cheval=self.cheval,
            cours__jour=self.cours.jour
        ).exclude(pk=self.pk).count()
        if total_jour >= 2:
            raise ValidationError(f"{self.cheval.nom} est déjà monté 2 fois ce jour-là.")

        # 3️⃣ Cavalier a dépassé 4 cours dans la semaine ?
        total_semaine = Participation.objects.filter(
            cavalier=self.cavalier
        ).exclude(pk=self.pk).count()
        if total_semaine >= 4:
            raise ValidationError(f"{self.cavalier.prenom} {self.cavalier.nom} a déjà atteint 4 cours cette semaine.")

        # 4️⃣ Cavalier en cours débutant ne peut pas faire concours
        if self.cours.niveau.lower() == "concours":
            debutant = Participation.objects.filter(
                cavalier=self.cavalier,
                cours__niveau__iexact="débutant"
            ).exclude(pk=self.pk)
            if debutant.exists():
                raise ValidationError("Ce cavalier suit un cours Débutant et ne peut pas participer à un Concours.")

        # 5️⃣ Cheval de moins de 6 ans ?
        if self.cheval.age < 6:
            if self.cours.niveau.lower() == "concours":
                raise ValidationError(f"{self.cheval.nom} a moins de 6 ans et ne peut pas faire de concours.")
            if not Moniteur.objects.filter(
                nom=self.cavalier.nom,
                prenom=self.cavalier.prenom
            ).exists():
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

