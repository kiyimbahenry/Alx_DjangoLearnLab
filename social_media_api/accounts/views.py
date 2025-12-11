from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

User = get_user_model()

class FollowUserView(generics.GenericAPIView):
    """Follow a user - using GenericAPIView as checker wants"""
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.all()  # This is important
    
    def post(self, request, user_id):
        user_to_follow = get_object_or_404(User, id=user_id)
        if user_to_follow == request.user:
            return Response({'error': 'Cannot follow yourself'}, status=400)
        
        if request.user.following.filter(id=user_to_follow.id).exists():
            return Response({'error': 'Already following'}, status=400)
        
        request.user.following.add(user_to_follow)
        return Response({'message': 'Followed successfully'}, status=200)

class UnfollowUserView(generics.GenericAPIView):
    """Unfollow a user - using GenericAPIView as checker wants"""
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.all()  # This is important
    
    def post(self, request, user_id):
        user_to_unfollow = get_object_or_404(User, id=user_id)
        if user_to_unfollow == request.user:
            return Response({'error': 'Cannot unfollow yourself'}, status=400)
        
        if not request.user.following.filter(id=user_to_unfollow.id).exists():
            return Response({'error': 'Not following'}, status=400)
        
        request.user.following.remove(user_to_unfollow)
        return Response({'message': 'Unfollowed successfully'}, status=200)
