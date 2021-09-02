from rest_framework import viewsets
from rest_framework import permissions

from documents.models import Document, Folder
from documents.serializers import DocumentSerializer, FolderSerializer
from documents.filters import DocumentFilter, FolderFilter


class FolderViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows CRUD operations on Folder objects
    """
    queryset = Folder.objects.all().order_by('-created_at')
    serializer_class = FolderSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_class = FolderFilter


class DocumentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows CRUD operations on Document objects
    """
    queryset = Document.objects.all().order_by('-created_at')
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_class = DocumentFilter
