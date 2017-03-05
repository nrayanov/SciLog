from django.contrib.auth.models import User
from django.db import models
from django.core.exceptions import ValidationError

from protocols.models import Protocol
from projects.models import Project


class University(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = 'Universities'

    def __str__(self):
        return self.name


class Role(models.Model):
    ROLES = (
        ('owner', 'Owner'),
        ('contributor', 'Contributor'),
        ('watcher', 'Watcher'),
    )
    ROLES_CAN_EDIT = (
        'owner',
        'contributor'
    )
    ROLES_TO_INVITE = (
        ('contributor', 'Contributor'),
        ('watcher', 'Watcher'),
    )

    researcher = models.ForeignKey('Researcher', related_name='roles')
    project = models.ForeignKey(
        'projects.Project',
        related_name='roles',
        null=True,
        blank=True)
    protocol = models.ForeignKey(
        'protocols.Protocol',
        related_name='roles',
        null=True,
        blank=True)
    role = models.CharField(max_length=255, choices=ROLES)

    class Meta:
        unique_together = (
            ('researcher', 'project'),
            ('researcher', 'protocol'))

    def __str__(self):
        role_object_label = ''
        if self.project:
            role_object_label = 'project {}'.format(self.project.name)
        elif self.protocol:
            role_object_label = 'protocol {}'.format(self.protocol.name)
        return '{} {} of/to {}'.format(
            self.researcher.user.username,
            self.get_role_display(),
            role_object_label
        )

    def clean(self):
        if not(self.project or self.protocol):
            raise ValidationError('You must choose \
either project or protocol!')
        if self.project and self.protocol:
            raise ValidationError('You cannot select \
project and protocol for the same role!')
        if self.role == 'owner':
            if self.project and self.project.roles.filter(role='owner').exists:
                raise ValidationError('There is already \
an owner of this project!')
            if self.protocol and self.protocol.roles.filter(
                    role='owner').exists:
                raise ValidationError('There is already \
an owner of this protocol!')

    @classmethod
    def get_db_roles(cls):
        return [role[0] for role in cls.ROLES]


class Researcher(models.Model):
    user = models.OneToOneField(User, related_name='researcher')
    university = models.ForeignKey(
        University,
        related_name='researchers',
        null=True,
        blank=True)
    scientific_degree = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        if self.user.first_name and self.user.last_name:
            return '{} {}'.format(self.user.first_name, self.user.last_name)
        else:
            return self.user.username

    def get_roles(self, scope=None, roles=Role.get_db_roles()):
        """
        Returns roles list django query set based on
        scope and a list of role names.
        If no role names are specified all roles are selected.
        Scope defines if the query gets roles for projects, protocols or both.
        """
        if scope == 'project':
            return Role.objects.filter(
                researcher=self,
                role__in=roles,
                protocol=None
            ).exclude(project=None).select_related(scope)
        elif scope == 'protocol':
            return Role.objects.filter(
                researcher=self,
                role__in=roles,
                project=None
            ).exclude(protocol=None).select_related(scope)
        else:
            return Role.objects.filter(
                researcher=self,
                role__in=roles,).select_related('project', 'protocol')

    def get_protocols_to_add(self, project):
        if self.can_edit(project):
            protocols = Protocol.objects.filter(
                roles__researcher=self,
                roles__project=None
            ).exclude(id__in=[o.id for o in project.protocols.all()])
            return protocols
        else:
            return Protocol.objects.none()

    def get_sources_to_add(self, project):
        if self.can_edit(project):
            sources = self.sources.all().exclude(
                id__in=[o.id for o in project.sources.all()]
            )
            return sources
        else:
            return Source.objects.none()

    def can_edit(self, item):
        role = item.roles.get(researcher=self)
        return role.role in Role.ROLES_CAN_EDIT

    def get_projects_to_edit(self):
        projects = Project.objects.filter(
            roles__researcher=self,
            roles__protocol=None,
            roles__role__in=Role.ROLES_CAN_EDIT
        )
        return projects

    def get_protocols_to_edit(self):
        projects = Protocol.objects.filter(
            roles__researcher=self,
            roles__project=None,
            roles__role__in=Role.ROLES_CAN_EDIT
        )
        return projects


class Source(models.Model):
    name = models.CharField(max_length=255)
    researcher = models.ForeignKey(Researcher, related_name='sources')
    url = models.URLField(max_length=255, null=True, blank=True)
    isbn = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name
