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
async def receive_input():
    messages.append(request.form["message"])
    reply = await get_reply(request.form["message"])
    messages.append(reply)
    output = render_template("message_list.html", messages=messages)
    sse.publish(output, type="message_list")
    return render_template("message_form.html")


async def get_reply(message):
    return f"reply to {message}"
