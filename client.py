import asyncio

class ChatClient:
    def __init__(self):
        self.reader = None
        self.writer = None

    async def connect(self, host, port):
        self.reader, self.writer = await asyncio.open_connection(host, port)

    async def send_message(self, message):
        self.writer.write(message.encode())
        await self.writer.drain()

    async def receive_messages(self):
        try:
            while True:
                data = await self.reader.read(100)
                print(data.decode())
        except asyncio.IncompleteReadError:
            pass

async def main():
    chat_client = ChatClient()
    await chat_client.connect('127.0.0.1', 8888)

    # Ввод комнаты (пример: /join room1)
    room_command = input("Enter room command: ")
    await chat_client.send_message(room_command)

    # Асинхронно запускаем прослушивание сообщений от сервера
    asyncio.create_task(chat_client.receive_messages())

    try:
        while True:
            message = input("Enter message: ")
            await chat_client.send_message(message)
    except KeyboardInterrupt:
        pass
    finally:
        chat_client.writer.close()
        await chat_client.writer.wait_closed()

if __name__ == '__main__':
    asyncio.run(main())
