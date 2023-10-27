from flask import Flask, render_template, request, Response, session, redirect, url_for
from flask_sse import sse
from dataclasses import dataclass
from flask_session import Session
import redis

app = Flask(__name__)
app.config["DEBUG"] = True
app.config["REDIS_URL"] = "redis://redis"
app.register_blueprint(sse, url_prefix="/stream")

app.config["SESSION_TYPE"] = "redis"
app.config["SESSION_REDIS"] = redis.from_url("redis://redis")
app.config["SESSION_PERMANENT"] = False

Session(app)


@dataclass
class Message:
    sender: str
    text: str


# in-memory lists of all users and messages
messages = []
users = []


def push_messages():
    for user in users:
        output = render_template("message_list.html", messages=messages, user=user)
        sse.publish(output, type="message_list", channel=user)


@app.route("/")
def index():
    if session.get("user") is not None:
        return redirect(url_for("chat"))
    else:
        return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():
    user = request.form["name"]
    users.append(user)
    session["user"] = user
    messages.append(Message("_system_", f"({user} joined!)"))
    push_messages()
    return redirect(url_for("chat"))


@app.route("/logout", methods=["POST"])
def logout():
    user = session.get("user")
    if user is not None:
        session.clear()

        messages.append(Message("_system_", f"({user} left the chat)"))
        push_messages()
        
        if request.headers.get("HX-Request"):
            resp = Response()
            resp.headers["HX-Redirect"] = url_for("index")
            return resp

    return redirect(url_for("index"))


@app.route("/chat")
def chat():
    user = session.get("user")
    if user is None:
        return redirect(url_for("index"))

    return render_template("chat.html", messages=messages, user=user)


@app.route("/input", methods=["POST"])
def receive_input():
    messages.append(Message(sender=session["user"], text=request.form["text"]))

    push_messages()

    return render_template("message_form.html")
