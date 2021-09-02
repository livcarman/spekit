import json
from django.test import TestCase
from django.core.files.base import ContentFile
from rest_framework.test import APIClient as Client
from rest_framework.authtoken.models import Token
from freezegun import freeze_time

from accounts.models import User
from documents.models import Document, Folder, Topic


class TopicApiTestCase(TestCase):
    """
    Base class for Topic endpoint integration tests
    """
    def setUp(self):
        self.url = "/topics/"
        self.username = "jdoe"
        self.password = "p@ssw0rd"
        self.user = User.objects.create(
            username=self.username,
            password=self.password,
            email="jdoe@example.com"
        )

        with freeze_time("2020-01-01"):
            self.root_folder = Folder.add_root(name="root")
            self.child_folder = self.root_folder.add_child(name="child")

            self.document1 = Document(
                name="doc 1",
                folder=self.root_folder
            )
            self.document1.file.save("foo.txt", ContentFile(b"lorem ipsum"))
            self.document1.save()

            self.document2 = Document(
                name="doc 2",
                folder=self.child_folder
            )
            self.document2.file.save("bar.txt", ContentFile(b"lorem ipsum"))
            self.document2.save()

            self.topic1 = Topic.objects.create(name='topic 1')
            self.topic1.documents.add(self.document1)
            self.topic1.folders.add(self.root_folder)

        with freeze_time("2020-02-01"):
            self.topic2 = Topic.objects.create(name='topic 2')
            self.topic2.documents.add(self.document2)
            self.topic2.folders.add(self.child_folder)


class TopicApiAnonymousTestCase(TopicApiTestCase):
    """
    Integration tests for anonymous users at Topic endpoints
    """
    def test_anonymous_user_create(self):
        client = Client()
        response = client.post(self.url, {
            "name": "foo",
            "long_description": "bar"
        })
        self.assertEqual(response.status_code, 401)

    def test_anonymous_user_read(self):
        client = Client()
        response = client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)["count"], 2)

    def test_anonymous_user_update(self):
        client = Client()
        response = client.patch(f"{self.url}{self.topic1.pk}/", {
            "name": "foobar",
        })
        self.assertEqual(response.status_code, 401)

    def test_anonymous_user_delete(self):
        client = Client()
        response = client.delete(f"{self.url}{self.topic1.pk}/")
        self.assertEqual(response.status_code, 401)


class TopicApiAuthenticatedUserTestCase(TopicApiTestCase):
    """
    Integration tests for authenticated users at Topic endpoints
    """
    def setUp(self):
        super().setUp()
        self.client = Client()
        token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    def test_authenticated_user_create(self):
        response = self.client.post(self.url, {
            "name": "new doc",
            "long_description": "bar",
            "folders": [self.root_folder.pk],
            "documents": [self.document1.pk]
        })
        self.assertEqual(response.status_code, 201)
        new_pk = json.loads(response.content)["id"]
        new_topic = Topic.objects.get(pk=new_pk)
        self.assertEqual(new_topic.folders.all().count(), 1)
        self.assertEqual(new_topic.documents.all().count(), 1)

    def test_authenticated_user_read(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)["count"], 2)

    def test_authenticated_user_update(self):
        response = self.client.patch(f"{self.url}{self.topic1.pk}/", {
            "name": "foobar",
        })
        self.assertEqual(response.status_code, 200)
        updated_topic = Topic.objects.get(pk=self.topic1.pk)
        self.assertEqual(updated_topic.name, "foobar")

    def test_authenticated_user_delete(self):
        response = self.client.delete(f"{self.url}{self.topic1.pk}/")
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Topic.objects.count(), 1)


class TopicApiFilterTestCase(TopicApiTestCase):
    """
    Integration tests for filters at Document endpoints
    """
    def test_filter_name(self):
        response = self.client.get(f"{self.url}?name=topic 1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)["count"], 1)

    def test_filter_folders(self):
        response = self.client.get(f"{self.url}?folders={self.root_folder.pk}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)["count"], 1)

    def test_filter_documents(self):
        response = self.client.get(f"{self.url}?documents={self.document1.pk}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)["count"], 1)

    def test_filter_created_at(self):
        response = self.client.get(f"{self.url}?created_at_before=2020-01-15T19:58:21.942889Z")
        self.assertEqual(response.status_code, 200)
        json_resp = json.loads(response.content)
        self.assertEqual(json_resp["count"], 1)
        self.assertEqual(json_resp["results"][0]["id"], str(self.topic1.pk))

    def test_filter_updated_at(self):
        response = self.client.get(f"{self.url}?updated_at_before=2020-01-15T19:58:21.942889Z")
        json_resp = json.loads(response.content)
        self.assertEqual(json_resp["count"], 1)
        self.assertEqual(json_resp["results"][0]["id"], str(self.topic1.pk))
