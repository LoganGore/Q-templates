FROM base-python-micro

WORKDIR /app

#Because service_base is our first layer, we copy our service stuff over the top
COPY . /app

#This does not need to be changed. Ports are assigned in docker-compose.yml
EXPOSE 8050

#For Development
CMD ["python3.7", "-u", "watch.py"]

#For Production
#CMD ["python3.7", "-u", "server.py"]
