# Generated by Django 5.2 on 2025-04-11 19:09

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("discussions", "0002_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="discussions",
            name="user",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="notes",
            name="discussion",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                to="discussions.discussions",
            ),
        ),
        migrations.AddField(
            model_name="notes",
            name="parent_note",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                to="discussions.notes",
            ),
        ),
        migrations.AddField(
            model_name="notes",
            name="thread",
            field=models.ForeignKey(
                blank=True,
                db_comment="Groups notes into top-level threads for organized display",
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="notes_thread_set",
                to="discussions.notes",
            ),
        ),
        migrations.AddField(
            model_name="notes",
            name="user",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="reprints",
            name="discussion",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                to="discussions.discussions",
            ),
        ),
        migrations.AddField(
            model_name="reprints",
            name="user",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
