from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
# Create your views here.
from django.db import models
from chat.models import Chat, Message
from common.models import User
from chat import serializers
from helpers.pagination import CustomPagination


class ChatListView(generics.ListAPIView):
    queryset = Chat.objects.all().annotate(
        last_message=Message.objects.filter(
            chat_id=models.OuterRef('id')).order_by('-created_at').values('text')[:1],
        last_message_date=Message.objects.filter(
            chat_id=models.OuterRef('id')).order_by('-created_at').values('created_at')[:1]
    )
    serializer_class = serializers.ChatListSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        return self.queryset.filter(members=self.request.user).annotate(
            # profile image
            profile_image=models.Case(
                models.When(is_group=True, then=models.F('avatar')),
                models.When(is_group=False, then=User.objects.exclude(
                    id=self.request.user.id).filter(chat__title=models.OuterRef('title')).values('avatar')[:1]),
                default=models.Value('None image'),
                output_field=models.CharField(),

            ),
            # profile title
            profile_title=models.Case(
                models.When(is_group=True, then=models.F('title')),
                models.When(is_group=False, then=User.objects.exclude(
                    id=self.request.user.id).filter(chat__title=models.OuterRef('title')).values('full_name')[:1]),
                default=models.Value('None image'),
                output_field=models.CharField(),

            ),
            is_unmuted=models.Case(
                models.When(unmuted=self.request.user, then=True),
                default= False,
                output_field=models.BooleanField()
            ),
            is_pinned=models.Case(
               models.When(pinned=self.request.user, then=1),
               default=0,
               output_field=models.IntegerField()
            ),
             unread_message_count=models.Count(
               models.Q(messages__read=self.request.user),
               output_field = models.IntegerField()
            ),

        ).order_by("-is_pinned").all()

class ChatCreateView(generics.CreateAPIView):
    queryset = Chat.objects.all()
    serializer_class = serializers.ChatCreateSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(members=self.request.user)


class MessageCreateView(generics.CreateAPIView):
    queryset = Message.objects.all()
    serializer_class = serializers.MessageCreateSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(from_user=self.request.user)


class ChatMessageListView(generics.ListAPIView):
    queryset = Message.objects.all()
    serializer_class = serializers.MessageCreateSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return self.queryset.filter(chat_id=self.kwargs['chat_id'])

    

class ChatMessageDeleteView(generics.DestroyAPIView):
    queryset = Message.objects.all()
    serializer_class = serializers.MessageCreateSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return self.queryset.filter(chat_id=self.kwargs['chat_id'])

    def get_object(self):
        return self.queryset.get(id=self.kwargs['message_id'])

    def perform_destroy(self, instance):
        instance.delete()