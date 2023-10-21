from flask import Flask, render_template, request, Response
from flask_sse import sse

app = Flask(__name__)
app.config["REDIS_URL"] = "redis://redis"
app.register_blueprint(sse, url_prefix="/stream")

# in-memory list of all messages
messages = []


@app.route("/")
def index():
    return render_template("index.html", messages=messages)


@app.route("/input", methods=["POST"])
def receive_input():
    messages.append(request.form["message"])
    messages.append(f"reply to {request.form['message']}")
    output = render_template("message_list.html", messages=messages)
    sse.publish(output, type="message_list")
    return Response("received", 201)
