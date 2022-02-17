import connexion
import six

from swagger_server.models.customer import Customer  # noqa: E501
from swagger_server.models.voucher import Voucher  # noqa: E501
from swagger_server import util


def find_vouhcer_by_segment(customer_id, country_code, last_order_ts, first_order_ts, total_orders, segment_name):  # noqa: E501
    """Return voucher amount by customer segment

    Return mostly used voucher value for customer segments # noqa: E501

    :param customer_id: customer id
    :type customer_id: int
    :param country_code: customer’s country - currently the available country is Peru
    :type country_code: str
    :param last_order_ts: timestamp of the last order done by customer
    :type last_order_ts: str
    :param first_order_ts: timestamp of the first order done by customer
    :type first_order_ts: str
    :param total_orders: total orders done by customer
    :type total_orders: int
    :param segment_name: which segment customer belongs to
    :type segment_name: List[str]

    :rtype: List[Voucher]
    """
    last_order_ts = util.deserialize_datetime(last_order_ts)
    first_order_ts = util.deserialize_datetime(first_order_ts)
    return 'do some magic!'


def select_voucher(body):  # noqa: E501
    """Return voucher according to customer segement

     # noqa: E501

    :param body: Request using customer transaction object
    :type body: dict | bytes

    :rtype: List[Voucher]
    """
    if connexion.request.is_json:
        body = Customer.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'
