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


class Document(models.Model):
    """
    An instance is a document in the document store.

    File assets are stored in S3. The Document model organizes these assets
    into Folders and Topics.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(
        help_text=_("A short, human-friendly identifier for the document."),
        max_length=255  # max filename length in Windows & UNIX
    )

    long_description = models.TextField(
        help_text=_("A longer description for the document. Optional."),
        blank=True,
        default=""
    )

    file = models.FileField()

    folder = models.ForeignKey(to="documents.Folder", on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Document: {self.name}"

    class Meta:
        verbose_name = _("Document")
        verbose_name_plural = _("Documents")


class Topic(models.Model):
    """
    An instance is a Topic, a tag for documents and folders.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(
        help_text=_("A short, human-friendly identifier for the topic."),
        max_length=255  # max filename length in Windows & UNIX
    )

    long_description = models.TextField(
        help_text=_("A longer description for the topic. Optional."),
        blank=True,
        default=""
    )

    folders = models.ManyToManyField(to="documents.Folder", related_name="topics")

    documents = models.ManyToManyField(to="documents.Document", related_name="topics")

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Topic: {self.name}"

    class Meta:
        verbose_name = _("Topic")
        verbose_name_plural = _("Topics")
