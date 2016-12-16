FROM ubuntu:latest

ENV VERSION 0.7.3
ENV DOWNLOAD_URL=https://github.com/jwilder/docker-gen/releases/download/$VERSION/docker-gen-linux-amd64-$VERSION.tar.gz
ENV DOCKER_HOST=unix:///tmp/docker.sock
ENV LOGSTASH_HOST=my-logstash.domain
ENV LOGSTASH_PORT=5044

RUN apt-get update -y
RUN apt-get install -y libssl-dev curl wget
RUN mkdir -p /opt/docker-gen && \
    mkdir -p /etc/docker-gen && \
    wget -O docker-gen.tar.gz $DOWNLOAD_URL && \
    tar -xvzf docker-gen.tar.gz -C /opt/docker-gen && \
    rm docker-gen.tar.gz
RUN wget -O filebeat_1.1.2_amd64.deb https://download.elastic.co/beats/filebeat/filebeat_1.1.2_amd64.deb && \
    dpkg -i filebeat_1.1.2_amd64.deb && \
    rm filebeat_1.1.2_amd64.deb

ADD ./filebeat.tmpl /etc/docker-gen/filebeat.tmpl
ADD ./run.sh /scripts/run.sh

CMD chmod -R 777 /scripts
CMD /scripts/run.sh
