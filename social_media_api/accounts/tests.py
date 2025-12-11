from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

User = get_user_model()

class FollowTests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='password123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='password123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user1)
    
    def test_follow_user(self):
        response = self.client.post(f'/api/auth/users/{self.user2.id}/follow/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['following'], True)
        self.assertTrue(self.user1.is_following(self.user2))
        
        # Check followers count
        response = self.client.get(f'/api/auth/users/{self.user2.id}/')
        self.assertEqual(response.data['followers_count'], 1)
    
    def test_unfollow_user(self):
        # First follow
        self.user1.follow(self.user2)
        
        # Then unfollow
        response = self.client.post(f'/api/auth/users/{self.user2.id}/unfollow/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['following'], False)
        self.assertFalse(self.user1.is_following(self.user2))
    
    def test_cannot_follow_self(self):
        response = self.client.post(f'/api/auth/users/{self.user1.id}/follow/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('cannot follow yourself', response.data['error'])
    
    def test_get_followers_list(self):
        # User2 follows User1
        self.client.force_authenticate(user=self.user2)
        self.client.post(f'/api/auth/users/{self.user1.id}/follow/')
        
        # Get User1's followers
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(f'/api/auth/users/{self.user1.id}/followers/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['username'], 'user2')
    
    def test_get_following_list(self):
        # User1 follows User2
        self.client.post(f'/api/auth/users/{self.user2.id}/follow/')
        
        # Get User1's following list
        response = self.client.get(f'/api/auth/users/{self.user1.id}/following/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['username'], 'user2')
    
    def test_user_suggestions(self):
        # Create more users
        User.objects.create_user(username='user3', password='password123')
        User.objects.create_user(username='user4', password='password123')
        
        response = self.client.get('/api/auth/users/suggestions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should get suggestions (users not followed and not self)
        self.assertGreater(len(response.data), 0)
