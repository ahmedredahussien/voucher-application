import logging
import os
import sys
from sqlite3.dbapi2 import OperationalError

import pandas as pd

# import sys
# import os.path
# sys.path.append(
# os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from yaml_config import YamlConfig


class CustomerVoucher:
    """################# Initialize variables and logging#######################"""

    def __init__(self):
        config_dict = YamlConfig.get_config(self)
        app_log_file = config_dict["logfile_path"]

        logging.basicConfig(filename=app_log_file, filemode='w', format='%(name)s - %(levelname)s - %(message)s',
                            level=logging.DEBUG)
        self.file_url = config_dict["source_file_path"]
        self.display_first_x_rows = int(config_dict["display_first_x_rows"])

        mysql_conf = config_dict["mysql"]
        self.dburl = mysql_conf["dburl"]
        self.db_schemaname = mysql_conf["db_schemaname"]
        self.create_voucher_db = mysql_conf["create_voucher_db"]
        self.use_voucher_db = mysql_conf["use_voucher_db"]
        self.customer_table = mysql_conf["customer_table"]
        self.voucher_table = mysql_conf["voucher_table"]
        self.select_cust_query = mysql_conf["select_cust_query"]
        self.rank_segements_query = mysql_conf["rank_segements_query"]

        logging.info('FILE_PATH=%s', self.file_url)
        logging.info('DISPLAY_THE_FIRST=%s OF DATAFRAME', self.display_first_x_rows)

    """###################### Read and load Row Data into Dataframe ##########################"""

    """
    read parquet compressed file as gzip and loading it into panda's dataframe 
    """

    def read_parquet(self, file_url):
        df = pd.read_parquet(file_url, engine='pyarrow')
        logging.debug(
            'DataFrame INFO: (Column Index,Column Name,Number of Records,Column Data Type). Then summary of datatypes used, memory')
        print(df.info())
        logging.info(df.info)
        logging.info("DATASET_COUNT=%s", df.shape)
        return df

    """################ Data Cleansing Stage 1 ####################"""

    """
    drop null rows, remove duplicated and filtering using Peru as predicate 
    """

    def cleanup(self, df):
        logging.debug('DROP NULL records, Duplicates and Keep only Peru country_code')
        query_condition = "country_code=='Peru'"
        df = df.dropna().drop_duplicates().query(query_condition)
        print(df.info())
        logging.info(df.info)
        print(df.shape)
        logging.info("DATASET_COUNT_AFTER_CLEANSING=%s", df.shape)
        return df

    """################ Data Types Conversion and Cleansing Stage 2 ####################"""

    def adjust_schema_datatypes(self, df):
        logging.debug(
            'Convert data type and masking/replacing incompatible types by null then removing those null values')
        logging.info('CONVERT_COLUMNS_DATATYPES_&_REMOVING_INCOMPATIBLE_TYPES')
        df['timestamp'] = self.convert_to_datetime(df['timestamp'])
        df['country_code'] = self.convert_to_str(df['country_code'])
        df['last_order_ts'] = self.convert_to_datetime(df['last_order_ts'])
        df['first_order_ts'] = self.convert_to_datetime(df['first_order_ts'])
        df['total_orders'] = self.convert_to_numeric(df['total_orders'])
        df['voucher_amount'] = self.convert_to_numeric(df['voucher_amount'])
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

        print(df.shape)
        logging.info("DATASET_COUNT_AFTER_FORMATING=%s", df.shape)

        print(df.info())
        logging.info(df.info)

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
        logging.debug("DATASET_LATEST_COUNT=%s", df.shape)
        logging.debug("DISPLAYING_FIRST=%s of the Dataset", self.display_first_x_rows)

        print(df.info())
        print(df.head(self.display_first_x_rows))
        for index, row in df.head(self.display_first_x_rows).iterrows():
            timestamp = row['timestamp']
            country_code = row['country_code']
            last_order_ts = row['last_order_ts']
            first_order_ts = row['first_order_ts']
            total_orders = row['total_orders']
            voucher_amount = row['voucher_amount']
            print("{0},{1},{2},{3},{4},{5}".format(timestamp, country_code, last_order_ts, first_order_ts, total_orders,
                                                   voucher_amount))
            logging.debug("%s,%s,%s,%s,%s,%s", timestamp, country_code, last_order_ts, first_order_ts, total_orders,
                          voucher_amount)

    """############ Validation for data issues ################"""

    def validate_data(self, df):
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

    """############## Enrich Data with Segments (recency, frequent) #############"""

    def enrich_data_with_segments(self, df):
        df['frequent_segment'] = self.convert_to_str(
            df.apply(lambda row: self.get_frequent_segment(row['total_orders']), axis=1))
        df['recency_segment'] = self.convert_to_str(
            df.apply(lambda row: self.get_recency_segment(row['last_order_ts'], row['first_order_ts']), axis=1))

        print(df.info())
        logging.info(df.info)
        logging.info("DATASET_COUNT=%s", df.shape)
        return df

    # helper functions
    def subtract_last_first_trans_day(self, last_order_ts, first_order_ts):
        diff_in_days = last_order_ts - first_order_ts  # timedelta datatype is returned
        return diff_in_days.days

    @staticmethod
    def get_recency_segment_by_days(self, diff_in_days):
        recency_segment = ""

        # assuption for cases where difference in days less than 30 as it was missing from requirement
        if diff_in_days >= 0 and diff_in_days < 30:
            recency_segment = "30-"
        elif diff_in_days >= 30 and diff_in_days < 60:
            recency_segment = "30-60"
        elif diff_in_days >= 60 and diff_in_days < 90:
            recency_segment = "60-90"
        elif diff_in_days >= 90 and diff_in_days < 120:
            recency_segment = "90-120"
        elif diff_in_days >= 120 and diff_in_days < 180:
            recency_segment = "120-180"
        elif diff_in_days >= 180:
            recency_segment = "180+"
        return recency_segment

    @staticmethod
    def get_recency_segment(self, last_order_ts, first_order_ts):
        diff_in_days = self.subtract_last_first_trans_day(last_order_ts, first_order_ts)
        recency_segment = self.get_recency_segment_by_days(diff_in_days)

        return recency_segment

    @staticmethod
    def get_frequent_segment(self,total_orders):
        frequent_segment = ""

        if total_orders >= 0 and total_orders <= 4:
            frequent_segment = "0-4"
        elif total_orders >= 5 and total_orders < 13:
            frequent_segment = "5-13"
        elif total_orders >= 13 and total_orders < 37:
            frequent_segment = "13-37"
        # assuption for cases where difference in days total orders more than 37 as it was missing from requirement
        elif total_orders >= 37:
            frequent_segment = "37+"
        return frequent_segment

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

        recency_segment = self.get_recency_segment_by_days(diff_in_days)
        frequent_segment = self.get_frequent_segment(dfSampleRequest["total_orders"].values)

        print(recency_segment)
        print(frequent_segment)

        filter_by_recency = (df["recency_segment"] == recency_segment)
        print(df.where(filter_by_recency))
        # filter_by_frequent = (df.frequent_segment==frequent_segment)
        # groupby_voucher = df.groupby('voucher_amount').count().where(filter_by_recency)

    """########## Save into dayabase ###############"""

    def init_con_engine(self):
        from sqlalchemy import create_engine
        engine = create_engine(self.dburl)
        return engine

    def persist_df(self, df, engine):

        try:
            engine.execute(self.create_voucher_db)  # create db
            engine.execute(self.use_voucher_db)
            # default
            # engine = create_engine('mysql://scott:tiger@localhost/foo')
            # mysql-python
            # engine = create_engine('mysql+mysqldb://scott:tiger@localhost/foo')
            # MySQL-connector-python
            # engine = create_engine('mysql+mysqlconnector://root:tiger@localhost/foo')
            # engine = create_engine("mysql+pymysql://user:pass@some_mariadb/dbname?charset=utf8mb4")

            # save dataframe into new table, but if already exists will be replaced
            # (if_exists possible values ='replace','append','fail')
            df.to_sql(self.customer_table, engine, schema=self.db_schemaname, if_exists="replace", index=False)

            # Fetch/Select sample records
            sql = self.select_cust_query
            result = engine.execute(sql)
            for row in result:
                print(row)
            return True
        except OperationalError as e:
            print(e)

    def rank_segments_by_voucher_count(self, engine):
        # top ranked voucher amount most used per segment
        query = self.rank_segements_query
        df = pd.read_sql(query, engine)

        df.to_sql(self.voucher_table, engine, schema="voucher", if_exists="replace", index=False)

        print(df)


if __name__ == '__main__':
    custvoucher = CustomerVoucher()

    # Read and load Row Data into Dataframe
    df = custvoucher.read_parquet(custvoucher.file_url)

    # Data Cleansing Stage 1
    df = custvoucher.cleanup(df)

    # Data Types Conversion and Cleansing Stage 2 after conversion
    df = custvoucher.adjust_schema_datatypes(df)

    # Display Sample Data
    custvoucher.display_sample_data(df)

    # Validation for data issues
    custvoucher.validate_data(df)

    # Enrich Data with Segments (recency, frequent)
    df = custvoucher.enrich_data_with_segments(df)

    # ---- Save database into mysql database tables ---
    dbengine = custvoucher.init_con_engine()

    # Save data with segments "table: customer_fact"
    is_saved = custvoucher.persist_df(df, dbengine)
    if is_saved:
        # Save ranked segments by voucher count "table: voucher_rank"
        custvoucher.rank_segments_by_voucher_count(dbengine)
