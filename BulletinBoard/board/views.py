from datetime import datetime
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404, render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from .filters import ReplyFilter
from .models import Post, Reply, Categories, Author
from django.contrib.auth.models import User
from .forms import PostForm, ReplyForm
from .tasks import send_email_through_celery


class PostsList(ListView):
    model = Post
    ordering = '-time_created'
    template_name = 'posts.html'
    context_object_name = 'posts'
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['time_now'] = datetime.utcnow()
        return context


class PostDetail(LoginRequiredMixin, DetailView):
    model = Post
    template_name = 'post.html'
    context_object_name = 'post'


class PostCreate(LoginRequiredMixin, CreateView):
    form_class = PostForm
    model = Post
    template_name = 'post_create.html'

    def form_valid(self, form):
        print(self.request.user.pk)
        post = form.save(commit=False)
        post.author = Author.objects.filter(user__pk=self.request.user.pk)[0]
        print(User.objects.filter(pk=self.request.user.pk)[0])
        return super().form_valid(form)


class PostUpdate(LoginRequiredMixin, UpdateView):
    form_class = PostForm
    model = Post
    template_name = 'post_create.html'


class PostDelete(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('posts')


class ReplyCreate(LoginRequiredMixin, CreateView):
    form_class = ReplyForm
    model = Reply
    template_name = 'reply_create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(*kwargs)
        pk = self.request.path.split('/')[-3]
        post = Post.objects.get(pk=pk)
        context['post_author'] = post.author
        context['post_title'] = post.title
        return context

    def form_valid(self, form):
        reply = form.save(commit=False)
        if self.request.method == 'POST':
            pk = self.request.path.split('/')[-3]
            sender = self.request.user
            reply.post = Post.objects.get(id=pk)
            reply.sender = User.objects.get(username=sender)
        reply.save()
        return super().form_valid(form)

    def get_success_url(self):
        url = '/post/'.join(self.request.path.split('/')[0:-2])
        return url


class ReplyDelete(LoginRequiredMixin, DeleteView):
    model = Reply
    template_name = 'reply_delete.html'
    success_url = reverse_lazy('my_replies')


class Replies(ListView, LoginRequiredMixin):
    model = Reply
    template_name = 'my_replies.html'
    context_object_name = 'replies'
    ordering = '-date_created'

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = ReplyFilter(self.request.GET, queryset)
        # return queryset.filter(post__author_id=self.request.user.id)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        return context


# ничего не работает
class CategoryList(ListView):
    model = Categories
    template_name = 'categories.html'
    context_object_name = 'category_list'

    def get_queryset(self):
        self.categories = get_object_or_404(Categories, id=self.kwargs['pk'])
        queryset = Post.objects.filter(category=self.categories).order_by('-time_created')
        return queryset


@login_required
def confirm_reply(request, reply_id):
    reply = Reply.objects.get(pk=reply_id)
    reply.confirmed = True
    reply.save()
    send_email_through_celery(reply_id)  # .delay(reply_id)
    return redirect('/')


def logout_user(request):
    logout(request)
    return redirect('/')
