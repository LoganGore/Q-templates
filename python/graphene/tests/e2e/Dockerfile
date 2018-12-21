# python environment for running the e2e tests
# --------------------------------------------
FROM docker.corp.maana.io/alpine_python3 as e2e
WORKDIR /usr/app
COPY e2e_requirements.txt .
RUN pip3 install --no-cache-dir -r e2e_requirements.txt
COPY ./*.py tests/
CMD ["python3", "-m", "pytest", "tests/"]
