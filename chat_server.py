import asyncio
import websockets

class ChatServer:
    def __init__(self):
        self.clients = set()
        self.rooms = {}  # Комнаты и их участники
        self.message_history = {}  # История сообщений для каждой комнаты

    async def handle_client(self, websocket, path):
        self.clients.add(websocket)

        try:
            while True:
                message = await websocket.recv()
                if message.startswith('/auth'):
                    await self.authenticate(websocket, message)
                elif message.startswith('/join'):
                    room_name = message.split(' ')[1]
                    await self.join_room(websocket, room_name)
                else:
                    await self.broadcast(websocket, message)
        except websockets.exceptions.ConnectionClosedError:
            pass
        finally:
            # Удаление клиента при отключении
            self.clients.remove(websocket)
            for room, members in self.rooms.items():
                members.discard(websocket)

    async def authenticate(self, client, message):
        # Аутентификация пользователя
        username = message.split(' ')[1]
        print(f"User {username} authenticated.")
        await client.send(f"Welcome, {username}!")

    async def broadcast(self, sender, message):
        # Отправка сообщения всем участникам комнаты
        for room, members in self.rooms.items():
            if sender in members:
                for member in members:
                    try:
                        await member.send(message)
                        # Сохранение сообщения в истории комнаты
                        self.message_history.setdefault(room, []).append(message)
                    except:
                        continue

    async def join_room(self, client, room_name):
        # Создание комнаты, если ее нет
        if room_name not in self.rooms:
            self.rooms[room_name] = set()

        # Добавление клиента в комнату
        for room, members in self.rooms.items():
            if client in members:
                members.discard(client)
        self.rooms[room_name].add(client)

        # Отправка истории сообщений комнаты новому участнику
        history = self.message_history.get(room_name, [])
        for message in history:
            await client.send(message)

async def main():
    chat_server = ChatServer()

    async with websockets.serve(
        chat_server.handle_client, '192.168.1.105', 8888
    ):
        await asyncio.Future()  # Ждем завершения

if __name__ == '__main__':
    asyncio.run(main())
