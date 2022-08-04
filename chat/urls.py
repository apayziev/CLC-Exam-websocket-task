from django.urls import path
from chat import views


urlpatterns = [
    path("chat-list/",views.ChatListView.as_view()),
    path("chat/create/",views.ChatCreateView.as_view()),
    path("chat/<int:pk>/message/create/",views.MessageCreateView.as_view()),
    path("chat/<int:chat_id>/message-list/",views.ChatMessageListView.as_view()),
    path("chat/<int:chat_id>/message/<int:message_id>/delete/",views.ChatMessageDeleteView.as_view()),

]