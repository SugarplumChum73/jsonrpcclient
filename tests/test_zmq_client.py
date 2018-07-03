import itertools
import json
from unittest import TestCase

import zmq
from mock import patch, Mock

from jsonrpcclient import Request
from jsonrpcclient.zmq_client import ZMQClient


class TestZMQClient(TestCase):
    def setUp(self):
        # Patch Request.id_generator to ensure the request id is always 1
        Request.id_generator = itertools.count(1)

    def test_instantiate(self):
        ZMQClient("tcp://localhost:5555")

    @patch("zmq.Socket.send_string", Mock())
    @patch(
        "zmq.Socket.recv",
        Mock(
            side_effect=lambda: json.dumps(
                {"jsonrpc": "2.0", "result": 99, "id": 1}
            ).encode("utf-8")
        ),
    )
    @patch("jsonrpcclient.client.Client.response_log")
    def test_send_message(self, *_):
        client = ZMQClient("tcp://localhost:5555")
        client.send_message(str(Request("go")))

    def test_send_message_conn_error(self):
        client = ZMQClient("tcp://localhost:5555")
        # Set timeouts
        client.socket.setsockopt(zmq.RCVTIMEO, 5)
        client.socket.setsockopt(zmq.SNDTIMEO, 5)
        client.socket.setsockopt(zmq.LINGER, 5)
        with self.assertRaises(zmq.error.ZMQError):
            client.send_message(str(Request("go")))
