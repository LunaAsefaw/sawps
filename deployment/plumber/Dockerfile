FROM rstudio/plumber:v1.2.0 AS prod

# install python 3.10
RUN apt-get update -y && apt-get upgrade -y

RUN apt install software-properties-common -y

RUN add-apt-repository ppa:deadsnakes/ppa

RUN apt install Python3.10

RUN apt-get install -y --no-install-recommends \
    gcc gettext cron \
    spatialite-bin libsqlite3-mod-spatialite \
    python3-dev python3-gdal python3-psycopg2 python3-ldap \
    python3-pip python3-pil python3-lxml python3-pylibmc \
    uwsgi uwsgi-plugin-python3 \
    libfreetype6-dev libpng-dev libtiff5-dev libjpeg-dev

# Install pip packages
ADD deployment/docker/requirements.txt /requirements.txt
RUN pip3 install --upgrade pip && pip install --upgrade pip
# Fix uwsgi build failure missing cc1
ARG CPUCOUNT=1
RUN pip3 install -r /requirements.txt

# install R packages
RUN install2.r --error tidyverse tidygam mgcv ggpubr

# add django project
ADD django_project /home/web/django_project

# create directories
RUN mkdir -p /home/web/plumber_data/

# add entrypoint.sh
ADD django_project/plumber_entrypoint.sh /home/web/plumber_entrypoint.sh

EXPOSE 8181

WORKDIR /home/web/django_project
ENTRYPOINT [ "/home/web/plumber_entrypoint.sh" ]
