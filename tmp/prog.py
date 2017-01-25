import time
import re
import os
import docker
import sys

client = docker.DockerClient(base_url='unix://var/run/docker.sock')

def main():
	options = getOptions()
	containers = getContainers(options)
	generateFilebeatYaml(options, {
		'containers': containers
	}, {
		'boo': 'yo dude'
	})
#	checkDockerStatus(options)

def getOptions():
	return {
		'blacklist': True
	}

def generateFilebeatYaml(options, lists, vars):
	with open('filebeat.yml', 'r') as f:
		lines = f.readlines()
		lines = replace_loops(lines, lists)
		lines = replace_vars(lines, vars)
		for line in lines:
			sys.stdout.write(line)

def replace_loops(lines, lists):
	loop = {
		'begin': -1,
		'end': -1
	}
	for count, line in enumerate(lines):
		if line.find('<<') != -1 and loop['begin'] == -1:
			loop['begin'] = count;
		elif line.find('>>') != -1 and loop['begin'] != -1 and loop['end'] == -1:
			loop['end'] = count
			chunk_before = list()
			for i in range(loop['end'] - loop['begin'] - 1):
				count = i + loop['begin'] + 1
				chunk_before.append(lines[count])
			q = re.findall('(?<=\<\<)[\w\d\s\-\_]+', lines[loop['begin']])[0].strip().split(' ')
			item_name = q[0]
			items_name = q[len(q) - 1]
			chunk_after = list()
			exec('for ' + item_name + ' in lists[\'' + items_name + '''\']:
  for line in chunk_before:
    for var in re.findall('(?<={{)([^{}$]+)(?=}})', line):
      if var.find(\'''' + item_name + '''[\') != -1:
        line = line.replace('{{' + var + '}}', eval(var))
    chunk_after.append(line)
''')
			lines = clear_loop(loop['begin'], loop['end'], lines)
			lines = replace_loop(loop['begin'], lines, chunk_after)
			return replace_loops(lines, lists)
	return lines

def clear_loop(begin, end, origional):
	for i in range(len(origional)):
		if i >= begin and i <= end:
			del origional[begin]
	return origional

def replace_loop(begin, origional, chunk):
	for i in range(len(chunk)):
		origional.insert(i + begin, chunk[i])
	return origional

def replace_vars(lines, vars):
	new_lines = list()
	for line in lines:
		for var in re.findall('(?<={{)([^{}$]+)(?=}})', line):
			line = line.replace('{{' + var + '}}', vars[var])
		for var in re.findall('(?<={{\$)([^{}]+)(?=}})', line):
			line = line.replace('{{$' + var + '}}', os.environ[var] if var in os.environ else '')
		new_lines.append(line)
	return new_lines

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

