from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import Post

User = get_user_model()

class FeedTests(APITestCase):
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
        self.user3 = User.objects.create_user(
            username='user3',
            email='user3@example.com',
            password='password123'
        )
        
        # Create posts
        self.post1 = Post.objects.create(
            author=self.user1,
            title='User1 Post',
            content='Content from user1'
        )
        self.post2 = Post.objects.create(
            author=self.user2,
            title='User2 Post',
            content='Content from user2'
        )
        self.post3 = Post.objects.create(
            author=self.user3,
            title='User3 Post',
            content='Content from user3'
        )
        
        self.client = APIClient()
        self.client.force_authenticate(user=self.user1)
    
    def test_feed_includes_followed_users_posts(self):
        # User1 follows User2
        self.user1.follow(self.user2)
        
        response = self.client.get('/api/posts/feed/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Feed should include posts from user2 and user1 (own posts)
        post_authors = [post['author']['username'] for post in response.data['results']]
        self.assertIn('user2', post_authors)
        self.assertIn('user1', post_authors)
        
        # Should NOT include posts from user3 (not followed)
        self.assertNotIn('user3', post_authors)
    
    def test_feed_ordering_most_recent_first(self):
        # Create another post for user1
        newer_post = Post.objects.create(
            author=self.user1,
            title='Newer Post',
            content='This is newer'
        )
        
        response = self.client.get('/api/posts/feed/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # First post should be the newest one
        self.assertEqual(response.data['results'][0]['id'], newer_post.id)
        self.assertEqual(response.data['results'][0]['title'], 'Newer Post')
    
    def test_feed_pagination(self):
        # Create many posts
        for i in range(15):
            Post.objects.create(
                author=self.user1,
                title=f'Post {i}',
                content=f'Content {i}'
            )
        
        response = self.client.get('/api/posts/feed/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should have pagination metadata
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        self.assertIn('total_pages', response.data)
        
        # Default page size is 10, so we should have next page
        self.assertIsNotNone(response.data['next'])
        self.assertEqual(len(response.data['results']), 10)
    
    def test_feed_empty_when_not_following_anyone(self):
        # User1 doesn't follow anyone yet
        response = self.client.get('/api/posts/feed/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should only see own posts
        for post in response.data['results']:
            self.assertEqual(post['author']['username'], 'user1')
    
    def test_trending_feed(self):
        # User1 follows User2
        self.user1.follow(self.user2)
        
        # Create a post and like it
        trending_post = Post.objects.create(
            author=self.user2,
            title='Trending Post',
            content='This post has many likes'
        )
        trending_post.likes.add(self.user1)
        
        response = self.client.get('/api/posts/feed/trending/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should include the trending post
        self.assertEqual(response.data['results'][0]['title'], 'Trending Post')
