import json
from django.test import TestCase
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient as Client
from rest_framework.authtoken.models import Token
from freezegun import freeze_time

from accounts.models import User
from documents.models import Document, Folder


class DocumentApiTestCase(TestCase):
    """
    Base class for Document endpoint integration tests
    """
    def setUp(self):
        self.url = "/documents/"
        self.username = "jdoe"
        self.password = "p@ssw0rd"
        self.user = User.objects.create(
            username=self.username,
            password=self.password,
            email="jdoe@example.com"
        )

        with freeze_time("2020-01-01"):
            self.root_folder = Folder.add_root(name="root")

        with freeze_time("2021-01-01"):
            self.child_folder = self.root_folder.add_child(name="child")

        with freeze_time("2021-01-01"):
            self.document1 = Document(
                name="doc 1",
                folder=self.root_folder
            )
            self.document1.file.save("foo.txt", ContentFile(b"lorem ipsum"))
            self.document1.save()

        with freeze_time("2021-02-01"):
            self.document2 = Document(
                name="doc 2",
                folder=self.child_folder
            )
            self.document2.file.save("bar.txt", ContentFile(b"lorem ipsum"))
            self.document2.save()


class DocumentApiAnonymousTestCase(DocumentApiTestCase):
    """
    Integration tests for anonymous users at Document endpoints
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
        response = client.patch(f"{self.url}{self.document1.pk}/", {
            "name": "foobar",
        })
        self.assertEqual(response.status_code, 401)

    def test_anonymous_user_delete(self):
        client = Client()
        response = client.delete(f"{self.url}{self.document1.pk}/")
        self.assertEqual(response.status_code, 401)


class DocumentApiAuthenticatedUserTestCase(DocumentApiTestCase):
    """
    Integration tests for authenticated users at Document endpoints
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
            "folder": self.child_folder.pk,
            "file": SimpleUploadedFile("new.txt", b"fdsafdsa", content_type="text/plain")
        })
        self.assertEqual(response.status_code, 201)
        new_pk = json.loads(response.content)["id"]
        new_file = Document.objects.get(pk=new_pk)
        self.assertIsNotNone(new_file.file)

    def test_authenticated_user_read(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)["count"], 2)

    def test_authenticated_user_update(self):
        response = self.client.patch(f"{self.url}{self.document1.pk}/", {
            "name": "foobar",
        })
        self.assertEqual(response.status_code, 200)
        updated_doc = Document.objects.get(pk=self.document1.pk)
        self.assertEqual(updated_doc.name, "foobar")

    def test_authenticated_user_delete(self):
        response = self.client.delete(f"{self.url}{self.document1.pk}/")
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Document.objects.count(), 1)


class DocumentApiFilterTestCase(DocumentApiTestCase):
    """
    Integration tests for filters at Document endpoints
    """
    def test_filter_name(self):
        response = self.client.get(f"{self.url}?name=doc 1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)["count"], 1)

    def test_filter_folder_id(self):
        response = self.client.get(f"{self.url}?folder_id={self.root_folder.pk}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)["count"], 1)

    def test_filter_created_at(self):
        response = self.client.get(f"{self.url}?created_at_before=2021-01-31T19:58:21.942889Z")
        self.assertEqual(response.status_code, 200)
        json_resp = json.loads(response.content)
        self.assertEqual(json_resp["count"], 1)
        self.assertEqual(json_resp["results"][0]["id"], str(self.document1.pk))

    def test_filter_updated_at(self):
        response = self.client.get(f"{self.url}?updated_at_before=2021-01-31T19:58:21.942889Z")
        json_resp = json.loads(response.content)
        self.assertEqual(json_resp["count"], 1)
        self.assertEqual(json_resp["results"][0]["id"], str(self.document1.pk))
