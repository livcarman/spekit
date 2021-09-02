from django.contrib import admin
from treebeard.forms import movenodeform_factory
from treebeard.admin import TreeAdmin

from documents.models import Document, Folder, Topic


class FolderAdmin(TreeAdmin):
    form = movenodeform_factory(Folder)


admin.site.register(Folder, FolderAdmin)
admin.site.register(Document, admin.ModelAdmin)
admin.site.register(Topic, admin.ModelAdmin)
