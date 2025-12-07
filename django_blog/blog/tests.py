# blog/tests.py
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Post

class PostCRUDTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        self.post = Post.objects.create(
            title='Test Post',
            content='Test Content',
            author=self.user
        )
    
    def test_post_list_view(self):
        response = self.client.get(reverse('blog-home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Post')
        self.assertTemplateUsed(response, 'blog/post_list.html')
    
    def test_post_detail_view(self):
        response = self.client.get(reverse('post-detail', args=[self.post.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Post')
        self.assertTemplateUsed(response, 'blog/post_detail.html')
    
    def test_post_create_view_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('post-create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/post_form.html')
    
    def test_post_create_view_unauthenticated(self):
        response = self.client.get(reverse('post-create'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_post_update_view_author(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('post-update', args=[self.post.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/post_form.html')
    
    def test_post_update_view_non_author(self):
        self.client.login(username='otheruser', password='testpass123')
        response = self.client.get(reverse('post-update', args=[self.post.pk]))
        self.assertEqual(response.status_code, 403)  # Forbidden
    
    def test_post_delete_view_author(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('post-delete', args=[self.post.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/post_confirm_delete.html')
    
    def test_post_delete_view_non_author(self):
        self.client.login(username='otheruser', password='testpass123')
        response = self.client.get(reverse('post-delete', args=[self.post.pk]))
        self.assertEqual(response.status_code, 403)  # Forbidden
