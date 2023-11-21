import asyncio
import websockets

class ChatServer:
    def __init__(self):
        self.clients = set()
        self.rooms = {}  # Комнаты и их участники
        self.message_history = {}  # История сообщений

    async def handle_client(self, websocket, path):
        self.clients.add(websocket)

        try:
            while True:
                message = await websocket.recv()
                if message.startswith('/join'):
                    room_name = message.split(' ')[1]
                    self.join_room(websocket, room_name)
                    await self.send_history(websocket, room_name)
                else:
                    await self.broadcast(websocket, message)
        except websockets.exceptions.ConnectionClosedError:
            pass
        finally:
            # Удаление клиента при отключении
            self.clients.remove(websocket)
            for room, members in self.rooms.items():
                members.discard(websocket)

    async def broadcast(self, sender, message):
        # Отправка сообщения всем участникам комнаты
        for room, members in self.rooms.items():
            if sender in members:
                for member in members:
                    try:
                        await member.send(message)
                        self.message_history.setdefault(room, []).append(message)
                    except:
                        continue

    async def send_history(self, client, room_name):
        # Отправка истории сообщений новому участнику комнаты
        history = self.message_history.get(room_name, [])
        for message in history:
            await client.send(message)

    def join_room(self, client, room_name):
        # Создание комнаты, если ее нет
        if room_name not in self.rooms:
            self.rooms[room_name] = set()

        # Добавление клиента в комнату
        for room, members in self.rooms.items():
            if client in members:
                members.discard(client)
        self.rooms[room_name].add(client)

async def main():
    chat_server = ChatServer()

    async with websockets.serve(
        chat_server.handle_client, '192.168.1.105', 8888
    ):
        await asyncio.Future()  # Ждем завершения

if __name__ == '__main__':
    asyncio.run(main())
