import logging
import pandas as pd

"""# Initialize variables and logging"""
file_url = ""
display_first_x_rows = 1


def init(self):
    from yaml_config import YamlConfig
    import os
    yaml_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources/config.yaml')
    print("yaml_file_path=" + yaml_file_path)
    config_dict = YamlConfig.load_yaml(yaml_file_path)
    app_log_file = config_dict["logfile_path"]
    logging.basicConfig(filename=app_log_file, filemode='w', format='%(name)s - %(levelname)s - %(message)s',
                        level=logging.DEBUG)
    self.file_url = config_dict["source_file_path"]
    self.display_first_x_rows = int(config_dict["display_first_x_rows"])
    logging.info('FILE_PATH=%s', file_url)
    logging.info('DISPLAY_THE_FIRST=%s OF DATAFRAME', display_first_x_rows)



"""# Read and load Row Data into Dataframe """

"""
read parquet compressed file as gzip and loading it into panda's dataframe 
"""


def read_parquet(file_url):
    df = pd.read_parquet(file_url, engine='pyarrow')
    logging.debug(
        'DataFrame INFO: (Column Index,Column Name,Number of Records,Column Data Type). Then summary of datatypes used, memory')
    print(df.info())
    logging.info(df.info)
    logging.info("DATASET_COUNT=%s", df.shape)
    return df


"""# Data Cleansing Stage 1 """

"""
drop null rows, remove duplicated and filtering using Peru as predicate 
"""


def cleanup(df):
    logging.debug('DROP NULL records, Duplicates and Keep only Peru country_code')
    query_condition = "country_code=='Peru'"
    df = df.dropna().drop_duplicates().query(query_condition)
    print(df.info())
    logging.info(df.info)
    print(df.shape)
    logging.info("DATASET_COUNT_AFTER_CLEANSING=%s", df.shape)
    return df


"""# Data Types Conversion and Cleansing Stage 2 """


def adjust_schema_datatypes(df):
    logging.debug('Convert data type and masking/replacing incompatible types by null then removing those null values')
    logging.info('CONVERT_COLUMNS_DATATYPES_&_REMOVING_INCOMPATIBLE_TYPES')
    df['timestamp'] = convert_to_datetime(df['timestamp'])
    df['country_code'] = convert_to_str(df['country_code'])
    df['last_order_ts'] = convert_to_datetime(df['last_order_ts'])
    df['first_order_ts'] = convert_to_datetime(df['first_order_ts'])
    df['total_orders'] = convert_to_numeric(df['total_orders'])
    df['voucher_amount'] = convert_to_numeric(df['voucher_amount'])
    print(df.head(display_first_x_rows))
    logging.debug(df.head(display_first_x_rows))
    """
    remove all Null values which was replaced instead of mismatched types "after applying convert_to_numeric"
    e.g. if total_order was not numeric so its value was replaced with NaN "Null" 
    """
    df = df.dropna()
    # convert to int after removing null and empty values from those files
    df['total_orders'] = convert_to_int(df['total_orders'])
    df['voucher_amount'] = convert_to_int(df['voucher_amount'])

    print(df.shape)
    logging.info("DATASET_COUNT_AFTER_FORMATING=%s", df.shape)

    print(df.info())
    logging.info(df.info)

    return df


# helper functions
def convert_to_numeric(dfColumn):
    return pd.to_numeric(dfColumn, errors='coerce')


def convert_to_int(dfColumn):
    return dfColumn.astype('int')


def convert_to_datetime(dfColumn):
    return pd.to_datetime(dfColumn, errors='coerce')


def convert_to_str(dfColumn):
    return dfColumn.astype('string')


"""# Display Sample Data"""


def display_sample_data(df):
    logging.debug("DATASET_LATEST_COUNT=%s", df.shape)
    logging.debug("DISPLAYING_FIRST=%s of the Dataset", display_first_x_rows)

    print(df.info())
    print(df.head(display_first_x_rows))
    for index, row in df.head(display_first_x_rows).iterrows():
        timestamp = row['timestamp']
        country_code = row['country_code']
        last_order_ts = row['last_order_ts']
        first_order_ts = row['first_order_ts']
        total_orders = row['total_orders']
        voucher_amout = row['voucher_amount']
        print("{0},{1},{2},{3},{4},{5}".format(timestamp, country_code, last_order_ts, first_order_ts, total_orders,
                                               voucher_amout))
        logging.debug("%s,%s,%s,%s,%s,%s", timestamp, country_code, last_order_ts, first_order_ts, total_orders,
                      voucher_amout)


"""# Validation for data issues"""


def validate_data(df):
    print(df.info)

    timestamp = df['timestamp']
    country_code = df['country_code']
    last_order_ts = df['last_order_ts']
    first_order_ts = df['first_order_ts']
    total_orders = df['total_orders']
    voucher_amout = df['voucher_amount']

    print("Validate Column Null Values")
    logging.info("Validate Column Null Values")

    print(
        "timestamp=[{0}],country_code=[{1}],last_order_ts=[{2}],first_order_ts=[{3}],total_orders=[{4}],voucher_amout=[{5}]" \
            .format(timestamp.isnull().values.any(), country_code.isnull().values.any() \
                    , last_order_ts.isnull().values.any(), first_order_ts.isnull().values.any(), \
                    total_orders.isnull().values.any(), voucher_amout.isnull().values.any()))

    df = df.astype(dtype={"country_code": "string", "total_orders": "int", "voucher_amount": "int"})


"""# Enrich Data with Segments (recency, frequent)"""


def enrich_data_with_segments(df):
    df['frequent_segment'] = convert_to_str(df.apply(lambda row: get_frequent_segment(row['total_orders']), axis=1))
    df['recency_segment'] = convert_to_str(
        df.apply(lambda row: get_recency_segment(row['last_order_ts'], row['first_order_ts']), axis=1))

    print(df.info())
    logging.info(df.info)
    logging.info("DATASET_COUNT=%s", df.shape)
    return  df


# helper functions
def subtract_last_first_trans_day(last_order_ts, first_order_ts):
    diff_in_days = last_order_ts - first_order_ts  # timedelta datatype is returned
    return diff_in_days.days


def get_recency_segment_by_days(diff_in_days):
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


def get_recency_segment(last_order_ts, first_order_ts):
    diff_in_days = subtract_last_first_trans_day(last_order_ts, first_order_ts)
    recency_segment = get_recency_segment_by_days(diff_in_days)

    return recency_segment


def get_frequent_segment(total_orders):
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


"""# Simulate Sample Request - not used"""


def simulate_sample_request(df):
    data = {
        "customer_id": 123,
        "country_code": "Peru",
        "last_order_ts": "2018-05-03 00:00:00+00:00",
        "first_order_ts": "2017-05-03 00:00:00+00:00",
        "total_orders": 15,
        "segment_name": "recency_segment"
    }
    dfSampleRequest = pd.DataFrame(data, index=[0])

    dfSampleRequest.last_order_ts = convert_to_datetime(dfSampleRequest.last_order_ts)
    dfSampleRequest.first_order_ts = convert_to_datetime(dfSampleRequest.first_order_ts)
    diff_in_days = (dfSampleRequest.last_order_ts - dfSampleRequest.first_order_ts).dt.days
    diff_in_days = (diff_in_days.values)

    recency_segment = get_recency_segment_by_days(diff_in_days)
    frequent_segment = get_frequent_segment(dfSampleRequest["total_orders"].values)

    print(recency_segment)
    print(frequent_segment)

    filter_by_recency = (df["recency_segment"] == recency_segment)
    # filter_by_frequent = (df.frequent_segment==frequent_segment)
    # print(df.where(filter_by_recency))
    groupby_voucher = df.groupby('voucher_amount').count().where(filter_by_recency)


if __name__ == '__main__':
    init()

    # Read and load Row Data into Dataframe
    df = read_parquet(file_url)

    # Data Cleansing Stage 1
    df = cleanup(df)

    # Data Types Conversion and Cleansing Stage 2 after conversion
    df = adjust_schema_datatypes(df)

    # Display Sample Data
    display_sample_data(df)

    # Validation for data issues
    validate_data(df)

    # Enrich Data with Segments (recency, frequent)
    df = enrich_data_with_segments(df)
