"""
Unit Testing module for Client
"""

from unittest import mock
import pytest
from src import minitwitter_pb2
from src.client.client import run

@pytest.fixture
def mock_grpc_and_stub() -> tuple:
    """
    This fixture mocks the gRPC channel and the MiniTwitterStub.
    It yields the mock channel and stub instance for testing.

    Returns:
        tuple: Mocked gRPC channel and stub instance.
    """
    with mock.patch('grpc.insecure_channel') as mock_channel:
        with mock.patch('src.minitwitter_pb2_grpc.MiniTwitterStub') as mock_stub_class:
            # Mock the return value of the MiniTwitterStub
            mock_stub_instance = mock.Mock()
            mock_stub_class.return_value = mock_stub_instance
            yield mock_channel, mock_stub_instance

def test_exit_command() -> None:
    """
    This should test the EXIT command by simulating user input
    and ensuring the "Exiting..." message is printed.

    It mocks the input and verifies the output.
    """
    with mock.patch('builtins.input', side_effect=["EXIT"]):
        with mock.patch('builtins.print') as mock_print:
            run()  # Call the client code
            # Verify that "Exiting..." message is printed
            mock_print.assert_any_call("Exiting...")

def test_send_command(mock_grpc_and_stub: tuple) -> None:
    """
    This should test the SEND command by simulating user input,
    sending a message, and ensuring the correct response is printed.

    It verifies that the stub method sendMessage was called with the expected message.
    """
    mock_channel, mock_stub_instance = mock_grpc_and_stub
    mock_stub_instance.sendMessage.return_value = minitwitter_pb2.MessageResponse(
        status="Message sent successfully"
    )

    with mock.patch('builtins.input', side_effect=["SEND Hello, world!", "EXIT"]):
        with mock.patch('builtins.print') as mock_print:
            run()  # Call the client code

            mock_stub_instance.sendMessage.assert_called_once_with(
                minitwitter_pb2.MessageRequest(message='Hello, world!')
            )

            mock_print.assert_any_call('Message sent successfully')
            mock_print.assert_any_call('Exiting...')

def test_get_command(mock_grpc_and_stub: tuple) -> None:
    """
    This should test the GET command by simulating user input to request the last messages.
    It checks that the messages are printed correctly.

    It verifies that getMessages was called with the expected count and the messages are printed.
    """
    mock_channel, mock_stub_instance = mock_grpc_and_stub
    mock_stub_instance.getMessages.return_value = minitwitter_pb2.MessageListResponse(
        status='Last messages:',
        messages=['Message 1', 'Message 2', 'Message 3']
    )

    with mock.patch('builtins.input', side_effect=['GET 5', 'EXIT']):
        with mock.patch('builtins.print') as mock_print:
            run()  # Call the client code

            mock_stub_instance.getMessages.assert_called_once_with(
                minitwitter_pb2.MessageListRequest(count=5)
            )

            mock_print.assert_any_call('Last messages:')
            mock_print.assert_any_call('- Message 3')
            mock_print.assert_any_call('- Message 2')
            mock_print.assert_any_call('- Message 1')
            mock_print.assert_any_call('Exiting...')

def test_get_invalid_count() -> None:
    """
    This should test the GET command with an invalid count.
    It checks that the error message for invalid count is printed.

    It simulates a non-integer input for count.
    """
    with mock.patch('builtins.input', side_effect=['GET abc', 'EXIT']):
        with mock.patch('builtins.print') as mock_print:
            run()  # Call the client code
            mock_print.assert_any_call('Invalid count. Please enter an integer.')
            mock_print.assert_any_call('Exiting...')

def test_invalid_command() -> None:
    """
    This should test an invalid command.
    It checks that the appropriate error message for an invalid command is printed.

    It simulates an unrecognized command input.
    """
    with mock.patch('builtins.input', side_effect=['UNKNOWN', 'EXIT']):
        with mock.patch('builtins.print') as mock_print:
            run()  # Call the client code
            mock_print.assert_any_call(
                'Invalid command. Use SEND <message>, GET <num_of_messages> or EXIT.'
            )
            mock_print.assert_any_call('Exiting...')
