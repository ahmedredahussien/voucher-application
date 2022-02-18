<div id="top"></div>
<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/ahmedredahussien/voucherProject">
    <img src="images/logo.png" alt="Logo" width="80" height="80">
  </a>
</div>
  
<!-- TABLE OF CONTENTS -->
<a name="TOP"></a>
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
       <ul>
        <li><a href="#presentation">Presentation</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#project-hierarchy">Project Hierarchy</a></li>
        <li><a href="#for-local-run">For Local Run</a></li>
      </ul>
    </li>
    <li><a href="#notebook">Notebook</a></li>
    <li>
        <a href="#docker-and-usage">Docker and Usage</a>
        <ul>
            <li><a href="#code-download">Code download</a></li>
            <li><a href="#docker-images-building">Docker Images Building</a></li>
        </ul>
    </li>
    <li>
        <a href="#information">Information</a>
        <ul>
            <li><a href="#fastapi-testing">FastAPI Testing</a></li>
            <li><a href="#mysql-voucher-database">MySQL Voucher Database</a></li>
        </ul>
    </li>
  </ol>
</details>

## About The Project
**Voucher Churning Customer Reactivation - Python App**
- The idea behind the project is to reactivate customers who left the platform and resume their
order frequency. The Marketing Team approaches the problem by sending vouchers to
customers based on specific rules and customer attributes

[Back to Top "Table of Contents"](#TOP)

### Presentation
**PowerPoint Presentation**
* [Churning Customer Reactivation](https://docs.google.com/presentation/d/1JESapE-7auJNW6evjp1srvGhA9TarUPn/edit?usp=sharing&ouid=109467200517397620113&rtpof=true&sd=true)

---
### Build From
- The data provided in the assignment is the historical data of voucher assignments for
customers  
    * [Dataset on s3 bucket] (s3://dh-data-chef-hiring-test/data-eng/voucher-selector/data.parquet.gzip)
    * [Dataset Https URL](https://dh-data-chef-hiring-test.s3.eu-central-1.amazonaws.com/data-eng/voucher-selector/data.parquet.gzip)
- Data Analysis on 
   * [Google colab Notebook](https://colab.research.google.com/drive/18_c5cS3fHxeIuwoAPH5aCXXawr2V9WUP?usp=sharing)

## Getting Started

### Prerequisites 

- Python Dependency Modules Installation 'pandas','pyarrow','s3fs==0.6.0','fsspec','pyyaml','fastapi','uvicorn[standard]','sqlalchemy','pymysql','mysql-connector-python','mysqlclient'
* [Dependencies](pip install -r all_requirements.txt)

### Project Hierarchy 
* **setup.py**
* **all_requirements.txt** : contains all python modules need to run the voucher python app and fastapi
* **src**
    * **main**
        * **api** : api package
            * **voucher_api.py** : fast-api rest api
        * **app** : app package
            * **voucher_data_preparation.py** : main application entry
        * **common** : common package
            * **common_utils.py** : customer segment classification functions
        * **config** : config package
            * **yaml_config** : class for reading configuration yaml file and initializing config dict instance
        * **resources**  : hold all resources like application configuration file
            * **config.yaml** : application yaml configuration file 
    * **test** : holding all unit testing 

### For Local Run 
```
Install dependent modules under parent project voucherProject in pycharm terminal or cli "command terminal", 
> pip install -r all_requirements.txt

Depending on your installed python version 2 or 3 run the following
> python <args>
or
> python3 <args>
```
---
- **Execution steps for Voucher Python App**

`` > python3 src\app\voucher_data_preparation.py ``

- **Execution steps for FastAPI**

`` > uvicorn src\api\voucher_data_preparation:app ``
[Back to Top "Table of Contents"](#TOP)

## Notebook 
**Notebook for data preparation and analysis**
* [You can view the published Google Notebook on google cloud](https://colab.research.google.com/drive/18_c5cS3fHxeIuwoAPH5aCXXawr2V9WUP?usp=sharing)

if you need further permission to edit please contact me ahmedredahussien@gmail.com 
[Back to Top "Table of Contents"](#TOP)
---

## Docker and Usage
To build the docker for the first time and run the application along with the REST API

You can download IDE "Integrated development environment" software application like Pycharm Intellij community free edition: **https://www.jetbrains.com/pycharm/download/**   

---

### Code download
- Clone the application repository **"https://github.com/ahmedredahussien/voucherProject"** to your machine using one of the 2 options below

* P.S : Make sure that in all cases that git is installed and python interpreter to run the unit tests
pycharm
```
git download : https://git-scm.com/downloads
python >= 3+ : https://www.python.org/downloads/
```
1. **using Option 1 Pycharm:** which has build in integration client with git : 
from upper Menu --> VCS -->  Get from Version Control --> copy the github repository url into URL textbox option
``https://github.com/ahmedredahussien/voucherProject.git``

2. **using Option 2 cli command:** 
``git clone https://github.com/ahmedredahussien/voucherProject.git voucher_project``



### Docker Images Building
3. Open command prompt terminal on your machine 
4. Go to the project parent directory after cloning the application repository 
5. Run the following command if its the first time, make sure you had stable connection for downloading these artifacts
``docker compose up --build --remove-orphans``
6. If you already built the container before run you need to execute only : 
``docker compose up``
7. If you like to run the docker contain in a detach mode in background (Not recommended option - to be able to the status of the logtrace)
``docker compose up -d``
8. Wait until the docker containers starts
    1. mysql-server-container, fastapi-python-app, mysql-php-admin,voucher-python-app)
9. On-startup the voucher-python-app container will start the voucher python application pipline and output results will be insterted into mysql database
10. Once you see the application execution finished successfully and ended with exit 0 "voucher-python-app exited with code 0", you can test the Fast REST API through its url
11. FastAPI has an interface which facilitates request and response user experience URL : 
``http://127.0.0.1:8000/docs``

[Back to Top "Table of Contents"](#TOP)

---
## Information

### FastAPI Testing
12. FastAPI is a Web framework for developing RESTful APIs in Python https://fastapi.tiangolo.com/. FastAPI is based on Pydantic and type hints to validate, serialize, and deserialize data, and automatically auto-generate OpenAPI documents. It fully supports asynchronous programming and can run with Uvicorn and Gunicorn, Uvicorn as one of the fastest Python frameworks available 
13. Open the resource url /voucher/ post verb method --> click on Try it out button --> copy and paste your json sample or modify the exisiting one 
14. Scroll down and you will see the response section and voucher_amount response value for the requested customer segment type
15. Alternative to FastAPI UI, is using native application or browser plugin for Postman tool, 
    1. download native app from : https://www.postman.com/downloads/
    2. download plugin from browser's Extensions plugins     
        
---
### MySQL Voucher Database 
16. Backend database is mysql, all wrangled data is persisted into MySQL for API exposure, future analysis and visualization
#### Multiple tools and third parity support integration with MySQL database  
17. Using any analysis and monitoring tools for Data quality  like Kibana, Graphana
18. Using  BI tool PowerBI, Tableau, Superset
19. Moreover for infrastructure monitoring using DataDog 
20. Using DBeaver software community edition on your machine you can query  the voucher database using native SQL : **https://dbeaver.io/download/** 

    1. **Customer transaction table along with 2 enriched columns for segments classification table : voucher.customer_fact** 

```
select * from voucher.customer_fact limit 30
select count(*) from voucher.customer_fact 
```
-
    2. **Voucher query for ranking most used voucher per each segment - 
    final result is already saved from python code in : voucher.voucher_rank table**
     
```
SELECT * FROM (
select cf.voucher_amount, count(cf.voucher_amount) as cnt, 
cf.frequent_segment, 
ROW_NUMBER () over ( partition by cf.frequent_segment order by count(cf.voucher_amount) desc) as frequent_voucher_rank,
cf.recency_segment,  
ROW_NUMBER () over ( partition by cf.recency_segment order by count(cf.voucher_amount) desc) as recency_voucher_rank
from voucher.customer_fact cf 
group by cf.voucher_amount,cf.recency_segment,cf.frequent_segment
) ranked_vouchers
where recency_voucher_rank = 1 or frequent_voucher_rank = 1
select * from voucher.voucher_rank 

```
[Back to Top "Table of Contents"](#TOP)
