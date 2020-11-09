from flask import Flask, render_template, request
from flask_socketio import SocketIO, send, emit
from queue import Queue
import translate
# from flask_socketio import join_room, leave_room

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

users_online = {}
lang_queues = {}
languages = [None, "English", "Spanish", "French", "Chinese (Simplified)", "Arabic", "Chinese (Traditional)",
             "Portuguese", "Vietnamese", "German", "Japanese", "Russian", "Swahili", "Hindi",
             "Korean", "Filipino"]
for lang in languages:
    lang_queues[lang] = Queue()

class User:
    def __init__(self, sid: str, name: str, language: str):
        self.sid = sid
        self.name = name
        self.language = language
        self.translate_session = None
        self.partner = None
    def connect(self, part) -> None:
        self.partner = part
        part.partner = self
        ts = translate.Session(self.language)
        self.translate_session = ts
        part.translate_session = ts
        print(f"{self.name} CONNECTED TO {part.name}")
        emit("found", (self.name,self.language), room=part.sid)
    def search(self):
        temp = lang_queues[self.language].queue
        if not lang_queues[self.language].empty() and not temp[0] is self:
            u = lang_queues[self.language].get()
            self.connect(u)
            return u
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

@socketio.on("transcend")
def transcend(sid, msg):
    print("ASISFH")
    sender = users_online[sid]
    print(f"{sender.name} --> {sender.partner.name}: {msg}")
    newmsg = translate.translate(msg, translate.lang_codes[sender.language.lower()])
    emit("chat message", (sender.name, newmsg))
    emit("chat message", (sender.name, newmsg), room=sender.partner.sid)

@socketio.on("topic request")
def topic(sid):
    u = users_online[sid]
    top = u.translate_session.question()
    emit("receive topic", top)
    emit("receive topic", top, room=u.partner.sid)

@socketio.on("new user")
def new_user(sid, name, language):
    u = User(sid, name, language)
    users_online[sid] = u
    other = u.search()
    if not other:
        emit("loop search")
        lang_queues[language].put(u)
    else:
        emit("found", (other.name, other.language))
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
    other = users_online[sid].search()
    if other:
       emit("found", other.name)

if __name__ == '__main__':
    socketio.run(app)