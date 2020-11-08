from flask import Flask, render_template, request
from flask_socketio import SocketIO, send, emit
from uuid import uuid4
from queue import Queue
from flask_socketio import join_room, leave_room

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

users_online = {}
lang_queues = {}
languages = ["English", "Spanish", "French"]
for lang in languages:
    lang_queues[lang] = Queue()

class User:
    def __init__(self, sid: str, name: str, language: str):
        self.sid = sid
        self.name = name
        self.language = language
        self.partner = None
    def connect(self, part) -> None:
        self.partner = part
        part.partner = self
        print(f"{self.name} CONNECTED TO {part.name}")
        emit("found", room=part.sid)
    def search(self):
        temp = lang_queues[self.language].queue
        if not lang_queues[self.language].empty() and not temp[0] is self:
            u = lang_queues[self.language].get()
            self.connect(u)
            return True
        return False


@app.route('/')
def hello_world():
    return render_template("henrytest.html")

@app.route('/searching')
def searching():
    return render_template("searching.html")

@socketio.on("connect")
def on_connect():
    emit("SID", request.sid)

@socketio.on("chat message")
def handle_message(sid, msg):
    sender = users_online[sid]
    print(f"{sender.name} --> {sender.partner.name}: {msg}")
    emit("chat message", (sender.name, msg))
    emit("chat message", (sender.name, msg), room=sender.partner.sid)

@socketio.on("new user")
def new_user(sid, name, language):
    u = User(sid, name, language)
    users_online[sid] = u
    if not u.search():
        emit("loop search")
        lang_queues[language].put(u)
    else:
        emit("found")
    emit("user created", (sid, name, language))
    print(f"Welcome {name}, speaking {language}, ID: {sid}!")

from flask_socketio import join_room, leave_room

@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    join_room(room)
    send(username + ' has entered the room.', room=room)

@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    send(username + ' has left the room.', room=room)

@socketio.on("search")
def search(sid):
    if users_online[sid].search():
       emit("found")

if __name__ == '__main__':
    socketio.run(app)