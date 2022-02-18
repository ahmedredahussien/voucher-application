ARG BASE_CONTAINER=python

#FROM command pulls the latest python image, which acts as the base image
FROM $BASE_CONTAINER

LABEL maintainer="Ahmed Reda <ahmedredahussien@gmail.com>"

#python virtual environemnt
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Working Directory
ENV WORKDIR=/voucher_poc

RUN mkdir -p ${WORKDIR}
WORKDIR ${WORKDIR}

ADD . $WORKDIR

# Install dependencies:
RUN pip install --no-cache-dir --upgrade -r $WORKDIR/docker_api/requirements.txt


# Run the application:
CMD ["uvicorn", "src.main.api.voucher_api:app", "--host", "0.0.0.0", "--port", "8000"]

