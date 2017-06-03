import json

class DockerComposeOutput(object):

	def __init__(self):
		self.ws = None
		self.allLogs = []
		self.newLogs = []
		
	def write(self, text):
		print('Log: {}'.format(text))
		self.allLogs.append(text)
		self.newLogs.append(text)
		
	def flush(self):
		self.flushNewLogs()

	def flushAllLogs(self):
		if self.ws is not None:
			for log in self.allLogs:
				self.ws.send(json.dumps({'type': 'log', 'log': log}))

	def flushNewLogs(self):
		if self.ws is not None:
			for log in self.newLogs:
				self.ws.send(json.dumps({'type': 'log', 'log': log}))
			self.newLogs = []

	def process_ws_connect(self, ws):
		self.ws = ws
		self.flushAllLogs()

	def process_ws_message(self, ws, msg_str):
		self.ws = ws
		if msg_str is None:
			return
		msg = json.loads(msg_str)
		if (msg['type'] == 'ping'):
			self.ws.send(json.dumps({'type': 'ping'}))
		self.flushNewLogs()