#!/bin/bash

sed -i "s/<LOGSTASH_HOST>/"$LOGSTASH_HOST"/g" /etc/docker-gen/filebeat.tmpl
sed -i "s/<LOGSTASH_PORT>/"$LOGSTASH_PORT"/g" /etc/docker-gen/filebeat.tmpl
curl -XPUT 'http://elk:9200/_template/filebeat?pretty' -d@/etc/filebeat/filebeat.template.json
/etc/init.d/filebeat start
/opt/docker-gen/docker-gen -notify "/etc/init.d/filebeat restart > /dev/null 2>&1 &" -notify-output -watch /etc/docker-gen/filebeat.tmpl /etc/filebeat/filebeat.yml
