from flask import Flask, render_template, request, session, redirect, make_response
from flask_socketio import join_room, leave_room, send, SocketIO, emit
import random
from k import secret_key, admin_password
app = Flask(__name__)
app.config['SECRET_KEY'] = secret_key
socketio = SocketIO(app, cors_allowed_origins='*')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.cookies.get('username') is None:
        name = f"User{genetare_name_postfix()}"
    else:
        name = request.cookies.get('username')
    response = make_response(render_template('chat.html', name=session.get('username', name)))
    return response

@socketio.on('connect')
def handle_connect():
    print(f"connected: {request.sid}")
    #if name is None:
    #    name = f"User{genetare_name_postfix()}"
    #emit('name', {'name': name})

@socketio.on('message')
def handle_message(data):
    print(f"received message: {data}")
    data['message'] = data['message'].strip()

    if data['message'] == "":
        return

    if data['message'].startswith('/'):
        if data['message'].startswith('/name'):
            name = data['message'].split(' ')[1] + genetare_name_postfix()
            set_name(name)
        elif data['message'].startswith('/ban'):
            pass

        else:
            send({'name': 'Server', 'message': 'Command not found'})

        return
    
    if data['name'] == 'undefined' or data['name'] == "" or data['name'] == None:
        name = f"User{genetare_name_postfix()}"
        set_name(name)
        send({'name': name, 'message': data['message']})
        return

    data['message'] = message_filter(data['message'])
    
    if data['message'] == "":
        return

    send(data, broadcast=True)

def genetare_name_postfix():
    return f'{random.randint(1, 1000):04}'

def message_filter(message: str):
    message = message.replace('<', '&lt;').replace('>', '&gt;')
    #ensure ascii characters only
    message = ''.join([i if ord(i) < 128 else '' for i in message])
    return message

def set_name(name: str):
    name = name.strip()
    restricted_names = []
    with open('restricted_names.txt', 'r') as f:
        restricted_names = f.readlines()
    if name.lower() in restricted_names:
        send({'name': 'Server', 'message': 'This name is restricted'})
        return False
    if name.startswith('#') or name.startswith('@') or name.startswith('/'):
        send({'name': 'Server', 'message': 'Name cannot start with #, @ or /'})
        return False
    if len(name) > 20:
        send({'name': 'Server', 'message': 'Name cannot be longer than 20 characters'})
        return False
    if len(name) < 3:
        send({'name': 'Server', 'message': 'Name cannot be shorter than 3 characters'})
        return False
    else:
        name.replace('<', '&lt;').replace('>', '&gt;')
        emit('name', {'name': name})
        send({'name': 'Server', 'message': f'You are now known as {name}'})
        return True

if __name__ == "__main__":
    socketio.run(app)