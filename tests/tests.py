from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User


class TestHomeView(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("reviewer:home")
        self.user = User.objects.create_user("testuser", "test@example.com", "testpassword")

    def test_home_view_GET(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

        self.client.login(username="testuser", password="testpassword")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_get(self):
        url = reverse("reviewer:home")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    # def test_post_valid_url(self):
    #     self.client.login(username="testuser", password="testpassword")
    #     url = reverse("reviewer:home")
    #     data = {"url": "https://play.google.com/store/apps/details?id=com.nianticlabs.pokemongo"}
    #     response = self.client.post(url, data=data)
    #     self.assertRedirects(
    #         response,
    #         url,
    #         status_code=200,
    #         target_status_code=302,
    #         msg_prefix="",
    #         fetch_redirect_response=True,
    #     )
    #     self.assertContains(response, "ポケットモンスターシリーズの最新作")

    # def test_post_invalid_url(self):
    #     self.client.login(username="testuser", password="testpassword")
    #     url = reverse("reviewer:home")
    #     data = {"url": "https://example.com"}
    #     response = self.client.post(url, data=data)
    #     self.assertRedirects(
    #         response,
    #         url,
    #         status_code=200,
    #         target_status_code=302,
    #         msg_prefix="",
    #         fetch_redirect_response=True,
    #     )
    #     self.assertContains(response, "GooglePlayアプリストアのURLではありません。正しいURLを入力してください。")
