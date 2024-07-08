from django.urls import path
from .views import RegisterView, HomeApi, LoginView, UserDetailView, OrganisationListView, OrganisationDetailView, AddUserToOrganisationView

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('', HomeApi.as_view(), name='Home'),
    path('api/users/<str:userId>/', UserDetailView.as_view(), name='user_detail'),
    path('api/organisations/', OrganisationListView.as_view(), name='organisation_list'),
    path('api/organisations/<str:orgId>/', OrganisationDetailView.as_view(), name='organisation_detail'),
    path('api/organisations/<str:orgId>/add_user/', AddUserToOrganisationView.as_view(), name='add_user_to_org'),
]
