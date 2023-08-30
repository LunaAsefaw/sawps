# Generated by Django 4.1.10 on 2023-08-07 06:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("species", "0007_remove_ownedspecies_management_status_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="taxon",
            name="colour_variant",
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="taxon",
            name="taxon_rank",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="species.taxonrank",
            ),
        ),
    ]