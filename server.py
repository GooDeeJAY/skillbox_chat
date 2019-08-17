#  Created by Artem Manchenkov, edited by Jasur Yusupov

from twisted.internet import reactor
from twisted.protocols.basic import LineOnlyReceiver
from twisted.internet.protocol import ServerFactory, connectionDone

class Client(LineOnlyReceiver):
    delimiter = "\n".encode()
    factory: 'Server'
    ip: str
    port: int
    login: str = None

    @property
    def step(self):
        return self.factory.step[self]

    def set_step(self, new_value: str = None):
        self.factory.step[self] = new_value

    def connectionMade(self):
        self.ip = self.transport.getPeer().host
        self.port = self.transport.getPeer().port
        self.factory.clients.append(self)
        self.factory.step[self] = "new_user"

        intro = """----- Welcome to the chat! -----\n
        · Be polite to others
        · Do not spam!\n"""
        self.send(intro)
        print(f"Client {self.ip} connected through port {self.port}")

    def connectionLost(self, reason=connectionDone):
        if self.login:
            self.factory.notify_all_users(f"{self.login} left the chat".center(45, "-"))
        self.factory.clients.remove(self)
        print(f"Client {self.ip}({self.login}) disconnected")

    def lineReceived(self, line: bytes):
        message = line.decode()

        if self.step == 'new_user':

            if message in [i.login for i in self.factory.clients]:
                self.send("This login is already owned, try another one!\nYour login:")
                return

            self.login = message

            if self.factory.messages:
                self.set_step("history_agreement")
                self.send(f"There are {len(self.factory.messages)} messages sent in chat before you joined, do you want to get them? (y/n)")
            else:
                notification = f"{self.login} joined the chat".center(45, "-")
                self.factory.notify_all_users(notification)
                self.set_step("chatting")

        elif self.step == 'history_agreement':
            response = message.lower()
            if response in ['y', 'yes']:
                self.set_step("msgs_number")
                self.send('Enter in numbers, how many messages you want to get:')

            elif response in ['n', 'no']:
                self.set_step("chatting")
                self.send("Ok")
                notification = f"{self.login} joined the chat".center(45, "-")
                self.factory.notify_all_users(notification)

        elif self.step == "msgs_number":
            if message.isnumeric():
                msg_count = len(self.factory.messages)

                if int(message) <= msg_count:
                    self.set_step("chatting")
                    x = msg_count - int(message)
                    for msg in self.factory.messages[x:]:
                        self.send(msg)

                    notification = f"{self.login} joined the chat".center(45, "-")
                    self.factory.notify_all_users(notification)
                else:
                    self.send(f"Number should be less than {msg_count+1}")
            else:
                self.send("Enter numbers only!!")
        else:
            format_message = f"{self.login}: {message}"
            self.factory.notify_all_users(format_message)
            print(format_message)

            if message == "/stats":
                info = f"""------ Chat stats: ------\n
                Users: {len(self.factory.clients)}
                Messages: {len(self.factory.messages)}\n"""
                self.factory.notify_all_users(info)

    def send(self, line):
        return self.sendLine(line.encode())

class Server(ServerFactory):
    clients: list
    messages: list
    step = dict
    protocol = Client

    def __init__(self):
        self.clients = []
        self.messages = []
        self.step = dict()
        print("Server started - OK")

    def startFactory(self):
        print("Start listening ...")

    def notify_all_users(self, message: str):
        self.messages.append(message)
        data = message.encode()
        for user in self.clients:
            user.sendLine(data)

if __name__ == '__main__':
    reactor.listenTCP(7410, Server())
    reactor.run()
