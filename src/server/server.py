"""
Module for Server
"""

from concurrent import futures
import grpc
from .. import minitwitter_pb2
from .. import minitwitter_pb2_grpc

messages: list[str] = []

class MiniTwitterServicer(minitwitter_pb2_grpc.MiniTwitterServicer):
    """
    gRPC Servicer class for handling MiniTwitter commands.
    """
    def sendMessage(
            self,
            request: minitwitter_pb2.MessageRequest,
            context
    ) -> minitwitter_pb2.MessageResponse:
        """
        Handles sending a message by appending it to the messages list.

        Args:
            request: The request containing the message to be sent.
            context: The gRPC context (unused here).

        Returns:
            A MessageResponse with a status message.
        """
        messages.append(request.message)
        return minitwitter_pb2.MessageResponse(status='Message sent successfully')

    def getMessages(
            self,
            request: minitwitter_pb2.MessageListRequest,
            context
    ) -> minitwitter_pb2.MessageListResponse:
        """
        Retrieves the most recent messages up to the specified count.

        Args:
            request: The request containing the count of messages to retrieve.
            context: The gRPC context (unused here).

        Returns:
            A MessageListResponse containing the messages.
        """
        recent_messages: list[str] = messages[-request.count:]
        return minitwitter_pb2.MessageListResponse(
            messages=recent_messages,
            status='Messages retrieved successfully'
        )



if __name__ == '__main__':
    pass
