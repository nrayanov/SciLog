import os

from django.db import models
from django.core.exceptions import ValidationError

from researchers.models import Role


def create_unique_id():
    unique_id = os.urandom(4).hex()
    while(True):
        try:
            Project.objects.get(unique_id=unique_id)
        except Project.DoesNotExist:
            return(unique_id)
        unique_id = os.urandom(4).hex()


class Project(models.Model):
    unique_id = models.CharField(max_length=8, unique=True, default=create_unique_id)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255, blank=True)
    sources = models.ManyToManyField('researchers.Source', related_name='projects', blank=True)
    protocols = models.ManyToManyField('protocols.Protocol', related_name='projects', blank=True)
    datetime_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def get_participants_by_role(self):
        participants_by_role = list()
        for role_value, role_label in Role.ROLES:
            if self.roles.filter(role=role_value).exists():
                participants_by_role.append(
                    (
                        role_label,
                        self.roles.filter(
                            role=role_value).order_by('researcher')
                    )
                )
        return participants_by_role
