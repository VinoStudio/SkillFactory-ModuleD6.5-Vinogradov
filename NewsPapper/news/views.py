from datetime import timedelta

from django.core.exceptions import PermissionDenied
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import render
from django.template.loader import render_to_string
from django.views.generic import ListView, DetailView, UpdateView, CreateView, DeleteView
from .models import Post, Category, Author
from django.views import View
from django.utils import timezone
from django.core.paginator import Paginator
from .filters import NewsFilter
from .forms import NewsForm
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, HttpResponseRedirect
from django.contrib.auth.models import Group
from decouple import config


class NewsList(ListView):
    model = Post
    template_name = 'posts/news.html'
    context_object_name = 'news'
    queryset = Post.objects.order_by('-id')
    ordering = ['-postDate']
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        return NewsFilter(self.request.GET, queryset=queryset).qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = NewsFilter(self.request.GET, queryset=self.get_queryset())
        context['choices'] = Post.CHOICES
        context['form'] = NewsForm
        context['author'] = not self.request.user.groups.filter(name='authors').exists()


        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
        return super().get(request, *args, **kwargs)


class CategoryList(ListView):
    model = Post
    template_name = 'posts/category_list.html'
    context_object_name = 'categories'
    queryset = Post.objects.order_by('-id')
    ordering = ['-postDate']
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.all().filter(postCategory__name=self.kwargs['name'])
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = Category.objects.get(name=self.kwargs['name'])
        context['subscribers'] = category.subscribers.all()
        context['category_name'] = category
        return context


def subscribe(request, name):
    category = Category.objects.get(name=name)
    user = request.user

    if not category.subscribers.filter(id=user.id).exists():
        category.subscribers.add(user)

        # html = render_to_string(
        #
        # )
    return redirect('news:posts')


    # category = Category.objects.get(pk=pk)
    # category.subscribers.add(request.user.id)
    # return HttpResponseRedirect(reverse('news:categories', args=[pk]))

def unsubscribe(request, name):
    category = Category.objects.get(name=name)
    user = request.user
    if category.subscribers.filter(id=user.id).exists():
        category.subscribers.remove(user)
    return redirect('news:posts')



@login_required
def become_author(request):
    user = request.user
    author = Group.objects.get(name='authors')
    if not request.user.groups.filter(name='authors').exists():
        author.user_set.add(user)
        Author.objects.create(userAuthor=user)
    return redirect('news:posts')


class NewsDetail(DetailView):
    model = Post
    template_name = 'posts/post.html'
    context_object_name = 'news_details'


class CreateNews(PermissionRequiredMixin, UserPassesTestMixin, LoginRequiredMixin, CreateView):

    template_name = 'posts/adds/add.html'
    form_class = NewsForm
    permission_required = ('news.add_post')

    def test_func(self):
        author = Author.objects.get(userAuthor_id=self.request.user.id)
        yesterday = timezone.now() - timedelta(days=1)
        per_day = Post.objects.filter(author=author,  postDate__gt=yesterday).count()
        if per_day > 2:
            raise PermissionDenied("You've overcome the daily normal of the posts, come tomorrow")
        else:
            return redirect('news:posts')

    # def post(self, request, *args, **kwargs):
    #     if self.post_permission():
    #         form = self.form_class(request.POST)
    #
    #         self.object = form.save()
    #
    #         self.categories = self.object.postCategory.all()
    #
    #         for category in self.categories:
    #             for subscriber in category.subscribers.all():
    #
    #                 html_content = render_to_string(
    #                     'send_mail_subscribe_to_news.html',
    #                     {
    #                         'user': subscriber,
    #                         'post': self.object,
    #                     }
    #                 )
    #
    #                 msg = EmailMultiAlternatives(
    #                     subject=f'{self.object.title}',
    #                     body=self.object.text,
    #                     from_email=config('DEFAULT_FROM_EMAIL'),
    #                     to=[f'{subscriber.email}'],
    #                 )
    #                 msg.attach_alternative(html_content, "text/html")
    #                 msg.send()
    #                 return redirect('news:posts')

class UpdateNews(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    permission_required = ('news.change_post',)

    template_name = 'posts/adds/add.html'
    form_class = NewsForm

    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')
        return Post.objects.get(pk=id)


class DeleteNews(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = ('news.delete_post',)

    model = Post
    context_object_name = "delete_news"
    template_name = 'posts/adds/delete_post.html'
    queryset = Post.objects.all()
    form_class = NewsForm
    success_url = reverse_lazy('news:posts')

class SearchList(ListView):
    model = Post
    template_name = 'posts/adds/search.html'
    context_object_name = 'posts'
    queryset = Post.objects.order_by('-id')
    ordering = ['-postDate']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = NewsFilter(self.request.GET, queryset=self.get_queryset())

        return context


# class Posts(View):
#
#     def get(self, request):
#         posts = Post.objects.order_by('-postDate')
#         pag = Paginator(posts, 10)
#         posts = pag.get_page(request.GET.get('page', 1))
#
#         context = {
#             'posts': posts
#         }
#
#         return render(request, 'posts/news.html', context)