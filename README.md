## Voucher Churning Customer Reactivation - Python App

- The idea behind the project is to reactivate customers who left the platform and resume their
order frequency. The Marketing Team approaches the problem by sending vouchers to
customers based on specific rules and customer attributes

---

- The data provided in the assignment is the historical data of voucher assignments for
customers  
    * [Dataset on s3 bucket] (s3://dh-data-chef-hiring-test/data-eng/voucher-selector/data.parquet.gzip)
    * [Dataset Https URL](https://dh-data-chef-hiring-test.s3.eu-central-1.amazonaws.com/data-eng/voucher-selector/data.parquet.gzip)
- Data Analysis on 
   * [Google colab Notebook](https://colab.research.google.com/drive/18_c5cS3fHxeIuwoAPH5aCXXawr2V9WUP?usp=sharing)

## Prerequisites 
- Python Modules Installation 'pandas','pyarrow', 's3fs==0.6.0','fsspec','pyyaml'
* [Dependencies](pip install pandas pyarrow s3fs==0.6.0 fsspec pyyaml)

```
Install dependent modules  using (setup.py) under parent project voucherProject, 
depending on your install python version 2 or 3 run the following
> python setup.py install --user
or
> python3 setup.py install --user
```
---
```
Execution steps 
> python3 setup.py install --user
then
> python3 src/main/voucher_datapreparation.py
```
* **setup.py**
* **src**
    * **main**
        * **resources**  #hold all resources like application configuration file
            * **config.yaml** #application yaml configuration file 
        * **voucher_data_preparation.py**  #main application entry
        * **yaml_config**  #class for reading configuration yaml file
    * **test** #holding all unit testing 

* **docker**

```
docker commands
to stop exisitng container
> docker stop python-voucher
> docker rm python-voucher

to start or restart
> docker restart python-voucher
> docker start python-voucher

to open ssh with the docker container 
> docker exec -it python-voucher /bin/bash

if you need to build a new docker
> docker build -t voucher_python:0.0.1 <Parent_folder_path_holding_Dockerfile>

if you need to pull the published docker from docker_hub
> docker pull

run once :
> docker run -d -it --name python-voucher voucher_python:0.0.1
or
run forever until stopping manually : 
> docker run -d -it --name python-voucher voucher_python:0.0.1 tail -f /dev/null
or
run once and output result to text file :
> docker run -it --name python-voucher voucher_python:0.0.1 > app.txt

```
