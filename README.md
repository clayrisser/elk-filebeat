# elk-filebeat
Dumps docker logs to an ELK stack automatically

## Installation
Reference the docker-compose.yml file

## Usage
Add the tag filebeat=true to containers you want to collect logs from.

The first time running kibana, you will need to change "logstash-*" to "filebeat-*"

## Resources
* http://www.sandtable.com/forwarding-docker-logs-to-logstash/
* https://elk-docker.readthedocs.io/
