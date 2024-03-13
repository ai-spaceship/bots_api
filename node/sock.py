import socketio
from utils.prisma import prisma

# Create a Socket.IO server
sio = socketio.AsyncServer(cors_allowed_origins=[], async_mode='asgi')
sio_app = socketio.ASGIApp(sio)

# Define a handler for the 'connect' event
@sio.event
async def connect(sid, environ, auth):
    data = await prisma.user.find_many()
    result = []
    for i in data:
        result.append(i.json())
    await sio.emit( {'data': result})

# Define a handler for the 'message' event
@sio.event
async def message(sid, data):
    print(f'Received message from {sid}: {data}')
    await sio.emit('message', data)

# Define a handler for the 'disconnect' event
@sio.event
async def disconnect(sid):
    print(f'Client {sid} disconnected')

@sio.on('bot agent')
async def on_message(sid, username):
    print(username)
    info = await prisma.user.find_first(
        where={
            "bot_username" : username
        }
        
    )
    if info:
        await sio.emit(info.json())
        return
    await sio.emit([])

# Run the server

    
