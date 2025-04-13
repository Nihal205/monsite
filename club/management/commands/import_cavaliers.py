import csv
from django.core.management.base import BaseCommand
from club.models import Cavalier

class Command(BaseCommand):
    help = 'Importe les cavaliers depuis un fichier CSV'

    def handle(self, *args, **kwargs):
        csv_path = "cavaliers_final_gmail.csv"  # Ton fichier CSV
        print(f"Import depuis : {csv_path}")

        try:
            with open(csv_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                count = 0
                for row in reader:
                    Cavalier.objects.create(
                        nom=row["nom"],
                        prenom=row["prenom"],
                        age=int(row["age"]),
                        email=row["email"]
                    )
                    count += 1

            self.stdout.write(self.style.SUCCESS(f"{count} cavaliers importés avec succès."))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"Fichier non trouvé : {csv_path}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Erreur : {e}"))
