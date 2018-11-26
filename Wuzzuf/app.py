from flask import Flask, render_template, request, session, jsonify
from flask_socketio import SocketIO, emit
from chatterbot.trainers import ListTrainer
from chatterbot import ChatBot
import re
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

f = open('static/data3.txt', 'r', encoding='utf-8')
lines = f.readlines()
f.close()


questions = []
answers = []
for line in lines:
    temp = line.split(' +++$+++ ')
    questions.append(temp[0].replace('\n', ''))
    answers.append(temp[1].replace('\n', ''))


# cleaning text to be easy for using
def clean_text(text):
    text = text.lower()
    text = re.sub("'d", " would", text)
    text = re.sub("'s", " is", text)
    text = re.sub("'m", " am", text)
    text = re.sub("'re", " are", text)
    text = re.sub("'ll", " will", text)
    text = re.sub("'ve", " have", text)
    text = re.sub("won't", "will not", text)
    text = re.sub("let's", "lets", text)
    text = re.sub("n't", " not", text)
    text = re.sub('[-()\"*#/@;:<>{}\[\]+|~.?`,=\'!]', " ", text)
    re.sub(' +', ' ', text)
    text = re.sub(" lets ", " let's ", text)
    return text

clean_questions = []
for question in questions:
    clean_questions.append(clean_text(question))

# cleaning the answers
clean_answers = []
for answer in answers:
    clean_answers.append(clean_text(answer))

for i in range(len(clean_questions)):
    bot.train([clean_answers[i], clean_questions[i]])


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
