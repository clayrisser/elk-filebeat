import time
import os
import docker
import sys

client = docker.DockerClient(base_url='unix://var/run/docker.sock')

def main():
	options = getOptions()
	containers = getContainers(options)
	generateFilebeatYaml(containers, options)
#	checkDockerStatus(options)

def getOptions():
	return {
		'blacklist': True
	}

def generateFilebeatYaml(containers, options):
	for container in containers:
		print(container)
	data = {
		'loops': list()
	}
	with open('filebeat.ymlt', 'r') as f:
		loop = {
			'begin': -1,
			'end': -1
		}
		for count, line in enumerate(f.readlines()):
			if line.find('<<') != -1 and loop['begin'] == -1:
				loop['begin'] = count;
			elif line.find('>>') != -1 and loop['begin'] != -1:
				loop['end'] = count;
				data['loops'].append(loop)
				loop = {
					'begin': -1,
					'end': -1
				}
			sys.stdout.write(line)
	print(data)

def getContainers(options):
	containers = list()
	for container in client.containers.list():
		valid = False
		if options['blacklist']:
			valid = True
		labels = container.attrs['Config']['Labels']
		for label in labels.iteritems():
			if options['blacklist']:
				if label[0] == 'filebeat' and label[1] == 'false':
					valid = False
			else:
				if label[0] == 'filebeat' and label[1] == 'true':
					valid = True
                if valid:
			containers.append({
				'id': container.id,
				'name': container.name,
				'container': container,
				'log_path': '/var/lib/docker/containers/' + container.id + '/' + container.id + '-json.log'
			})
	return containers

def checkDockerStatus(options):
	while True:
		print('checking docker status')
		time.sleep(5)

main()

