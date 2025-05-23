# Generated by Django 4.2.20 on 2025-04-11 00:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("club", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="cours", options={"ordering": ["jour", "heure_debut"]},
        ),
        migrations.RenameField(
            model_name="cours", old_name="titre", new_name="niveau",
        ),
        migrations.RemoveField(model_name="cours", name="date",),
        migrations.AddField(
            model_name="cours",
            name="heure_debut",
            field=models.TimeField(default="09:00"),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="cours",
            name="heure_fin",
            field=models.TimeField(default="09:00"),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="cours",
            name="jour",
            field=models.CharField(
                choices=[
                    ("lundi", "Lundi"),
                    ("mardi", "Mardi"),
                    ("mercredi", "Mercredi"),
                    ("jeudi", "Jeudi"),
                    ("vendredi", "Vendredi"),
                    ("samedi", "Samedi"),
                ],
                default=9,
                max_length=10,
            ),
            preserve_default=False,
        ),
    ]
