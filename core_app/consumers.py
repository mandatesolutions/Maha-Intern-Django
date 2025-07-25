from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.core.cache import cache
from .models import *
from .utils import get_room_name
import json

class ChatroomConsumer(WebsocketConsumer):
    def connect(self):
        self.sender = self.scope["user"]
        self.sender.name = f'{self.sender.first_name} {self.sender.last_name}'
        
        self.receiver_id = self.scope['url_route']['kwargs']['receiver_id']
        self.receiver = UserModel.objects.get(id=self.receiver_id)
        self.receiver.name = f'{self.receiver.first_name} {self.receiver.last_name}'
        
        self.room_name = get_room_name(self.sender.id, self.receiver.id)
        self.room_group_name = f"chat_{self.room_name}"

        async_to_sync(self.channel_layer.group_add)(self.room_group_name, self.channel_name)
        self.accept()

        messages = self.get_cached_messages()
        for msg in messages:
            self.send(text_data=json.dumps(msg))

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(self.room_group_name, self.channel_name)

    def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        sender = self.sender
        receiver = self.receiver

        self.save_message(sender, receiver, message)
        self.store_message_in_cache(sender, message)

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'user_id': sender.id,
                'name': sender.name
            }
        )

    def chat_message(self, event):
        self.send(text_data=json.dumps({
            'user_id': event['user_id'],
            'message': event['message'],
            'name': event['name'],
        }))

    def save_message(self, sender, receiver, message):
        ChatMessage.objects.create(
            sender=sender, receiver=receiver, message=message, room_name=self.room_name
        )

    def store_message_in_cache(self, user, message):
        key = f"maha_intern_chat_history_{self.room_name}"
        entry = {"user_id": user.id,"name":user.name, "message": message}
        history = cache.get(key, [])
        history.append(entry)
        history = history[-50:]
        cache.set(key, history, timeout=None)

    def get_cached_messages(self):
        key = f"maha_intern_chat_history_{self.room_name}"
        return cache.get(key, [])

        
        

        
    