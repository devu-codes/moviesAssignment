from djoser.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import serializers, pagination
from .models import *
from collections import OrderedDict
from rest_framework.response import Response
from collections import Counter

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """ Serializer for User Model CRUD """
    class Meta:
        model = get_user_model()
        fields = (
            'id','first_name','last_name','email', 'password')
        extra_kwargs = {
            'password': {'write_only': True}
            }

    def create(self, validated_data):
        """ cutom create to handle password """
        password = validated_data.pop('password', None)
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user
    

class UserListSerializer(serializers.ModelSerializer):
    """ Serializer for Listing Users """
    
    class Meta:
        model = get_user_model()
        fields = ('email','display_name','creation_time')
        
class UserRetrieveSerializer(serializers.ModelSerializer):
    """ Serializer for retrieving a User """
    
    class Meta:
        model = get_user_model()
        fields = ('email','description','creation_time')

class UserUpdateSerializer(serializers.ModelSerializer):
    """ Serializer for retrieving a User """
    
    class Meta:
        model = get_user_model()
        fields = ('email','first_name','last_name','display_name')
        
    def update(self, instance, validated_data):
        if instance.email != validated_data.get('email', instance.email):
            raise serializers.ValidationError({"non_field_error":"Email cannot be updated"})
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        return instance



class MovieSerializer(serializers.ModelSerializer):
    """ Serializer for User Model CRUD """
   
    class Meta:
        model = Movie
        fields = ('uuid','title','genre','description')  



class CollectionListSerializer(serializers.ModelSerializer):
   
    class Meta:
        model = Collection
        fields = ('uuid', 'title','description')   


class CollectionPagination(pagination.PageNumberPagination):
    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('is_success', self.get_is_success(
                self.page.paginator.object_list)),
            ('data', {
                "collections": data,
                "favourite_genres": self.get_fav_genres(
                self.page.paginator.object_list)
            }),
        ]))

    def get_is_success(self, queryset):
        return True if queryset.count()>0 else False
    
    def get_fav_genres(self, queryset):
        uuid = queryset[0].uuid
        movie_ids = MoviesCollection.objects.filter(collection__uuid=uuid).values_list('movie_id', flat=True)
        genres = ','.join(Movie.objects.filter(pk__in=movie_ids).values_list('genre', flat=True)).lower()
        genre_counts = Counter(genres.split(','))
        top_counts = dict(genre_counts.most_common(3))
        return top_counts if top_counts else None

    class Meta:
        serializer_class = CollectionListSerializer


class CollectionSerializer(serializers.ModelSerializer):
    movies = MovieSerializer(many=True)
   
    class Meta:
        model = Collection
        fields = ('uuid', 'title', 'description', 'movies','created_by')  
        extra_kwargs = {
            'created_by': {'write_only': True}
            } 
    
    def create(self, validated_data):
        movies_data = self.context['request'].data['movies']
        movies_data_pop = validated_data.pop('movies')
        collection = Collection.objects.create(**validated_data)
        for movie_data in movies_data:
            uuid = movie_data['uuid']
            movie, created = Movie.objects.get_or_create(uuid=uuid,defaults=movie_data)
            MoviesCollection.objects.get_or_create(collection=collection, movie=movie)
        return collection
    
    def update(self, instance, validated_data):
        movies_data = self.context['request'].data['movies']
        movies_data_pop = validated_data.pop('movies')

        instance.title = validated_data.get('title', instance.title)
        instance.created_by = validated_data.get('created_by', instance.created_by)
        instance.description = validated_data.get('description', instance.description)
        instance.save()

        # Update or create movies
        updated_movies = []
        for movie_data in movies_data:
            uuid = movie_data.get('uuid','')
            title = movie_data.get('title','')
            description = movie_data.get('description','')

            movie, created = Movie.objects.update_or_create(
                uuid=uuid,
                defaults={'title': title, 'description': description}
            )

            updated_movies.append(movie)
        instance.movies.set(updated_movies)
        return instance
