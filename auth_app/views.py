from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import User, Organisation
from .serializers import UserSerializer, OrganisationSerializer, UserLoginSerializer

class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
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

class LoginView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
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

class UserDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, id):
        try:
            user = User.objects.get(userId=id)
            if user == request.user or user.organisations.filter(users=request.user).exists():
                return Response({
                    "status": "success",
                    "message": "User details retrieved successfully",
                    "data": UserSerializer(user).data
                })
            return Response({"message": "You don't have permission to view this user"}, status=status.HTTP_403_FORBIDDEN)
        except User.DoesNotExist:
            return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

class OrganisationListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        organisations = request.user.organisations.all()
        return Response({
            "status": "success",
            "message": "Organisations retrieved successfully",
            "data": {
                "organisations": OrganisationSerializer(organisations, many=True).data
            }
        })

    def post(self, request):
        serializer = OrganisationSerializer(data=request.data)
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

class OrganisationDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, orgId):
        try:
            org = Organisation.objects.get(orgId=orgId)
            if request.user in org.users.all():
                return Response({
                    "status": "success",
                    "message": "Organisation details retrieved successfully",
                    "data": OrganisationSerializer(org).data
                })
            return Response({"message": "You don't have permission to view this organisation"}, status=status.HTTP_403_FORBIDDEN)
        except Organisation.DoesNotExist:
            return Response({"message": "Organisation not found"}, status=status.HTTP_404_NOT_FOUND)

class AddUserToOrganisationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, orgId):
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