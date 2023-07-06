# Generated by Django 4.1.7 on 2023-07-04 08:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("frontend", "0008_boundarysearchrequest_boundaryfile"),
    ]

    operations = [
        migrations.CreateModel(
            name="ContextLayerLegend",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=512)),
                ("colour", models.CharField(blank=True, max_length=20, null=True)),
                (
                    "layer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="frontend.contextlayer",
                    ),
                ),
            ],
        ),
    ]