import os
from datetime import datetime, timedelta

from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from BulletinBoard.settings import SITE_URL

from .models import Reply, Post, Author, Categories


@shared_task
def send_email_through_celery(pk) -> None:
    reply = Reply.objects.get(pk=pk)
    if not reply.confirmed:
        user = Author.objects.filter(user__username=reply.post.author).values('user__username', 'user__email')
        username = user[0]['user__username']
        email = user[0]['user__email']
        html_content = render_to_string(
            'post_created.html',
            {
                'link': f'{SITE_URL}/my_replies/',
                'sender': reply.sender,
                'text': reply.text,
            }
        )
        sbj = "Новый отклик"
    else:
        user = Reply.objects.filter(sender__username=reply.sender).values('sender__username', 'sender__email')
        username = user[0]['sender__username']
        email = user[0]['sender__email']
        html_content = render_to_string(
            'reply_accepted.html',
            {
                'link': f'{SITE_URL}/post/{reply.post.pk}/',
                'user': reply.post.author,
            }
        )
        sbj = "Ответ на отклик"

    msg = EmailMultiAlternatives(
        subject=sbj,
        body=f"Здравствуй, {username}. {sbj} от {reply.sender}!",
        from_email=os.getenv('EMAIL'),
        to=[email],
    )
    msg.attach_alternative(html_content, "text/html")
    print(f"sending e-mail to {email}")
    msg.send()

# Заготовка под рассылку новостей, но пока из задания непонятно, что за рассылка, какой формат и пр.
@shared_task
def send_weekly_news():
    users = []
    last_week = datetime.now() - timedelta(days=7)
    posts = Post.objects.filter(creation_time__gte=last_week)
    categories = set(posts.values_list('category__name', flat=True))
    for category in categories:
        users += Categories.objects.filter(category=category).values_list(
            'subscribers__username',
            'subscribers__email'
        )
    html_content = render_to_string(
        'posts_last_week.html',
        {
            'link': f'{SITE_URL}',
            'posts': posts,
        }
    )
    for user in set(users):
        user_name, user_email = user
        if user_name:
            msg = EmailMultiAlternatives(
                subject=f"Здравствуй, {user_name}.",
                body='',
                from_email=os.getenv('EMAIL'),
                to=[user_email],
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
