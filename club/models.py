from django.db import models


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
    titre = models.CharField(max_length=100)
    date = models.DateTimeField()
    cheval = models.ForeignKey(Cheval, on_delete=models.CASCADE)
    cavalier = models.ForeignKey(Cavalier, on_delete=models.CASCADE)
    entraineur = models.ForeignKey(Moniteur, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.titre} - {self.date.strftime('%d/%m/%Y')}"


class Inscription(models.Model):
    cavalier = models.ForeignKey(Cavalier, on_delete=models.CASCADE)
    cours = models.ForeignKey(Cours, on_delete=models.CASCADE)
    date_inscription = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.cavalier} inscrit à {self.cours}"
