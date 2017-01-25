#!../venv/bin/python2
#mmh, j'ai envie d'utiliser du coding: utf-8 - ouais, vendu !
#from __future__ import unicode_literals

########################################################
#    Premier module du serveur Maelström : theWall.    #
#    Jette un oeil au readme pour plus de détails.     #
#    Batoo, 2015.                                      #
########################################################


from gevent import monkey
monkey.patch_all()
from time import sleep
from threading import Thread
from flask import Flask, render_template, session, request, flash, redirect, url_for
from flask.ext.socketio import SocketIO, emit, disconnect

from flask.ext.wtf import Form
from wtforms import TextField, PasswordField
from wtforms.validators import Required, length


### VAR ###
#thread = None
#thread2 = None
fireflies = []
#roomName = u'Die_freien_Verrückten'
roomName = u'TheWall_First_Room'

### CONFIG SERVEUR ###
app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'Fools rush in where angels fear to tread.'
socketio = SocketIO(app)

### PARTIE SERVEUR ###
def fireflies_thread():
    """doesn't work currently"""
    size = len(fireflies)
    while True:
        sleep(5)
        newSize = len(fireflies)
        if newSize != size:
            print 'changes in fireflies'
            emit('update fireflies', {'fireflies': fireflies})
        size = newSize


def backup_thread():
    """Save discussions in a local file."""
    count = 0
    while True:
        sleep(60*60*3) # every 3h
        count += 1
        f = open('data/' + 'backup-' + str(count), 'w')
        f.write("page-content")
        f.close()



### app.route ###
@app.route('/', methods=['GET'])
def index():
    return isLogged(render_template('thewall.html',
        location="<a href='http://baptabl.fr'>/bat</a>/theWall/" + roomName,
        fireflies=fireflies
    ))


### login methods ###
def testLogin(login, password):
    global fireflies
    #if login in fireflies:
    return 1
    """
    else:
        fireflies.append(login)
        return 1
    """

def isLogged(func):
    if not 'pseudo' in session:
        flash('Tu dois  t\'authentifier !')
        return redirect(url_for('login'))
    else:
        return func


class loginForm(Form):
    "formulaire de login"
    login = TextField('choisis un pseudonyme : ', [Required("Tu dois entrer un pseudonyme !")])
    #password = PasswordField('Mot de passe', [Required("Veuillez entrer votre mot de passe.")])

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def validate(self):
        if not Form.validate(self):
            return False
        return testLogin(self.login.data, True)#, self.password.data)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = loginForm()

    if request.method == 'POST':
        if form.validate() == False:
            print 'false form'
            for errors in form.errors.values():
                for error in errors:
                    flash(error)
            return render_template('login.html', form=form, location="/bat/theWall/login")
        else:
            if form.login.data not in fireflies:
                session['pseudo'] = form.login.data
                fireflies.append(form.login.data)
                print fireflies
                return redirect(url_for('index'))
            else:
                flash(u'désolé mais ce pseudo est déjà pris !')
                return render_template('login.html', form=form, location="/bat/theWall/login")

    elif request.method == 'GET':
        return render_template('login.html', form=form, location="/bat/theWall/login")

def logout():
    if 'pseudo' not in session:
        return redirect(url_for('login'))
    if session['pseudo'] in fireflies:
        fireflies.remove(session['pseudo'])
    print fireflies
    session.pop('pseudo', None)


    return redirect(url_for('index'))
app.add_url_rule('/logout', 'logout', logout)


### socketio ###
@socketio.on('my event')
def test_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my response',
    {
        'data': message['data'],
        'count': session['receive_count'],
        'pseudo': session['pseudo'],
        'lucioles': '</li><li>'.join(fireflies)
    })


@socketio.on('my broadcast event')
def test_broadcast_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my response',
    {
        'data': message['data'],
        'count': session['receive_count'],
        'pseudo': session['pseudo'],
        'lucioles': '</li><li>'.join(fireflies)
    }, broadcast=True)


@socketio.on('disconnect request')
def disconnect_request():
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my response',
         {'data': "<i>déconnecté de la discussion</i>", 'count': session['receive_count']})
    disconnect()

"""
@socketio.on('connect')
def test_connect():
    emit('my response', {'data': 'Connected', 'count': 0})
"""

@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')


if __name__ == "__main__":
    # ces treads seront à lancer lors de la connection du premier client (qui sera alors host auto-proclamé)
    thread = None
    thread2 = None
    if thread is None:
        thread = Thread(target=backup_thread)
        thread.start()
    if thread2 is None:
        thread2 = Thread(target=fireflies_thread)
        thread2.start()


    #fireflies = []
    #print fireflies
    socketio.run(app, host='0.0.0.0', port=7777)



