import contextlib
import http
import http.server
import logging
import socket


LOG = logging.getLogger(__name__)


# copied from https://github.com/python/cpython/blob/3.12/Lib/http/server.py
class DualStackServer(http.server.ThreadingHTTPServer):

    def server_bind(self):
        # suppress exception when protocol is IPv4
        with contextlib.suppress(Exception):
            self.socket.setsockopt(
                socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
        return super().server_bind()

    # add log
    def get_request(self):
        r = super().get_request()
        LOG.info('get_request: %s', r)
        return r

    def shutdown_request(self, request):
        LOG.info('shutdown_request: %s', request)
        super().shutdown_request(request)


class Handler(http.server.BaseHTTPRequestHandler):

    def handle_one_request(self):
        LOG.info('handle_one_request: %s', self.request)
        return super().handle_one_request()

    def do_HEAD(self):
        self.send_response(http.HTTPStatus.OK)
        self.send_header("Content-type", "text/plain")
        self.send_header("Content-Length", "2")
        self.end_headers()

    def do_GET(self):
        self.do_HEAD()
        self.wfile.write(b'OK')

    def log_message(self, format, *args):
        message = format % args
        LOG.info("%s - - [%s] %s\n" %
                         (self.address_string(),
                          self.log_date_time_string(),
                          message.translate(self._control_char_table)))

    def address_string(self):
        return '%s:%s' % (self.client_address[0], self.client_address[1])


def run():
    server_address = ('', 8080)
    Handler.protocol_version = 'HTTP/1.1'
    httpd = DualStackServer(server_address, Handler)
    httpd.serve_forever()


logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
run()
