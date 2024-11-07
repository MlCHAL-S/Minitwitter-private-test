"""
Module for Client
"""

import grpc
from .. import minitwitter_pb2, minitwitter_pb2_grpc

def run() -> None:
    """
    Run the client application.

    This function establishes a gRPC channel, listens for user input, and processes
    commands to send or retrieve messages or exit the client application.
    """
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = minitwitter_pb2_grpc.MiniTwitterStub(channel)

        while True:
            command = input('Enter command (SEND <message>, GET <num_of_messages> or EXIT): ')

            if command.startswith("SEND "):
                message_text: str = command[5:]
                response: minitwitter_pb2.MessageResponse = stub.sendMessage(
                    minitwitter_pb2.MessageRequest(
                        message=message_text)
                    )
                print(response.status)

            elif command.startswith("GET "):
                try:
                    count: int = int(command[4:])
                    response: minitwitter_pb2.MessageListResponse = stub.getMessages(
                        minitwitter_pb2.MessageListRequest(
                            count=count)
                        )
                    print('Last messages:')
                    for msg in response.messages:
                        print(f'- {msg}')
                except ValueError:
                    print('Invalid count. Please enter an integer.')
            elif command == 'EXIT':
                print('Exiting...')
                break
            else:
                print('Invalid command. Use SEND <message>, GET <num_of_messages> or EXIT.')

if __name__ == "__main__":
    run()
