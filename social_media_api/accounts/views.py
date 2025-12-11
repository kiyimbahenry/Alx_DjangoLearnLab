from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from django.contrib.auth import authenticate, login
from django.shortcuts import get_object_or_404
from django.db.models import Q

# Import User model correctly
from django.contrib.auth import get_user_model
User = get_user_model()

# Import serializers
from .serializers import (
    UserSerializer, RegisterSerializer, 
    LoginSerializer
)

class RegisterView(generics.CreateAPIView):
    """User registration view"""
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create user
        user = serializer.save()
        
        # Get token
        token, created = Token.objects.get_or_create(user=user)
        
        # Prepare response data
        response_data = {
            'message': 'User registered successfully',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
            },
            'token': token.key
        }
        
        return Response(response_data, status=status.HTTP_201_CREATED)

class LoginView(APIView):
    """User login view"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token = serializer.validated_data['token']
            
            # Login the user (for session auth if needed)
            login(request, user)
            
            response_data = {
                'message': 'Login successful',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                },
                'token': token
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(generics.RetrieveUpdateAPIView):
    """Get or update user profile"""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

class LogoutView(APIView):
    """Logout view"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # Delete the token
        Token.objects.filter(user=request.user).delete()
        return Response({
            'message': 'Logged out successfully'
        }, status=status.HTTP_200_OK)

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing users"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = User.objects.all()
        search = self.request.query_params.get('search', None)
        
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search)
            )
        
        return queryset
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def follow(self, request, pk=None):
        """Follow a user"""
        user_to_follow = self.get_object()
        current_user = request.user
        
        if user_to_follow == current_user:
            return Response(
                {'error': 'You cannot follow yourself'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if current_user.following.filter(id=user_to_follow.id).exists():
            return Response(
                {'error': 'You are already following this user'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        current_user.following.add(user_to_follow)
        
        return Response({
            'message': f'You are now following {user_to_follow.username}',
            'following': True,
            'followers_count': user_to_follow.followers.count(),
            'following_count': current_user.following.count()
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def unfollow(self, request, pk=None):
        """Unfollow a user"""
        user_to_unfollow = self.get_object()
        current_user = request.user
        
        if user_to_unfollow == current_user:
            return Response(
                {'error': 'You cannot unfollow yourself'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not current_user.following.filter(id=user_to_unfollow.id).exists():
            return Response(
                {'error': 'You are not following this user'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        current_user.following.remove(user_to_unfollow)
        
        return Response({
            'message': f'You have unfollowed {user_to_unfollow.username}',
            'following': False,
            'followers_count': user_to_unfollow.followers.count(),
            'following_count': current_user.following.count()
        }, status=status.HTTP_200_OK)

class FollowUserView(APIView):
    """Alternative view for following/unfollowing users"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, user_id):
        try:
            user_to_follow = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        if user_to_follow == request.user:
            return Response(
                {'error': 'Cannot follow/unfollow yourself'},
                status=status.HTTP_400_BAD_REQUEST
            )

        current_user = request.user
        
        if current_user.following.filter(id=user_to_follow.id).exists():
            current_user.following.remove(user_to_follow)
            action = 'unfollowed'
            following = False
        else:
            current_user.following.add(user_to_follow)
            action = 'followed'
            following = True

        return Response({
            'message': f'Successfully {action} {user_to_follow.username}',
            'following': following,
            'followers_count': user_to_follow.followers.count(),
            'following_count': current_user.following.count()
        })
