from django import forms
from django.db import models
from django.utils.translation import gettext_lazy as _


class STextField(models.CharField):
    """Single-line-TextField / Unlimited-length-Charfield.

    PROBLEM IT SOLVES: In Postgres we tend to just use `text` data type everywhere,
        but we want most fields to be displayed as single-line text inputs, not as
        textarea as Django does with TextFields.
    """
    description = _("Practically an unlimited length CharField")

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = int(1e9)  # Satisfy management validation.
        super().__init__(*args, **kwargs)
        # Don't add max-length validator like CharField does.

    def get_internal_type(self):
        # This has no function, since this value is used as a lookup in
        # db_type().  Put something that isn't known by django so it
        # raises an error if it is ever used.
        return 'LongCharField'

    def db_type(self, connection):
        # *** This is probably only compatible with Postgres.
        return 'text'

    def formfield(self, **kwargs):
        # Don't pass max_length to form field like CharField does.
        return super(models.CharField, self).formfield(**kwargs)


# class TimestampedModel(models.Model):
#     class Meta:
#         abstract = True
#         ordering = ['created_at']
#
#     created_at = models.DateTimeField(db_index=True, auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)


# class ClonableMixin(object):
#     """
#     Any clonable model is expected to have some utility functions, but we
#     leave the actual cloning logic to particular model classes since this
#     is likely to be custom with respect to related objects.
#
#     EXPECTATIONS:
#         - subclass of models.Model
#     """
#
#     def get_clean_data(self, skip=set()):
#         return {
#             k: v for k, v in self.__dict__.items()
#             if k[0] != '_' and k not in skip
#         }
#
#     def clone(self, update={}):
#         clone_data = self.get_clean_data(skip={'id'})
#         clone_data.update(update)
#         return self.__class__.objects.create(**clone_data)
