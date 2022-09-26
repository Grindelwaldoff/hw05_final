from django.db import models


class CreateModel(models.Model):
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания',
        db_index=True
    )

    class Meta:
        abstract = True
        ordering = ('-created',)
