import django_filters
from django.core.exceptions import ObjectDoesNotExist

from documents.models import Document, Folder, Topic


class FolderFilter(django_filters.FilterSet):
    parent = django_filters.UUIDFilter(method="filter_parent")
    child = django_filters.UUIDFilter(method="filter_child")
    topics = django_filters.ModelMultipleChoiceFilter(queryset=Topic.objects.all())
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
            'topics',
            'created_at',
            'updated_at'
        ]


class DocumentFilter(django_filters.FilterSet):
    folder_id = django_filters.UUIDFilter(field_name='folder__pk', lookup_expr='exact')
    topics = django_filters.ModelMultipleChoiceFilter(queryset=Topic.objects.all())
    created_at = django_filters.IsoDateTimeFromToRangeFilter()
    updated_at = django_filters.IsoDateTimeFromToRangeFilter()

    class Meta:
        model = Document
        fields = [
            'id',
            'name',
            'folder_id',
            'topics',
            'created_at',
            'updated_at'
        ]


class TopicFilter(django_filters.FilterSet):
    folders = django_filters.ModelMultipleChoiceFilter(queryset=Folder.objects.all())
    documents = django_filters.ModelMultipleChoiceFilter(queryset=Document.objects.all())
    created_at = django_filters.IsoDateTimeFromToRangeFilter()
    updated_at = django_filters.IsoDateTimeFromToRangeFilter()

    class Meta:
        model = Topic
        fields = [
            'id',
            'name',
            'folders',
            'documents',
            'created_at',
            'updated_at'
        ]
