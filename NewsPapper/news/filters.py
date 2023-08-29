from django_filters import FilterSet
from .models import Post, Author

class NewsFilter(FilterSet):

    class Meta:
        model = Post
        # fields = ('postDate', 'title', 'author')
        fields = {
            'postDate': ['icontains'],
            'title': ['icontains'],
            'author': ['exact'],
        }