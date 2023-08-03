from django.urls import path
from .views import *


urlpatterns = [
   path('', PostsList.as_view(), name='posts'),
   path('post/<int:pk>', PostDetail.as_view(), name='post_detail'),
   path('create/', PostCreate.as_view(), name='post_create'),
   path('<int:pk>/update/', PostUpdate.as_view(), name='post_update'),
   path('<int:pk>/delete/', PostDelete.as_view(), name='post_delete'),
   path('<int:pk>/reply/', ReplyCreate.as_view(), name='reply_create'),
   path('my_replies/', Replies.as_view(), name='my_replies'),
   path('my_replies/<int:pk>/delete', ReplyDelete.as_view(), name='reply_delete'),
   path('my_replies/confirm/<int:reply_id>', confirm_reply, name='reply_confirm'),
   # path('categories/<int:pk>/', CategoryList.as_view(), name='category_list'),
   path('logout/', logout_user, name='logout'),
]
