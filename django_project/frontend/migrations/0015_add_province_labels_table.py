# Generated by Django 4.1.10 on 2023-09-08 08:04

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("frontend", "0014_uploadspeciescsv"),
    ]

    operations = [
        migrations.RunSQL(
            """CREATE TABLE IF NOT EXISTS layer.zaf_provinces_small_scale (
                id int8 NULL,
                geom public.geometry NULL,
                adm1_en varchar(50) NULL
            );""",
            reverse_sql=migrations.RunSQL.noop
        ),
        migrations.RunSQL(
            """create table if not exists layer.province_labels as
            select id as id,
                st_centroid(st_makevalid(geom)) as geom,
                adm1_en as adm1_en
            from layer.zaf_provinces_small_scale""",
            reverse_sql="drop table if exists layer.province_label",
            elidable=False
        ),
    ]
