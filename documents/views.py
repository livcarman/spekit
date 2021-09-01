from rest_framework import viewsets
from rest_framework import permissions

from documents.models import Folder
from documents.serializers import FolderSerializer
from documents.filters import FolderFilter


class FolderViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows CRUD operations on Folder objects
    """
    queryset = Folder.objects.all().order_by('-created_at')
    serializer_class = FolderSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_class = FolderFilter
