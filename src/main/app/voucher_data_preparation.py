import logging
import os
import sys
from sqlite3.dbapi2 import OperationalError

import MySQLdb
import boto3

import pandas as pd
import sqlalchemy


sys.path.insert(1, os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from config.yaml_config import YamlConfig

from common.common_utils import CommonUtils
from common.custom_exceptions import CustomVoucherBusinessException, CustomDatabaseException

from sqlalchemy.exc import (OperationalError)
from sqlalchemy import create_engine



class CustomerVoucher:
    """################# Initialize variables and logging#######################"""
    def __init__(self):
        try:
            self.config_dict = YamlConfig.get_config()
            app_log_file = self.config_dict["logfile_path"]

            logging.basicConfig(filename=app_log_file, filemode='w', format='%(name)s - %(levelname)s - %(message)s',
                                level=logging.DEBUG)
            self.source_directory = self.config_dict["source_directory"]
            self.file_url = self.config_dict["source_file_path"]

            self.display_first_x_rows = int(self.config_dict["display_first_x_rows"])

            s3_conf = self.config_dict["s3"]
            self.bucket_name = s3_conf["bucket_name"]
            self.bucket_key_file = s3_conf["bucket_key_file"]

            mysql_conf = self.config_dict["mysql"]
            self.dburl = mysql_conf["dburl"]
            self.dburl_alternative = mysql_conf["dburl_alternative"]
            self.db_schemaname = mysql_conf["db_schemaname"]
            self.create_voucher_db = mysql_conf["create_voucher_db"]
            self.use_voucher_db = mysql_conf["use_voucher_db"]
            self.customer_table = mysql_conf["customer_table"]
            self.voucher_table = mysql_conf["voucher_table"]
            self.select_cust_query = mysql_conf["select_cust_query"]
            self.rank_segements_query = mysql_conf["rank_segements_query"]

            logging.info('FILE_PATH=%s', self.file_url)
            logging.info('DISPLAY_THE_FIRST=%s OF DATAFRAME', self.display_first_x_rows)

        except KeyError as err:
            print("KeyError error: {0}".format(err))
            logging.error("KeyError error:=%s", err)
        except ValueError as err:
            print("Could not convert data to an integer: {0}".format(err))
            logging.error("Could not convert data to an integer:=%s", err)
        except BaseException as err:
            print(f"Unexpected {err=}, {type(err)=}")
            logging.error("BaseException:=%s", err)
        except Exception as err:
            print("General Exception: {0}".format(err))
            logging.error("Exception:=%s", err)
        else:
            print("Initialization variables and logging finished successfully")
            logging.debug("Initialization variables and logging finished successfully")

    """###################### Download, Read and load Row Data into Dataframe ##########################"""

    def download_parquet(self):
        """
             Accessing the Bucket Name and Key (file path) anonymously in order to download s3 parquet file
             Bucket Name and Key path are retrieved from yaml config file
        """
        try:
            print('FILE_PATH_TO_WRITE={0}'.format(self.file_url))
            # try creating the parent sample_data source directory and ignore if already exists
            os.makedirs(self.source_directory, exist_ok=True)

            s3_client = boto3.client('s3', aws_access_key_id='', aws_secret_access_key='')
            s3_client._request_signer.sign = (lambda *args, **kwargs: None)
            obj = s3_client.get_object(Bucket=self.bucket_name, Key=self.bucket_key_file)
            bytes_response = obj['Body'].read()

            # write bytes into file
            with open(self.file_url, "wb") as file_object:
                file_object.write(bytes_response)

            downloaded_file_size = os.path.getsize(self.file_url)
            print('DOWNLOADED_FILE_SIZE={0}'.format(downloaded_file_size))
            logging.info('DOWNLOADED_FILE_SIZE=%s', downloaded_file_size)
            return True

        except Exception as err:
            print("download_parquet Exception: {0}".format(err))
            logging.error("download_parquet Exception:=%s", err)
            return False

    def read_parquet(self, file_url):
        """
            Read parquet compressed file as gzip and loading it into panda's dataframe
            :param Absolute path of s3 parquet file location
        """
        try:
            df = pd.read_parquet(file_url, engine='pyarrow')
            logging.debug(
                'DataFrame INFO: (Column Index,Column Name,Number of Records,Column Data Type). Then summary of datatypes used, memory')
            print(df.info())
            logging.info(df.info)
            logging.info("DATASET_COUNT=%s", df.shape)

        except Exception as err:
            print("read_parquet Exception: {0}".format(err))
            logging.error("read_parquet Exception:=%s", err)
            raise CustomVoucherBusinessException(
                "Reading parquet failed from {0} URL, Exception: {1}".format(file_url, err))
        else:
            return df

    """################ Data Cleansing Stage 1 ####################"""

    def cleanup(self, df):
        """
            Drop null rows, remove duplicated and filtering using Peru as predicate
            :param dataframe for cleansing
        """
        try:
            logging.debug('DROP NULL records, Duplicates and Keep only Peru country_code')
            query_condition = "country_code=='Peru'"
            df = df.dropna().drop_duplicates().query(query_condition)
            print(df.info())
            logging.info(df.info)
            print(df.shape)
            logging.info("DATASET_COUNT_AFTER_CLEANSING=%s", df.shape)
        except Exception as err:
            print("cleanup Exception: {0}".format(err))
            logging.error("cleanup Exception:=%s", err)
            raise CustomVoucherBusinessException("cleanup Exception: {0}".format(err))
        else:
            return df

    """################ Data Types Conversion and Cleansing Stage 2 ####################"""

    def adjust_schema_datatypes(self, df):
        """
            Converting dataframe data types to match data values and Cleansing Stage 2
            :param dataframe for converting its fields and cleansing
        """
        try:
            logging.debug(
                'Convert data type and masking/replacing incompatible types by null then removing those null values')
            logging.info('CONVERT_COLUMNS_DATATYPES_&_REMOVING_INCOMPATIBLE_TYPES')
            df['timestamp'] = self.convert_to_datetime(df['timestamp'])
            df['country_code'] = self.convert_to_str(df['country_code'])
            df['last_order_ts'] = self.convert_to_datetime(df['last_order_ts'])
            df['first_order_ts'] = self.convert_to_datetime(df['first_order_ts'])
            df['total_orders'] = self.convert_to_numeric(df['total_orders'])
            df['voucher_amount'] = self.convert_to_numeric(df['voucher_amount'])

            # df[['timestamp', 'last_order_ts', 'first_order_ts']] = df[['timestamp', 'last_order_ts', 'first_order_ts']].apply(pd.to_timedelta)
            print(df.dtypes)

            print(df.head(self.display_first_x_rows))
            logging.debug(df.head(self.display_first_x_rows))
            """
            remove all Null values which was replaced instead of mismatched types "after applying convert_to_numeric"
            e.g. if total_order was not numeric so its value was replaced with NaN "Null" 
            """
            df = df.dropna()
            # convert to int after removing null and empty values from those files
            df['total_orders'] = self.convert_to_int(df['total_orders'])
            df['voucher_amount'] = self.convert_to_int(df['voucher_amount'])

            # using dictionary to convert specific columns
            convert_dict = {
                'country_code': 'str',
                'total_orders': 'int32',
                'voucher_amount': 'int32'
            }
            # df = df.astype(convert_dict)

            print(df.shape)
            logging.info("DATASET_COUNT_AFTER_FORMATING=%s", df.shape)

            print(df.info())
            logging.info(df.info)

        except Exception as err:
            print("adjust_schema_datatypes Exception: {0}".format(err))
            logging.error("adjust_schema_datatypes Exception:=%s", err)
            return None
        else:
            return df

    # helper functions
    def convert_to_numeric(self, dfColumn):
        return pd.to_numeric(dfColumn, errors='coerce')

    def convert_to_int(self, dfColumn):
        return dfColumn.astype('int')

    def convert_to_datetime(self, dfColumn):
        return pd.to_datetime(dfColumn, errors='coerce')

    def convert_to_str(self, dfColumn):
        return dfColumn.astype('string')

    """########### Display Sample Data ###############"""

    def display_sample_data(self, df):
        """
            Displat first x rows of dataframe
            :param dataframe to display
        """
        try:
            logging.debug("DATASET_LATEST_COUNT=%s", df.shape)
            logging.debug("DISPLAYING_FIRST=%s of the Dataset", self.display_first_x_rows)

            print("DISPLAYING_FIRST={0}".format(self.display_first_x_rows))
            print(df.info())
            for index, row in df.head(self.display_first_x_rows).iterrows():
                timestamp = row['timestamp']
                country_code = row['country_code']
                last_order_ts = row['last_order_ts']
                first_order_ts = row['first_order_ts']
                total_orders = row['total_orders']
                voucher_amount = row['voucher_amount']
                print("{0},{1},{2},{3},{4},{5}".format(timestamp, country_code, last_order_ts, first_order_ts,
                                                       total_orders,
                                                       voucher_amount))
                logging.debug("%s,%s,%s,%s,%s,%s", timestamp, country_code, last_order_ts, first_order_ts, total_orders,
                              voucher_amount)
        except Exception as err:
            print("display_sample_data Exception: {0}".format(err))
            logging.error("display_sample_data Exception:=%s", err)
            raise CustomVoucherBusinessException(
                "Display sample dataframe dataset records failed, Exception: {0}".format(err))
        else:
            return df

    """############ Validation for data issues ################"""

    def validate_data(self, df):
        """
            Validate columns value making sure its free from null and can be converted without errors
            :param dataframe to validate
        """
        try:

            print(df.info)

            timestamp = df['timestamp']
            country_code = df['country_code']
            last_order_ts = df['last_order_ts']
            first_order_ts = df['first_order_ts']
            total_orders = df['total_orders']
            voucher_amount = df['voucher_amount']

            print("Validate Column Null Values")
            logging.info("Validate Column Null Values")

            print(
                "timestamp=[{0}],country_code=[{1}],last_order_ts=[{2}],first_order_ts=[{3}],total_orders=[{4}],voucher_amount=[{5}]" \
                    .format(timestamp.isnull().values.any(), country_code.isnull().values.any() \
                            , last_order_ts.isnull().values.any(), first_order_ts.isnull().values.any(), \
                            total_orders.isnull().values.any(), voucher_amount.isnull().values.any()))

            print("Validate Column Simple Datatype conversion")
            logging.info("Validate Column Simple Datatype conversion")
            df = df.astype(dtype={"country_code": "string", "total_orders": "int", "voucher_amount": "int"})
        except Exception as err:
            print("validate_data Exception: {0}".format(err))
            logging.error("validate_data Exception:=%s", err)
            raise CustomVoucherBusinessException(
                "Validating dataframe dataset null values and datatypes failed, Exception: {0}".format(err))
        else:
            return df

    """############## Enrich Data with Segments (recency, frequent) #############"""

    def enrich_data_with_segments(self, df):
        """
            Adding 2 new columns to dataframe with which are calculated fields for  frequent_segment and recency_segment
            :param dataframe to enrich
        """
        custvoucher = CustomerVoucher()
        commonutils = CommonUtils()
        try:
            frequent_segment_val = df.apply(lambda row: commonutils.get_frequent_segment(commonutils, row['total_orders']), axis=1)
            recency_segment_val = df.apply(lambda row: commonutils.get_recency_segment(commonutils, row['last_order_ts'],row['first_order_ts']),axis=1)
            print(frequent_segment_val)
            df['frequent_segment'] = str(frequent_segment_val)
            df['recency_segment'] = str(recency_segment_val)


            print(df.info())
            logging.info(df.info)
            logging.info("DATASET_COUNT=%s", df.shape)

            print(df.head(custvoucher.display_first_x_rows))
            logging.info(df.head(custvoucher.display_first_x_rows))
        except Exception as err:
            print("enrich_data_with_segments Exception: {0}".format(err))
            logging.error("enrich_data_with_segments Exception:=%s", err)
            raise CustomVoucherBusinessException(
                "Enriching customer transaction dataframe with segments failed, Exception: {0}".format(err))
        else:
            return df

    """########## Simulate Sample Request - not used ###############"""

    def simulate_sample_request(self, df):
        data = {
            "customer_id": 123,
            "country_code": "Peru",
            "last_order_ts": "2018-05-03 00:00:00+00:00",
            "first_order_ts": "2017-05-03 00:00:00+00:00",
            "total_orders": 15,
            "segment_name": "recency_segment"
        }
        dfSampleRequest = pd.DataFrame(data, index=[0])

        dfSampleRequest.last_order_ts = self.convert_to_datetime(dfSampleRequest.last_order_ts)
        dfSampleRequest.first_order_ts = self.convert_to_datetime(dfSampleRequest.first_order_ts)
        diff_in_days = (dfSampleRequest.last_order_ts - dfSampleRequest.first_order_ts).dt.days
        diff_in_days = (diff_in_days.values)

        recency_segment = CommonUtils.get_recency_segment_by_days(diff_in_days)
        frequent_segment = CommonUtils.get_frequent_segment(dfSampleRequest["total_orders"].values)

        print(recency_segment)
        print(frequent_segment)

        filter_by_recency = (df["recency_segment"] == recency_segment)
        print(df.where(filter_by_recency))
        # filter_by_frequent = (df.frequent_segment==frequent_segment)
        # groupby_voucher = df.groupby('voucher_amount').count().where(filter_by_recency)

    """########## Save into dayabase ###############"""

    def init_con_engine(self):
        """
            Sqlalchemy connection instance initialization, using URL from yaml config file
        """
        is_error = False
        exception_msg = None
        try:
            print("initialize_engine_url")
            logging.debug("initialize_engine_url")

            engine = create_engine(self.dburl)
            engine.connect()

            print("database connection initialized : {0}".format(engine))
            logging.debug("database connection initialized:=%s", engine)

        except OperationalError as err:
            is_error = True
            exception_msg = str(err)
            print("init_con_engine OperationalError: {0}".format(err))
            logging.error("init_con_engine OperationalError:=%s", err)
        except Exception as err:
            is_error = True
            exception_msg = str(err)
            print("init_con_engine Exception: {0}".format(err))
            logging.error("init_con_engine Exception:=%s", err)
        else:
            print("Returned: {0}".format(engine))
            logging.debug("Returned %s", engine)

            return engine
        finally:
            if is_error:
                print("Error Message=" + exception_msg)
                logging.error("Database initialization failed %s", exception_msg)
                raise CustomDatabaseException("Database initialization failed: {0}".format(exception_msg))

    def persist_df(self, df, engine):
        """
            Adding 2 new columns to dataframe with which are calculated fields for  recency_segment and recency_segment
            :param dataframe to save into database
            :param engine is connection instance to connect to mysql database
        """
        is_succeded = True

        try:
            print("create_voucher_db={0},use_voucher_db={1},customer_table={2},db_schemaname={3},select_cust_query={4}"
                  .format(self.create_voucher_db, self.use_voucher_db,
                          self.customer_table, self.db_schemaname,
                          self.select_cust_query))
            logging.debug(
                'create_voucher_db=%s,use_voucher_db=%s,customer_table=%s,db_schemaname=%s,select_cust_query=%s',
                self.create_voucher_db, self.use_voucher_db,
                self.customer_table, self.db_schemaname,
                self.select_cust_query)

            print("Engine Connection={0}".format(engine))
            logging.debug("Engine Connection=%s", engine)

            if not engine:
                logging.error("Engine Connection is null")
                print("Engine Connection is null")

                raise CustomVoucherBusinessException("Saving Customer Transactions with segments to database failed")
            else:
                engine.execute(self.create_voucher_db)  # create db
                engine.execute(self.use_voucher_db)

                # save dataframe into new table, but if already exists will be replaced
                # (if_exists possible values ='replace','append','fail')
                df.to_sql(self.customer_table, engine, schema=self.db_schemaname, if_exists="replace", index=False)

                # Fetch/Select sample records
                sql = self.select_cust_query
                result = engine.execute(sql)
                for row in result:
                    print(row)
        except OperationalError as err:
            print("persist_df OperationalError: {0}".format(err))
            logging.error("persist_df OperationalError:%s", err)
            is_succeded = False
        except Exception as err:
            print("persist_df Exception: {0}".format(err))
            logging.error("persist_df Exception:=%s", err)
            is_succeded = False
            raise CustomVoucherBusinessException("Customer Transactions saving to database failed: {0}".format(err))
        finally:
            return is_succeded

    def rank_segments_by_voucher_count(self, engine):
        """
            Calculate the most used voucher per each segment (frequent_segment and recency_segment),
            executing ranking query and saving dataframe into database
            :param engine is connection instance to connect to mysql database and save results
        """
        try:
            # top ranked voucher amount most used per segment
            query = self.rank_segements_query
            df = pd.read_sql(query, engine)

            df.to_sql(self.voucher_table, engine, schema="voucher", if_exists="replace", index=False)

            print(df)
        except Exception as err:
            print("rank_segments_by_voucher_count Exception: {0}".format(err))
            logging.error("rank_segments_by_voucher_count Exception:=%s", err)
            raise CustomVoucherBusinessException(
                "Query customer transaction segments and Saving ranked most used vouchers failed: {0}".format(err))

    def save_db_transaction(self, dbengine):
        """
        Not Used - Just for testing purpose
        Save data with segments "table: customer_fact" and
        Save ranked segments by voucher count "table: voucher_rank"
        """
        from sqlalchemy.orm import Session
        try:
            with Session(dbengine) as session:
                session.add(self.persist_df(df, dbengine))
                session.add(self.rank_segments_by_voucher_count(dbengine))
                session.commit()
                session.flush()
        except Exception as err:
            print("Database Transaction Rolledback: {0}".format(err))
            logging.error("Database Transaction Rolledback: %s", err)
            session.rollback()


if __name__ == '__main__':
    custvoucher = CustomerVoucher()

    is_data_available = custvoucher.download_parquet()

    if not is_data_available:
        logging.debug("Exist Application - Dataset is not available")
        print("Exist Application - Dataset is not available")
        sys.exit(1)

    # Download, Read and load Row Data into Dataframe
    df = custvoucher.read_parquet(custvoucher.file_url)
    try:
        # ---- Data Preparation  ---

        # Data Cleansing Stage 1
        df = custvoucher.cleanup(df)

        # Data Types Conversion and Cleansing Stage 2 after conversion
        df = custvoucher.adjust_schema_datatypes(df)

        # Display Sample Data
        custvoucher.display_sample_data(df)

        # Validation for data issues
        # custvoucher.validate_data(df)

        # Enrich Data with Segments (recency, frequent)
        df = custvoucher.enrich_data_with_segments(df)

        # ---- Save database into mysql database tables ---
        dbengine = None
        try:
            dbengine = custvoucher.init_con_engine()
        except CustomDatabaseException as err:
            if ("mysql_db" in err.message):
                # In case that this code will run locally - Retrying to intialize connection using the localhost ip 127.0.0.1
                # instead of docker container image database service name mysql_db
                print("Retry initializing database connection using alternative localhost ip as database url")
                logging.warning("Retry initializing database connection using alternative localhost ip as database url")
                custvoucher.dburl = custvoucher.dburl_alternative
                dbengine = custvoucher.init_con_engine()

        print("dbengine {0}".format(dbengine))

        # Save data with segments "table: customer_fact"
        is_saved = custvoucher.persist_df(df, dbengine)
        if is_saved:
            # Save ranked segments by voucher count "table: voucher_rank"
            custvoucher.rank_segments_by_voucher_count(dbengine)
    except CustomVoucherBusinessException as vbe:
        print("VoucherBusinessException raised:{0}".format(vbe.message))
        logging.error("VoucherBusinessException:%s", vbe.message)
    except Exception as err:
        print("Unknown General Exception: {0}".format(err))
        logging.error("Unknown General Exception:=%s", err)
    finally:
        print("Voucher Application Ended")

