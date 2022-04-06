FROM scratch

MAINTAINER Ananth Goyak <ananthgoyal@berkeley.edu>


EXPOSE 5001

RUN yum install -y amazon-linux-extras && amazon-linux-extras install -y python3.8


WORKDIR /tmp
