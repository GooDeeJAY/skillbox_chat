#  Created by Artem Manchenkov, edited by Jasur Yusupov

from twisted.internet import reactor, stdio
from twisted.internet.protocol import Protocol, ClientFactory

class MessageHandler(Protocol):
    output = None

    def dataReceived(self, data: bytes):
        if self.output:
            self.output.write(data)

class User(MessageHandler):
    factory: 'Connector'

    def wrap(self):
        handler = MessageHandler()
        handler.output = self.transport
        wrapper = stdio.StandardIO(handler)
        self.output = wrapper

    def connectionMade(self):
        self.send_message(self.factory.login)
        self.wrap()

    def send_message(self, content: str):
        self.transport.write(f"{content}\n".encode())


class Connector(ClientFactory):
    protocol = User
    login: str

    def __init__(self, login: str):
        self.login = login

    def startedConnecting(self, connector):
        print("Connecting to the server...")

    def clientConnectionFailed(self, connector, reason):
        print("Connection failed")
        reactor.callFromThread(reactor.stop)

    def clientConnectionLost(self, connector, reason):
        print("Disconnected from the server")
        reactor.callFromThread(reactor.stop)


if __name__ == '__main__':
    user_login = input("Your login: ")
    reactor.connectTCP("localhost", 7410, Connector(user_login))
    reactor.run()
