from datetime import datetime, timezone
from flask import Flask, render_template, session, redirect, url_for, flash, request  # CHANGED: added request
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField
from wtforms.validators import DataRequired, Email

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'

bootstrap = Bootstrap(app)
moment = Moment(app)


class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    email = EmailField('What is your UofT Email address?',
                       validators=[DataRequired(), Email()])
    submit = SubmitField('Submit')


@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        old_name = session.get('name')
        if old_name is not None and old_name != form.name.data:
            flash('Looks like you have changed your name!')
        old_email = session.get('email')
        if old_email is not None and old_email != form.email.data:
            flash('Looks like you have changed your email!')
        session['name'] = form.name.data
        session['email'] = form.email.data
        if 'utoronto' in form.email.data:              # NEW: valid UofT email → go to chat
            return redirect(url_for('chat_page'))
        return redirect(url_for('index'))
    return render_template('index.html', form=form,
                           name=session.get('name'),
                           email=session.get('email'))


# NEW: show the chat page
@app.route('/chat', methods=['GET'])
def chat_page():
    email = session.get('email')
    if not email or 'utoronto' not in email:
        return redirect(url_for('index'))
    return render_template('chat.html', name=session.get('name'))


# NEW: chatbot endpoint (starter code + memory)
@app.route('/chat', methods=['POST'])
def chat():
    message = request.json['message']
    lower = message.lower()

    if 'my name is' in lower:
        start = lower.index('my name is') + len('my name is')
        chat_name = message[start:].strip().rstrip('.!')
        session['chat_name'] = chat_name                # remember it
        reply = f"Nice to meet you, {chat_name}!"
    elif 'what is my name' in lower:
        chat_name = session.get('chat_name')            # recall it
        if chat_name:
            reply = f"Your name is {chat_name}."
        else:
            reply = "I don't know your name yet."
    elif 'hello' in lower:
        reply = "Hello!"
    else:
        reply = "I don't understand."

    return {"reply": reply}


# NEW: logout clears memory and goes home
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500