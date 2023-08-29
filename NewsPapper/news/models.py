from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum

class Author(models.Model):
    userAuthor = models.OneToOneField(User, on_delete=models.CASCADE)
    userRating = models.SmallIntegerField(default=0)

    def update_rating(self):
        postValue = self.post_set.all().aggregate(summ = Sum('postRating'))
        postRating = 0
        postRating += postValue.get('summ')

        commentValue = self.userAuthor.comment_set.all().aggregate(summ = Sum('rating'))
        commentRating = 0
        commentRating += commentValue.get('summ')

        self.userRating = postRating * 3 + commentRating
        self.save()

    def __str__(self):
        return f'User: {self.userAuthor}'

class Category(models.Model):
    name = models.CharField(max_length=64, unique=True)
    subscribers = models.ManyToManyField(User, through='CategorySubscriber')

    def __str__(self):
        return f'Категория: {self.name}'


class CategorySubscriber(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subscriber = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.category}"


class Post(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    NEWS = 'NW'
    ARTICLE = 'AR'
    CHOICES = (
        (NEWS, 'Новость'),
        (ARTICLE, 'Статья')
    )

    postType = models.CharField(max_length=2, choices=CHOICES, default=NEWS)
    postDate = models.DateTimeField(auto_now_add=True)
    postCategory = models.ManyToManyField(Category, through='PostCategory')
    title = models.CharField(max_length=128)
    text = models.TextField(max_length=500)
    postRating = models.SmallIntegerField(default=0)

    def like(self):
        self.postRating += 1
        self.save()

    def dislike(self):
        self.postRating -= 1
        self.save()

    def preview(self):
        return self.text[:125] + '...'

    def __str__(self):
        return f'Пост за авторством: {self.author.userAuthor}, жанром: {self.postType},' \
               f' с заголовком: {self.title} и содержанием: {self.preview()} '

    def get_absolute_url(self):
        return f'/news/{self.id}'

class PostCategory(models.Model):
    postInBetween = models.ForeignKey(Post, on_delete=models.CASCADE)
    categoryInBetween = models.ForeignKey(Category, on_delete=models.CASCADE)

class Comment(models.Model):
    commentPost = models.ForeignKey(Post, on_delete=models.CASCADE)
    commentUser = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    commentDate = models.DateTimeField(auto_now_add=True)
    rating = models.SmallIntegerField(default=0)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def __str__(self):
        return f'Комментарий "{self.text}", пользователя {self.commentUser}'
