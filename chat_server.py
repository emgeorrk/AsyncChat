import asyncio
import websockets

class ChatServer:
    def __init__(self):
        self.clients = set()
        self.rooms = {}  # Комнаты и их участники

    async def handle_client(self, websocket, path):
        self.clients.add(websocket)

        try:
            while True:
                message = await websocket.recv()
                if message.startswith('/auth'):
                    username, room_name = message.split(' ')[1:3]
                    self.join_room(websocket, username, room_name)
                elif message.startswith('/join'):
                    room_name = message.split(' ')[1]
                    self.join_room(websocket, None, room_name)
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
                    except:
                        continue

    def join_room(self, client, username, room_name):
        # Создание комнаты, если ее нет
        if room_name not in self.rooms:
            self.rooms[room_name] = set()

        # Добавление клиента в комнату
        for room, members in self.rooms.items():
            if client in members:
                members.discard(client)

        if username:
            self.rooms[room_name].add(client)
            # Отправляем уведомление о входе в комнату только текущему пользователю
            client.send(f"---Joined room: {room_name} as {username}---")
        else:
            self.rooms[room_name].add(client)

async def main():
    chat_server = ChatServer()

    async with websockets.serve(
        chat_server.handle_client, '192.168.1.105', 8888
    ):
        await asyncio.Future()  # Ждем завершения

if __name__ == '__main__':
    asyncio.run(main())
