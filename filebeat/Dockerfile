FROM ubuntu:latest

ENV BLACKLIST=false
ENV SLEEP_SECONDS=5
ENV LOGSTASH_HOST=elk
ENV LOGSTASH_PORT=5044
ENV KIBANA_HOST=elk
ENV KIBANA_PORT=9200
ENV AUTO_UPDATE=true

RUN apt-get update -y && apt-get install -y libssl-dev wget curl python-pip
RUN pip install docker
RUN wget -O filebeat_1.1.2_amd64.deb https://download.elastic.co/beats/filebeat/filebeat_1.1.2_amd64.deb && \
    dpkg -i filebeat_1.1.2_amd64.deb && \
    rm filebeat_1.1.2_amd64.deb

ADD ./filebeat.yml /scripts/filebeat.yml
ADD ./run.py /scripts/run.py
RUN chmod -R 777 /scripts

CMD /etc/init.d/filebeat start &
CMD echo "filebeat started" && \
    curl -XPUT "http://$KIBANA_HOST:$KIBANA_PORT/_template/filebeat?pretty" -d@/etc/filebeat/filebeat.template.json && \
    echo "curl ran" && \
    python /scripts/run.py && \
    echo "python ran"
