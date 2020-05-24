import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, send_from_directory
from flask_sockets import Sockets
from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler
from docker_compose_log import DockerComposeLog
from docker_compose_output import DockerComposeOutput


class CustomFlask(Flask):
    jinja_options = Flask.jinja_options.copy()
    jinja_options.update(dict(
        block_start_string='$$',
        block_end_string='$$',
        variable_start_string='$',
        variable_end_string='$',
        comment_start_string='$#',
        comment_end_string='#$',
    )
)


# global vars
app = CustomFlask(__name__)
sockets = Sockets(app)
docker_compose_output = None


@app.after_request
def add_header(r):
    # disable caching
    # after multiple runs kubernetes or docker swarm can expose the same port that was exposed
    # for a different web app. if both apps have the same file names the browser could use an old/cached version
    r.headers['Access-Control-Allow-Origin'] = os.environ.get('MINIENV_ALLOW_ORIGIN')
    r.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    r.headers['Cache-Control'] = 'no-store, must-revalidate'
    r.headers['Expires'] = '0'
    return r


@app.route('/<path:path>')
def send_file(path):
    return send_from_directory('public', path)


@app.route('/')
def index():
    http_scheme = os.environ.get('MINIENV_NODE_HOST_PROTOCOL')
    print('Serving request, http_scheme = {}'.format(http_scheme))
    if http_scheme == 'http':
        web_socket_protocol = 'ws://'
    else:
        web_socket_protocol = 'wss://'
    return render_template('index.html', web_socket_protocol=web_socket_protocol)


@sockets.route('/')
def process_websocket_message(ws):
    docker_compose_output.process_ws_connect(ws)
    while not ws.closed:
        message = ws.receive()
        docker_compose_output.process_ws_message(ws, message)


if __name__ == '__main__':
    try:
        load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
        docker_compose_output = DockerComposeOutput()
        print('Starting Docker Compose Log @ {}...'.format(os.environ.get('MINIENV_DIR')))
        docker_compose_log = DockerComposeLog(
            docker_compose_output,
            os.environ.get('MINIENV_DIR')
        )
        print('Docker Compose Log started.')
        docker_compose_log.start()
        # Start HTTP/WebSocket server
        port = int(os.getenv('PORT', 8080))
        server = pywsgi.WSGIServer(('', port), app, handler_class=WebSocketHandler)
        server.serve_forever()
    except (KeyboardInterrupt, SystemExit):
        pass