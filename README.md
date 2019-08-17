ДЗ | Messenger на Python 15-17 августа
github: https://github.com/manchenkoff/skillbox-chat

Added Features:
1. If the user enters a login which is already owned by another user in the chat, the server sends "try another login" message, but not closes the connection. This way is more comfortable for users)
2. If there are some messages sent in chat before the user has joined, the server asks for the user to send them or not. If the user accepts that he wants to receive a history of the chat, the server asks for a number of messages to be sent to the user
3. If user types /stats, the server sends the statistics of the server: users count, amount of messages that are sent in chat

