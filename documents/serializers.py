from rest_framework import serializers

from documents.models import Document, Folder, Topic


class FolderSerializer(serializers.ModelSerializer):
    parent = serializers.PrimaryKeyRelatedField(
        allow_null=True,
        source="get_parent",
        queryset=Folder.objects.all()
    )
    children = serializers.PrimaryKeyRelatedField(
        source="get_children",
        many=True,
        read_only=True
    )
    topics = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Topic.objects.all()
    )

    def validate_parent(self, value):
        if value and self.instance and self.instance.pk and self.instance.pk == value.pk:
            raise serializers.ValidationError(
                'A folder cannot be its own parent.'
            )

        return value

    def create(self, validated_data):
        parent = validated_data.pop('get_parent')

        try:
            topics = validated_data.pop('topics')
        except KeyError:
            topics = None

        folder = Folder(**validated_data)

        if parent:
            parent.add_child(instance=folder)
        else:
            root = Folder.get_last_root_node()

            if root:
                root.add_sibling(instance=folder)
            else:
                Folder.add_root(instance=folder)

        if topics:
            folder.topics.set(topics)
            folder.save()

        return folder

    def update(self, instance, validated_data):
        try:
            parent = validated_data.pop('get_parent')
        except KeyError:
            parent = instance.get_parent()

        try:
            topics = validated_data.pop('topics')
        except KeyError:
            topics = instance.topics.all()

        instance.topics.set(topics)

        for k, v in validated_data.items():
            setattr(instance, k, v)

        instance.save()

        if parent is None:
            last_root = Folder.get_last_root_node()
            instance.move(last_root, "sorted-sibling")
        else:
            instance.move(parent, "sorted-child")

        # FIXME: This fix_tree() call probably shouldn't be here.
        # Occasionally, treebeard's denormalized fields seem to get out of sync
        # after moving nodes. fix_tree() will repair any inconsistencies.
        #
        # Putting this call in the request lifecycle is almost certainly
        # something that will not scale, but in the interest of time I've
        # thrown it in here to make the demo functional. Without it, I was
        # periodically getting IntegrityErrors from the check condition on
        # num_children.
        instance.fix_tree()

        # Need to refetch instance because of treebeard's caching
        return Folder.objects.get(pk=instance.pk)

    class Meta:
        model = Folder
        fields = [
            'id',
            'name',
            'long_description',
            'parent',
            'topics',
            'children',
            'created_at',
            'updated_at'
        ]


class DocumentSerializer(serializers.ModelSerializer):
    folder = serializers.PrimaryKeyRelatedField(
        queryset=Folder.objects.all()
    )
    topics = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Topic.objects.all()
    )

    class Meta:
        model = Document
        fields = [
            'id',
            'name',
            'long_description',
            'folder',
            'file',
            'topics',
            'created_at',
            'updated_at'
        ]


class TopicSerializer(serializers.ModelSerializer):
    folders = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Folder.objects.all()
    )
    documents = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Document.objects.all()
    )

    class Meta:
        model = Topic
        fields = [
            'id',
            'name',
            'long_description',
            'folders',
            'documents',
            'created_at',
            'updated_at'
        ]
