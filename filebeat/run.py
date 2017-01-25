import time
import re
import os
import docker
import sys
import hashlib

client = docker.DockerClient(base_url='unix://var/run/docker.sock')

def main():
	options = get_options()
	update_filebeat(options)
	print('tailing logs . . .')
	if options['auto_update']:
		check_docker_status(options)

def get_options():
	return {
		'blacklist': True if ('BLACKLIST' in os.environ and os.environ['BLACKLIST'] == "true") else False,
		'auto_update': False if ('AUTO_UPDATE' in os.environ and os.environ['AUTO_UPDATE'] == "false") else True,
		'filebeat_dir': '/etc/filebeat',
		'sleep_seconds': float(os.environ['SLEEP_SECONDS']) if 'SLEEP_SECONDS' in os.environ else float('5')
	}

def update_filebeat(options):
	containers = get_containers(options)
	file = generate_filebeat_yaml(options, {
		'containers': containers
	}, {})
	if filebeat_updated(file, options):
		print('updated')
		write_filebeat_yaml(options, file)
		restart_filebeat(options)

def restart_filebeat(options):
	print('restarting filebeat')
	os.system('/etc/init.d/filebeat restart &')

def generate_filebeat_yaml(options, lists, vars):
	file = ''
	with open('/scripts/filebeat.yml', 'r') as f:
		lines = f.readlines()
		lines = replace_loops(lines, lists)
		lines = replace_vars(lines, vars)
		for line in lines:
			file += line
	return file

def write_filebeat_yaml(options, file):
	location = (options['filebeat_dir'] + '/filebeat.yml').replace('//', '/')
	f = open(location, 'w')
	f.write(file)

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
			q = re.findall('(?<=\<\<)(.+)', lines[loop['begin']])[0].strip().split(' ')
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

def get_containers(options):
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

def hash_file(file):
	md5 = hashlib.md5()
	md5.update(file)
	return md5.hexdigest()

def filebeat_updated(new_file, options):
	current_file = ''
	location = (options['filebeat_dir'] + '/filebeat.yml').replace('//', '/')
	with open(location, 'r') as f:
		lines = f.readlines()
		for line in lines:
			current_file += line
	return hash_file(current_file) != hash_file(new_file)

def check_docker_status(options):
	while True:
		update_filebeat(options)
		time.sleep(options['sleep_seconds'])

main()
