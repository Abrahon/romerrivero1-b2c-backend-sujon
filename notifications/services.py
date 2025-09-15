# # notifications/services.py
# from .models import Notification
# from asgiref.sync import async_to_sync
# from channels.layers import get_channel_layer
# from .serializers import NotificationSerializer

# def create_notification(user, notification_type, title, message, send_ws=True):
#     """
#     Create DB record and optionally push to websocket channel.
#     Returns Notification instance.
#     """
#     notif = Notification.objects.create(
#         user=user,
#         notification_type=notification_type,
#         title=title,
#         message=message,
#     )

#     if send_ws:
#         # serialize
#         payload = NotificationSerializer(notif).data
#         channel_layer = get_channel_layer()
#         group_name = f"notifications_user_{user.id}"   
#         async_to_sync(channel_layer.group_send)(
#             group_name,
#             {
#                 "type": "send_notification",  # maps to consumer.send_notification
#                 "payload": payload
#             }
#         )
#     return notif
