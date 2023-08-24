# Generated by Django 4.1.10 on 2023-08-24 12:14

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("population_data", "0011_samplingeffortcoverage_and_more"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="annualpopulationperactivity",
            name="unique_population_count_per_activity",
        ),
        migrations.AddConstraint(
            model_name="annualpopulationperactivity",
            constraint=models.UniqueConstraint(
                fields=("year", "owned_species", "activity_type"),
                name="unique_population_count_per_activity",
            ),
        ),
    ]