ARG BASE_CONTAINER=python

#FROM command pulls the latest python image, which acts as the base image
FROM $BASE_CONTAINER

LABEL maintainer="Ahmed Reda <ahmedredahussien@gmail.com>"

#python virtual environment
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Working Directory
ENV WORKDIR=/voucher_poc

RUN mkdir -p ${WORKDIR}
WORKDIR ${WORKDIR}
ADD . $WORKDIR

# Install dependencies: COPY source-local-machine destination-container
COPY requirements.txt $WORKDIR/
RUN pip install -r $WORKDIR/requirements.txt

# Run the application:
COPY voucher_data_preparation.py $WORKDIR/
COPY data.parquet.gzip $WORKDIR/

CMD ["python", "voucher_data_preparation.py"]