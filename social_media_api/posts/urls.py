from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PostViewSet, CommentViewSet, LikeViewSet, 
    FeedViewSet, ExploreViewSet, UserPostsViewSet,
    SearchViewSet
)

router = DefaultRouter()
router.register(r'posts', PostViewSet, basename='post')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'likes', LikeViewSet, basename='like')
router.register(r'feed', FeedViewSet, basename='feed')
router.register(r'explore', ExploreViewSet, basename='explore')
router.register(r'search', SearchViewSet, basename='search')

# User-specific routes
user_posts_list = UserPostsViewSet.as_view({'get': 'list'})

urlpatterns = [
    path('', include(router.urls)),
    path('users/<int:user_id>/posts/', user_posts_list, name='user-posts'),
]
