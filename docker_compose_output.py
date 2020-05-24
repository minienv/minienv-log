import json


class DockerComposeOutput(object):

    def __init__(self):
        self.web_sockets = []
        self.all_logs = []
        self.new_logs = []

    def write(self, text):
        print('Log: {}'.format(text))
        self.all_logs.append(text)
        self.new_logs.append(text)

    def flush(self):
        self.flush_new_logs()

    def flush_all_logs(self, ws):
        try:
            for log in self.all_logs:
                ws.send(json.dumps({'type': 'log', 'log': log, 'all': True}))
        except:
            print('Error flushing all logs.')
            self.web_sockets.remove(ws)

    def flush_new_logs(self):
        ws_error_indexes = []
        for index, ws in enumerate(self.web_sockets):
            try:
                for log in self.new_logs:
                    ws.send(json.dumps({'type': 'log', 'log': log}))
            except:
                print('Error flushing new logs.')
                ws_error_indexes.push(index)
        self.new_logs = []
        if len(ws_error_indexes) > 0:
            for i in range(len(ws_error_indexes)-1, 0):
                del self.web_sockets[ws_error_indexes[i]]

    def process_ws_connect(self, ws):
        self.web_sockets.append(ws)
        self.flush_all_logs(ws)

    def process_ws_message(self, ws, msg_str):
        if ws not in self.web_sockets:
            self.web_sockets.append(ws)
            self.flush_all_logs(ws)
            return
        if msg_str is None:
            return
        msg = json.loads(msg_str)
        if msg['type'] == 'ping':
            ws.send(json.dumps({'type': 'ping'}))