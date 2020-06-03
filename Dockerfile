FROM python:3-alpine
RUN pip install --upgrade pip
COPY dist/ /tmp/dist/
RUN cd /tmp/dist/ && python setup.py test && pip install .
RUN rm -rf /tmp/dist
COPY docker-entrypoint.sh /usr/local/bin/
RUN ln -s /usr/local/bin/docker-entrypoint.sh /
ENTRYPOINT ["docker-entrypoint.sh"]
