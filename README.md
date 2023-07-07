# elk-filebeat
Dumps docker logs to an ELK stack automatically

![](assets/elk-filebeat.png)

## Installation
```
services:
  elk:
    image: jamrizzi/elk:latest
    ports:
      - 5601:5601
    volumes:
      - /volumes/elk-data:/var/lib/elasticsearch
  filebeat:
    image: jamrizzi/filebeat:latest
    environment:
      BLACKLIST: false
      SLEEP_SECONDS: 5
      LOGSTASH_HOST: elk
      LOGSTASH_PORT: 5044
      KIBANA_HOST: elk
      KIBANA_PORT: 9200
      AUTO_UPDATE: true
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - /var/lib/docker/containers:/var/lib/docker/containers
    links:
      - elk:elk
```

## Usage
Add the tag filebeat=true to containers you want to collect logs from.

The first time running kibana, you will need to change "logstash-&ast;" to "filebeat-&ast;"

## Resources
* http://www.sandtable.com/forwarding-docker-logs-to-logstash/
* https://elk-docker.readthedocs.io/
