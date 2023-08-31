# Generated by Django 4.1.10 on 2023-08-29 17:33

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("stakeholder", "0010_organisation_national_organisation_province"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="allowing_sanbi_to_expose_data",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="hosting_through_sanbi_platforms",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="use_of_data_by_sanbi_only",
            field=models.BooleanField(default=False),
        ),
    ]