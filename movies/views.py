import os
import requests
from .models import *
from .serializers import *
from django.shortcuts import render
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, mixins, viewsets, permissions, filters
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from moviesCollection.settings import username, password
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from retry import retry
from rest_framework.mixins import ListModelMixin, CreateModelMixin, \
    UpdateModelMixin, DestroyModelMixin, RetrieveModelMixin

User = get_user_model()
# Create your views here.
@api_view(['GET'])
def samp(request):
    return Response({"view":"Sample view!!!"})


class UserViewset(
        viewsets.GenericViewSet):
    """ User viewset for CRUD """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter]    
    search_fields = ['email', 'first_name', 'last_name']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return UserListSerializer
        elif self.action == 'retrieve':
            return UserRetrieveSerializer
        elif self.action == 'update':
            return UserUpdateSerializer
        return UserSerializer
    
    # create a user
    def create(self, request):
        """
        :param request: A json string with the user details
        {
          "first_name" : "Samp",
          "last_name" : "Kumar",
          "email": "samp@gmail.com",
          "password" : "samp@123"
         }
        :return: A json string with the response {"id" : "<user_id>"}
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"id":(serializer.data)['id']}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # list all users
    def list(self, request, **kwargs):
        """
        :return: A json list with the response
        [
          {
            "email" : "<email>",
            "display_name" : "<first_name + last_name>",
            "creation_time" : "<some date:time format>"
          }
        ]
        """
        queryset = super().get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    # describe user
    def retrieve(self, request, pk, format=None):
        try: 
            user = super().get_queryset().get(pk=pk)
            serializer = self.get_serializer(user)
            return Response(serializer.data,status=status.HTTP_200_OK)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)
    
    # describe user
    @action(detail=False, methods=['post'])
    def describe_user(self, request, pk=None, **kwargs):
      """
        :param request: A json string with the user details
        {
          "id" : "<user_id>"
        }
        
        :return: A json string with the response
        {
          "email" : "<email>",
          "description" : "<some description>",
          "creation_time" : "<some date:time format>"
        }
        """
      try:
          id = (request.data)['id'] 
          user = super().get_queryset().get(id=id)
          serializer = UserRetrieveSerializer(user)
          return Response(serializer.data,status=status.HTTP_200_OK)
      except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)
    
    # update user
    def update(self,request,pk=None):   
        """
        :param request: A json string with the user details
        {
          "id" : "<user_id>",
          "user" : {
            "email" : "<email>",
            "display_name" : "<first_name +  last_name>"
          }
        }
        
        :return:
        Constraint:
            * email cannot be updated
            * name can be max 64 characters
            * display name can be max 128 characters
        """
        user = super().get_queryset().get(id=pk)
        serializer = self.get_serializer(user,data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ObtainJWTToken(APIView):
    authentication_classes = ()
    permission_classes = ()

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = authenticate(email=email, password=password)

        if user is not None:
            refresh = RefreshToken.for_user(user)

            return Response({'access_token': str(refresh.access_token), 'refresh_token': str(refresh)})
        else:
            return Response({'error': 'Invalid credentials'}, status=400)


class ProtectedView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        return Response({'message': f'Heyy, {user.email}!'})

from rest_framework.pagination import PageNumberPagination

class CollectionViewset(
          viewsets.GenericViewSet):
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer
    pagination_class = CollectionPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return super().get_queryset().filter(created_by=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list':
            return CollectionListSerializer
        return CollectionSerializer
    
    # create teams
    def create(self, request):
        data = request.data
        data.update({'created_by': request.user})
        serializer = self.get_serializer(data= data)
        if serializer.is_valid():
            serializer.save()
            return Response({"collection_uuid":(serializer.data).get("uuid",'')}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
       
    # list all collections
    def list(self, request, **kwargs):
        queryset = super().get_queryset().filter(created_by= self.request.user)
        paginator = CollectionPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = self.get_serializer(queryset, many=True)
        return paginator.get_paginated_response(serializer.data)

      
    # retrieve a collection
    def retrieve(self, request, pk=None, format=None):
        try: 
            team = super().get_queryset().get(pk=pk)
            serializer = self.get_serializer(team)
            return Response(serializer.data,status=status.HTTP_200_OK)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)
      
    # update a collection
    def update(self,request,pk=None):   
        collection = super().get_queryset().get(pk=pk)
        serializer = self.get_serializer(collection,data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, pk=None, **kwargs):
        collection = super().get_queryset().get(pk=pk)
        print("collection",collection)
        if not collection:
            return Response(status = status.HTTP_406_NOT_ACCEPTABLE)
        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

url = 'https://demo.credy.in/api/v1/maya/movies/'
@retry(tries=3, delay=1, backoff=2)
def make_request():
    session = requests.Session()
    retry_strategy = Retry(
        total=3,
        backoff_factor=2,
        status_forcelist=[429, 500, 502, 503, 504],
        method_whitelist=["HEAD", "GET", "OPTIONS"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    response = session.get(url, auth=(username, password))
    response.raise_for_status()
    return response

class MoviesViewset(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return None

    def list(self, request):
        try:
            response = make_request()
            if response.status_code == 200:
                data = response.json()
                print(data)
            else:
                print(f'Request failed with status code: {response.status_code}')
        except requests.exceptions.RequestException as err:
              print(f'An error occurred: {err}')   
        return Response(data)
            

@api_view(['GET'])
def get_request_count(request):
    counter = RequestCounter.objects.first()
    request_count = counter.count if counter else 0
    return Response({'requests': request_count})

@api_view(['GET'])
def reset_request_count(request):
    counter = RequestCounter.objects.first()
    if not counter:
        counter = RequestCounter()
    counter.count = 0
    counter.save()
    return Response({'message': 'Request count reset successfully'})

