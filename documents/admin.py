from django.contrib import admin
from treebeard.forms import movenodeform_factory
from treebeard.admin import TreeAdmin

from documents.models import Folder


class FolderAdmin(TreeAdmin):
    form = movenodeform_factory(Folder)


admin.site.register(Folder, FolderAdmin)
