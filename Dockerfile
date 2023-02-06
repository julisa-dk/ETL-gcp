FROM prefecthq/prefect:2.7.7-python3.9

COPY docker-requirements.txt .

RUN pip3 install -r docker-requirements.txt --trusted-host pypi.python.org --no-cache-dir

COPY ./etl_parent_flow-deployment ./etl_parent_flow-deployment
COPY data ./data