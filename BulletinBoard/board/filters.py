from django import forms
from django.db import models
from django_filters import FilterSet, DateTimeFilter

from .models import Reply


class ReplyFilter(FilterSet):
    class Meta:
        model = Reply
        fields = {
            'text': ['icontains'],
            'sender': ['in'],
            'date_created': ['gt'],
        }
        filter_overrides = {
            models.DateTimeField: {
                'filter_class': DateTimeFilter,
                'extra': lambda f: {
                    'widget': forms.TextInput(attrs={'type': 'date'}),
                },
            },
        }


# class CategoryFilter(FilterSet):
#     class Meta:
#         model = Post
#         fields = ['category']
