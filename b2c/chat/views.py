from django.shortcuts import render
# Create your views here.
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Message
from .serializers import MessageSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from accounts .permissions import IsAdminUser

#  Buyer sends a message
class SendMessageView(generics.CreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)


#  Admin views all messages (or Buyer views their own)
class MessageListView(generics.ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:  #  Admin sees all
            return Message.objects.all().order_by('-timestamp')
        else:  #  Buyer sees only their messages
            return Message.objects.filter(sender=user).order_by('-timestamp')

#  Admin marks a message as read


class MarkMessageReadView(generics.UpdateAPIView):
    serializer_class = MessageSerializer
    queryset = Message.objects.all()
    permission_classes = [IsAdminUser]  # Admin users can mark messages as read
    
    def perform_update(self, serializer):
        # Mark the message as read and save it
        message = serializer.save(is_read=True)
        
        # Optionally, you can add any additional logic here if needed
        return Response({'status': 'marked as read'})




# class MarkMessageReadView(APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def patch(self, request, pk):
#         try:
#             message = Message.objects.get(id=pk, receiver=request.user)  # Ensure the message belongs to the authenticated user
#             message.is_read = True
#             message.save()
#             return Response(MessageSerializer(message).data, status=status.HTTP_200_OK)
#         except Message.DoesNotExist:
#             return Response({'detail': 'Message not found.'}, status=status.HTTP_404_NOT_FOUND)
