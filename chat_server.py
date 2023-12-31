import asyncio
import json

import websockets

class ChatServer:
    def __init__(self):
        self.clients = set()
        self.rooms = {}  # Комнаты и их участники
        self.message_history = {}  # История сообщений по комнатам

    async def handle_client(self, websocket, path):
        self.clients.add(websocket)

        try:
            while True:
                message = await websocket.recv()
                if message.startswith('/auth'):
                    username, room_name = message.split(' ')[1:3]
                    await self.join_room(websocket, username, room_name)
                elif message.startswith('/join'):
                    room_name = message.split(' ')[1]
                    await self.join_room(websocket, None, room_name)
                elif message.startswith('/leave'):
                    await self.broadcast(websocket, f'{username} left the room.', 'system')
                else:
                    await self.broadcast(websocket, message, username)
        except websockets.exceptions.ConnectionClosedError:
            pass
        finally:
            # Удаление клиента при отключении
            self.clients.remove(websocket)
            for room, members in self.rooms.items():
                members.discard(websocket)

    async def broadcast(self, sender, message, username):
        # Отправка сообщения всем участникам комнаты
        message_cont = {
            'username': username,
            'message': message
        }
        for room, members in self.rooms.items():
            if sender in members:
                for member in members:
                    try:
                        await member.send(json.dumps(message_cont))
                    except:
                        continue
                # Сохранение сообщения в истории
                self.message_history.setdefault(room, []).append(message_cont)

    async def join_room(self, client, username, room_name):
        # Создание комнаты, если ее нет
        if room_name not in self.rooms:
            self.rooms[room_name] = set()

        # Добавление клиента в комнату
        for room, members in self.rooms.items():
            if client in members:
                members.discard(client)

        if username:
            self.rooms[room_name].add(client)
            # Отправляем историю сообщений текущему пользователю
            if room_name in self.message_history:
                for message in self.message_history[room_name]:
                    await client.send(json.dumps(message))

            message_cont = {
                'username': 'system',
                'message': f'{username} joined the room.'
            }

            await self.broadcast(client, f'{username} joined the room.', 'system')

            # await client.send(json.dumps(message_cont))
            # self.message_history.setdefault(room, []).append(message_cont)
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
