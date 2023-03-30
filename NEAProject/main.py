from website import create_app, quizSection
from flask import session
from flask_socketio import join_room, leave_room,send,SocketIO

rooms = quizSection.rooms # rooms dictionary is imported from different file as it is a global variable

app = create_app()
socketio = SocketIO(app)

@socketio.on("message") 
#This line sets up a Socket.IO event listener that listens for the "message" event,
#which is emitted by the client when a user sends a message
def message(data):
    room = session.get("room")
    if room not in rooms:
        return 
    
    content = {
        "name": session.get("name"),#Gets the messages sent by a user and adds to the rooms dictionary
        "message": data["data"]
    }
    send(content, to=room)
    rooms[room]["messages"].append(content)

@socketio.on("connect")
def connect(auth):
    room = session.get("room")
    name = session.get("name")
    if not room or not name: #session is checked to see whether there is any session data 
        return
    if room not in rooms: #if session data exists a quiz is not ongoing with room code specified
        leave_room(room)  #then user is removed from the quiz room
        return
    
    join_room(room) # if requirements are met then the user is added to the quiz room
    send({"name": name, "message": "has entered the room"}, to=room)
    rooms[room]["members"] += 1

@socketio.on("disconnect")
def disconnect():
    room = session.get("room")
    name = session.get("name")
    leave_room(room) #then user is removed from the quiz room when disconnected

    if room in rooms:
        rooms[room]["members"] -= 1
        if rooms[room]["members"] <= 0: #If there are no users in a quiz room then quiz room is deleted
            del rooms[room]
    
    send({"name": name, "message": "has left the room"}, to=room)

if __name__ == '__main__':
    socketio.run(app,debug=True) 

    
