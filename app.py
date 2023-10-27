from flask import Flask, render_template, request, Response, session
from flask_sse import sse
from dataclasses import dataclass
from uuid import uuid4
from flask_session import Session
import redis

app = Flask(__name__)
app.config["DEBUG"] = True
app.config["REDIS_URL"] = "redis://redis"
app.register_blueprint(sse, url_prefix="/stream")

app.config["SESSION_TYPE"] = "redis"
app.config["SESSION_REDIS"] = redis.from_url("redis://redis")

Session(app)

# in-memory lists of all users and messages
messages = []
users = []


@dataclass
class Message:
    sender: str
    text: str


@app.route("/")
def index():
    user = str(uuid4())
    users.append(user)
    session["user"] = user
    return render_template("index.html", messages=messages, user=user)


@app.route("/input", methods=["POST"])
def receive_input():
    messages.append(Message(sender=session["user"], text=request.form["text"]))

    for user in users:
        output = render_template("message_list.html", messages=messages, user=user)
        sse.publish(output, type="message_list", channel=user)

    return render_template("message_form.html")
