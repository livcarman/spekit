import json
from django.test import TestCase
from rest_framework.test import APIClient as Client
from rest_framework.authtoken.models import Token
from freezegun import freeze_time

from accounts.models import User
from documents.models import Folder


class FolderApiTestCase(TestCase):
    """
    Base class for Folder endpoint integration tests
    """
    def setUp(self):
        self.url = "/folders/"
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

        with freeze_time("2021-01-30"):
            self.grandchild_folder = self.child_folder.add_child(name="grandchild")


class FolderApiAnonymousTestCase(FolderApiTestCase):
    """
    Integration tests for anonymous users at Folder endpoints
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
        self.assertEqual(json.loads(response.content)["count"], 3)

    def test_anonymous_user_update(self):
        client = Client()
        response = client.patch(f"{self.url}{self.root_folder.pk}/", {
            "name": "foobar",
        })
        self.assertEqual(response.status_code, 401)

    def test_anonymous_user_delete(self):
        client = Client()
        response = client.delete(f"{self.url}{self.root_folder.pk}/")
        self.assertEqual(response.status_code, 401)


class FolderApiAuthenticatedUserTestCase(FolderApiTestCase):
    """
    Integration tests for authenticated users at Folder endpoints
    """
    def setUp(self):
        super().setUp()
        self.client = Client()
        token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    def test_authenticated_user_create_root(self):
        response = self.client.post(self.url, {
            "name": "new root",
            "long_description": "bar",
            "parent": ""
        })
        self.assertEqual(response.status_code, 201)
        new_pk = json.loads(response.content)["id"]
        new_root = Folder.objects.get(pk=new_pk)
        self.assertIsNone(new_root.get_parent())

    def test_authenticated_user_create_leaf(self):
        response = self.client.post(self.url, {
            "name": "new root",
            "long_description": "bar",
            "parent": self.child_folder.pk
        })
        self.assertEqual(response.status_code, 201)
        new_pk = json.loads(response.content)["id"]
        new_leaf = Folder.objects.get(pk=new_pk)
        self.assertEqual(new_leaf.get_parent().pk, self.child_folder.pk)

    def test_authenticated_user_read(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)["count"], 3)

    def test_authenticated_user_update(self):
        response = self.client.patch(f"{self.url}{self.root_folder.pk}/", {
            "name": "foobar",
        })
        self.assertEqual(response.status_code, 200)
        updated_root = Folder.objects.get(pk=self.root_folder.pk)
        self.assertEqual(updated_root.name, "foobar")

    def test_authenticated_user_move_root(self):
        new_node = Folder.add_root(name="bar")
        response = self.client.patch(f"{self.url}{self.root_folder.pk}/", {
            "parent": new_node.pk,
        })
        self.assertEqual(response.status_code, 200)
        updated_root = Folder.objects.get(pk=self.root_folder.pk)
        self.assertEqual(updated_root.get_parent().pk, new_node.pk)

    def test_authenticated_user_move_leaf(self):
        new_node = Folder.add_root(name="bar")
        response = self.client.patch(f"{self.url}{self.grandchild_folder.pk}/", {
            "parent": new_node.pk,
        })
        self.assertEqual(response.status_code, 200)
        updated_leaf = Folder.objects.get(pk=self.grandchild_folder.pk)
        self.assertEqual(updated_leaf.get_parent().pk, new_node.pk)

    def test_authenticated_user_move_branch(self):
        new_node = Folder.add_root(name="bar")
        response = self.client.patch(f"{self.url}{self.child_folder.pk}/", {
            "parent": new_node.pk,
        })
        self.assertEqual(response.status_code, 200)
        updated_leaf = Folder.objects.get(pk=self.child_folder.pk)
        self.assertEqual(updated_leaf.get_parent().pk, new_node.pk)

    def test_authenticated_user_delete(self):
        response = self.client.delete(f"{self.url}{self.child_folder.pk}/")
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Folder.objects.count(), 1)


class FolderApiFilterTestCase(FolderApiTestCase):
    """
    Integration tests for filters at Folder endpoints
    """
    def test_filter_name(self):
        response = self.client.get(f"{self.url}?name=root")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)["count"], 1)

    def test_filter_parent(self):
        response = self.client.get(f"{self.url}?parent={self.root_folder.pk}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)["count"], 1)

    def test_filter_child(self):
        response = self.client.get(f"{self.url}?child={self.child_folder.pk}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)["count"], 1)

    def test_filter_created_at(self):
        response = self.client.get(f"{self.url}?created_at_before=2020-09-01T19:58:21.942889Z")
        self.assertEqual(response.status_code, 200)
        json_resp = json.loads(response.content)
        self.assertEqual(json_resp["count"], 1)
        self.assertEqual(json_resp["results"][0]["id"], str(self.root_folder.pk))

    def test_filter_updated_at(self):
        response = self.client.get(f"{self.url}?updated_at_before=2020-09-01T19:58:21.942889Z")
        json_resp = json.loads(response.content)
        self.assertEqual(json_resp["count"], 1)
        self.assertEqual(json_resp["results"][0]["id"], str(self.root_folder.pk))
