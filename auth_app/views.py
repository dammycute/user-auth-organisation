from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import User, Organisation
from .serializers import UserSerializer, OrganisationSerializer, UserLoginSerializer

class RegisterView(generics.CreateAPIView):
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            org_name = f"{user.firstName}'s Organisation"
            org = Organisation.objects.create(name=org_name)
            org.users.add(user)
            refresh = RefreshToken.for_user(user)
            return Response({
                "status": "success",
                "message": "Registration successful",
                "data": {
                    "accessToken": str(refresh.access_token),
                    "user": UserSerializer(user).data
                }
            }, status=status.HTTP_201_CREATED)
        return Response({
            "status": "Bad request",
            "message": "Registration unsuccessful",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class LoginView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(email=serializer.validated_data['email'], password=serializer.validated_data['password'])
            if user:
                refresh = RefreshToken.for_user(user)
                return Response({
                    "status": "success",
                    "message": "Login successful",
                    "data": {
                        "accessToken": str(refresh.access_token),
                        "user": UserSerializer(user).data
                    }
                })
            return Response({
                "status": "Bad request",
                "message": "Authentication failed"
            }, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'userId'

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance == request.user or instance.organisations.filter(users=request.user).exists():
            serializer = self.get_serializer(instance)
            return Response({
                "status": "success",
                "message": "User details retrieved successfully",
                "data": serializer.data
            })
        return Response({"message": "You don't have permission to view this user"}, status=status.HTTP_403_FORBIDDEN)

class OrganisationListView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrganisationSerializer

    def get_queryset(self):
        return self.request.user.organisations.all()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "status": "success",
            "message": "Organisations retrieved successfully",
            "data": {
                "organisations": serializer.data
            }
        })

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            org = serializer.save()
            org.users.add(request.user)
            return Response({
                "status": "success",
                "message": "Organisation created successfully",
                "data": OrganisationSerializer(org).data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "status": "Bad Request",
            "message": "Client error",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class OrganisationDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Organisation.objects.all()
    serializer_class = OrganisationSerializer
    lookup_field = 'orgId'

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user in instance.users.all():
            serializer = self.get_serializer(instance)
            return Response({
                "status": "success",
                "message": "Organisation details retrieved successfully",
                "data": serializer.data
            })
        return Response({"message": "You don't have permission to view this organisation"}, status=status.HTTP_403_FORBIDDEN)

class AddUserToOrganisationView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def post(self, request, orgId, *args, **kwargs):
        try:
            org = Organisation.objects.get(orgId=orgId)
            if request.user in org.users.all():
                user_id = request.data.get('userId')
                try:
                    user = User.objects.get(userId=user_id)
                    org.users.add(user)
                    return Response({
                        "status": "success",
                        "message": "User added to organisation successfully"
                    })
                except User.DoesNotExist:
                    return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)
            return Response({"message": "You don't have permission to add users to this organisation"}, status=status.HTTP_403_FORBIDDEN)
        except Organisation.DoesNotExist:
            return Response({"message": "Organisation not found"}, status=status.HTTP_404_NOT_FOUND)
