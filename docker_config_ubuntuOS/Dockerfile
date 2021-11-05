FROM ubuntu:20.04
#set up environment
RUN apt-get update && apt-get install --no-install-recommends --no-install-suggests -y curl
RUN apt-get -y install python3.8
RUN apt-get -y install python3-pip
RUN apt install -y git
WORKDIR /code
COPY requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.3.0/en_core_sci_sm-0.3.0.tar.gz
RUN python3 -m pip install --no-cache-dir git+https://github.com/OntoGene/PyBioC.git
COPY . /code/


