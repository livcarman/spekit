import django_filters
from django.core.exceptions import ObjectDoesNotExist

from documents.models import Folder


class FolderFilter(django_filters.FilterSet):
    parent = django_filters.UUIDFilter(method="filter_parent")
    child = django_filters.UUIDFilter(method="filter_child")
    created_at = django_filters.IsoDateTimeFromToRangeFilter()
    updated_at = django_filters.IsoDateTimeFromToRangeFilter()

    def filter_parent(self, queryset, name, value):
        try:
            child_pks = Folder.objects.get(pk=value).get_children()
            return queryset.filter(pk__in=child_pks)
        except ObjectDoesNotExist:
            return Folder.objects.none()

    def filter_child(self, queryset, name, value):
        try:
            parent = Folder.objects.get(pk=value).get_parent()
            return queryset.filter(pk=parent.pk)
        except (ObjectDoesNotExist, AttributeError):
            return Folder.objects.none()

    class Meta:
        model = Folder
        fields = [
            'id',
            'name',
            'parent',
            'created_at',
            'updated_at'
        ]
