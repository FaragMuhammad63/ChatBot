from flask import Flask, render_template, request, session, jsonify
from flask_socketio import SocketIO, emit
from chatterbot.trainers import ListTrainer
from chatterbot import ChatBot

f = open('static/data.txt', 'r', encoding='utf-8')
lines = f.readlines()
f.close()

# data processing
dialog = []
for line in lines:
    dialog.append(line.replace('\n', ''))


bot = ChatBot("Chatty")
bot.set_trainer(ListTrainer)
bot.train(dialog)


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)


@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('question')
def send_response(question):
    answer = str(bot.get_response(question['data']))
    emit('response', {'data': answer})


if __name__ == '__main__':
    app.run()
