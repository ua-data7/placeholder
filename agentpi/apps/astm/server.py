import logging
import netifaces as ni

from astm import server

from agentpi.library import is_ipv4
from .dispatcher import AgentRecordDispatcher


logger = logging.getLogger(__name__)


def run_server(current_app, port, astm_nic):
    astm_port = int(port)
    print(f"astm_nic: {astm_nic}  astm_port: {astm_port} ")
    if(is_ipv4(astm_nic)):
        ip = astm_nic
    else:
        try:
            ni.ifaddresses(astm_nic)
        except ValueError:
            logger.error(f"ERROR: No interface {astm_nic} found.")
            return
        try:
            ip = ni.ifaddresses(astm_nic)[ni.AF_INET][0]['addr']
        except KeyError:

            logger.error(f"ERROR: No IP found on interface {astm_nic}.")
            return

    logger.info(f"Launching service on {astm_nic}: {ip}:{astm_port}")
    s = server.Server(
        host=ip,
        port=astm_port,
        request=None,
        dispatcher=AgentRecordDispatcher,
        timeout=None,
        encoding=None
    )
    s.serve_forever()
