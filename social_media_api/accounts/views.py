from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model
from .models import User
from .serializers import (
    UserSerializer, RegisterSerializer, 
    LoginSerializer
)

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    """
    User registration view that returns a token
    """
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
    """
    User login view that returns a token
    """
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
    """
    Get or update user profile
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        # Handle partial updates
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response({
            'message': 'Profile updated successfully',
            'user': serializer.data
        })

class UserListView(generics.ListAPIView):
    """
    List all users (for testing/following functionality)
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

class UserDetailView(generics.RetrieveAPIView):
    """
    Get specific user details
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

class LogoutView(APIView):
    """
    Logout view - delete user token
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # Delete the token
        Token.objects.filter(user=request.user).delete()
        return Response({
            'message': 'Logged out successfully'
        }, status=status.HTTP_200_OK)
