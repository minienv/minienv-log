import threading
import time
from compose.container import Container
from compose.cli.command import get_project as compose_get_project, get_config_path_from_options
from compose.cli.log_printer import build_log_presenters
from compose.cli.log_printer import LogPrinter
from compose.config.environment import Environment

class DockerComposeLog(threading.Thread):

	def __init__(self, docker_compose_output, docker_compose_path) :
		threading.Thread.__init__(self)
		self.docker_compose_output = docker_compose_output
		self.docker_compose_path = docker_compose_path

	def run(self):
		p = self.get_project(self.docker_compose_path)
		containers = p.containers(stopped=True)
		while len(containers) == 0:
			time.sleep(5)
			containers = p.containers(stopped=True)
		log_args = {
    		'follow': True,
    		'timestamps': True
		}
		self.log_printer_from_project(
			p,
			containers,
			True,
			log_args,
			event_stream=p.events()
		).run()

	def stop(self):
		pass

	def get_project(self, path):
		environment = Environment.from_env_file(path)
		config_path = get_config_path_from_options(path, dict(), environment)
		project = compose_get_project(path, config_path)
		return project

	def log_printer_from_project(
		self,
    	project,
    	containers,
    	monochrome,
    	log_args,
    	cascade_stop=False,
    	event_stream=None,
	):
		return LogPrinter(
			containers,
        	build_log_presenters(project.service_names, monochrome),
        	event_stream or project.events(),
        	cascade_stop=cascade_stop,
        	log_args=log_args,
        	output=self.docker_compose_output
		)