import uuid
from django.db import models
from django.utils.translation import ugettext_lazy as _
from treebeard.mp_tree import MP_Node


class Folder(MP_Node):
    """
    An instance is a folder in the document store.

    Folders are used to organize documents in the document store. They are
    hierarchical, and may have parents and children. They can be tagged with
    Topics to help users find them. Each Document in the store belongs to a
    Folder.

    We are using a Materialized Path tree to capture the hierarchical
    relationship between folders. Ref:
        https://django-treebeard.readthedocs.io/en/latest/mp_tree.html
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(
        help_text=_("A short, human-friendly identifier for the folder."),
        max_length=255  # max filename length in Windows & UNIX
    )

    long_description = models.TextField(
        help_text=_("A longer description for the folder. Optional."),
        blank=True,
        default=""
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    node_order_by = ['name', 'id']

    def __str__(self):
        return f"Folder: {self.name}"

    class Meta:
        verbose_name = _("Folder")
        verbose_name_plural = _("Folders")
