from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, generics, parsers

from cosmetics import serializers
from cosmetics.models import *


def index(request):
    return HttpResponse("ScoreApp")


class UserViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.ListAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = serializers.UserSerializer
    parser_classes = [parsers.MultiPartParser]

