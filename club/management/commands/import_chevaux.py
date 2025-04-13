import csv
from django.core.management.base import BaseCommand
from club.models import Cheval

class Command(BaseCommand):
    help = 'Importe les chevaux depuis un fichier CSV'

    def handle(self, *args, **kwargs):
        csv_path = "club-equestre/monsite/chevaux_data_modifie.csv"  # Ton fichier CSV

        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            count = 0
            for row in reader:
                Cheval.objects.create(
                    nom=row["nom"],
                    age=int(row["age"]),
                    race=row["race"],
                    seances_travail=int(row["seances_travail"]),
                    disponible=row["disponible"].strip().lower() in ["oui", "true", "1"]
                )
                count += 1

        self.stdout.write(self.style.SUCCESS(f"{count} chevaux importés avec succès."))