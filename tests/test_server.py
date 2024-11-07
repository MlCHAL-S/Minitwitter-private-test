"""
Unit Testing module for MiniTwitterServicer Class and Smoke Test for serve function.
"""

from unittest import mock
import pytest
from src import minitwitter_pb2
from src.server.server import MiniTwitterServicer, messages, serve

@pytest.fixture
def servicer() -> MiniTwitterServicer:
    """
    This fixture creates a new MiniTwitterServicer instance
    and clears the message list before each test.

    Returns:
        MiniTwitterServicer: An instance of the servicer class.
    """
    messages.clear()
    return MiniTwitterServicer()

def test_send_message_success(servicer: MiniTwitterServicer) -> None:
    """
    This should test the successful sending of a message.
    It ensures that the message is stored and the correct response is returned.

    It verifies that the message list is updated and the correct status is returned.
    """
    request = minitwitter_pb2.MessageRequest(message='Hello, world!')
    response = servicer.sendMessage(request, None)
    assert response.status == 'Message sent successfully'
    assert messages == ['Hello, world!']

def test_send_empty_message(servicer: MiniTwitterServicer) -> None:
    """
    This should test sending an empty message.
    It ensures that empty messages are accepted and handled correctly.

    It verifies that an empty message can be added to the messages list.
    """
    request = minitwitter_pb2.MessageRequest(message="")
    response = servicer.sendMessage(request, None)
    assert response.status == 'Message sent successfully'
    assert messages == [""]

def test_get_messages_success(servicer: MiniTwitterServicer) -> None:
    """
    This should test retrieving messages successfully.
    It verifies that the correct number of messages are returned in the response.
    """
    servicer.sendMessage(minitwitter_pb2.MessageRequest(message='Message 1'), None)
    servicer.sendMessage(minitwitter_pb2.MessageRequest(message='Message 2'), None)
    servicer.sendMessage(minitwitter_pb2.MessageRequest(message='Message 3'), None)

    request = minitwitter_pb2.MessageListRequest(count=2)
    response = servicer.getMessages(request, None)
    assert response.status == 'Messages retrieved successfully'
    assert response.messages == ['Message 2', 'Message 3']

def test_get_more_messages_than_available(servicer: MiniTwitterServicer) -> None:
    """
    This should test retrieving more messages than are available.
    It ensures the server correctly returns all available messages, even if more are requested.
    """
    servicer.sendMessage(minitwitter_pb2.MessageRequest(message="Only message"), None)

    request = minitwitter_pb2.MessageListRequest(count=5)
    response = servicer.getMessages(request, None)
    assert response.status == 'Messages retrieved successfully'
    assert response.messages == ['Only message']

def test_get_zero_messages(servicer: MiniTwitterServicer) -> None:
    """
    This should test the behavior when the count is 0.
    It checks that the response is empty but successful when requesting zero messages.
    """
    request = minitwitter_pb2.MessageListRequest(count=0)
    response = servicer.getMessages(request, None)
    assert response.status == 'Messages retrieved successfully'
    assert response.messages == []

def test_get_messages_no_messages_in_storage(servicer: MiniTwitterServicer) -> None:
    """
    This should test the behavior when there are no messages stored.
    It verifies that the server returns an empty list
    with a success status when no messages are available.
    """
    request = minitwitter_pb2.MessageListRequest(count=2)
    response = servicer.getMessages(request, None)
    assert response.status == 'Messages retrieved successfully'
    assert response.messages == []

def test_serve_starts_grpc_server() -> None:
    """
    This should test if the gRPC server starts correctly.
    It ensures the server is configured and starts properly.

    It mocks grpc.server to prevent the actual server from starting during testing.
    """
    with mock.patch('grpc.server') as mock_grpc_server:
        mock_server_instance = mock.Mock()
        mock_grpc_server.return_value = mock_server_instance
        serve()
        mock_grpc_server.assert_called_once()
        mock_server_instance.add_insecure_port.assert_called_once_with('[::]:50051')
        mock_server_instance.start.assert_called_once()
        mock_server_instance.wait_for_termination.assert_called_once()
