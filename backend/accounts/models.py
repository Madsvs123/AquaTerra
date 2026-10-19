import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models

from common.choices import InvitationStatus, SystemRole
from common.models import TenantOwnedModel, TimeStampedModel


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=160, blank=True)
    title = models.CharField(max_length=120, blank=True)
    phone = models.CharField(max_length=40, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email
        if self.email:
            self.email = self.email.strip().lower()
        if not self.full_name:
            self.full_name = self.get_full_name() or self.email
        super().save(*args, **kwargs)

    def __str__(self):
        return self.full_name or self.email


class RoleDefinition(TenantOwnedModel):
    name = models.CharField(max_length=80)
    slug = models.SlugField(max_length=80)
    base_role = models.CharField(max_length=40, choices=SystemRole.CHOICES, default=SystemRole.VIEWER)
    permissions = models.JSONField(default=list)
    description = models.TextField(blank=True)

    class Meta:
        unique_together = ("organization", "slug")

    def __str__(self):
        return self.name


class Invitation(TenantOwnedModel):
    email = models.EmailField()
    role = models.CharField(max_length=40, choices=SystemRole.CHOICES, default=SystemRole.VIEWER)
    role_definition = models.ForeignKey(
        RoleDefinition, null=True, blank=True, on_delete=models.SET_NULL, related_name="invitations"
    )
    team = models.ForeignKey(
        "organizations.Team", null=True, blank=True, on_delete=models.SET_NULL, related_name="invitations"
    )
    assigned_farms = models.ManyToManyField("farms.Farm", blank=True, related_name="invitations")
    assigned_zones = models.ManyToManyField("farms.IrrigationZone", blank=True, related_name="invitations")
    restrict_to_assigned = models.BooleanField(default=False)
    token = models.CharField(max_length=96, unique=True)
    status = models.CharField(max_length=20, choices=InvitationStatus.CHOICES, default=InvitationStatus.PENDING)
    invited_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="sent_invitations")
    expires_at = models.DateTimeField()
    accepted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [models.Index(fields=["organization", "email", "status"])]

    def __str__(self):
        return f"{self.email} ({self.status})"


class ApiKey(TimeStampedModel):
    organization = models.ForeignKey(
        "organizations.Organization", on_delete=models.CASCADE, related_name="api_keys"
    )
    name = models.CharField(max_length=120)
    prefix = models.CharField(max_length=16)
    key_hash = models.CharField(max_length=64, unique=True)
    scopes = models.JSONField(default=list)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="api_keys")
    last_used_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    revoked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    @property
    def is_active(self):
        from django.utils import timezone

        if self.revoked_at:
            return False
        if self.expires_at and self.expires_at <= timezone.now():
            return False
        return True
