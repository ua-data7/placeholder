import re
import logging
import pprint
from datetime import datetime
import requests
import json
import copy

from flask import current_app
from flask.cli import with_appcontext

from astm.server import BaseRecordsDispatcher
from astm.records import HeaderRecord, PatientRecord, OrderRecord, CommentRecord

from agentpi import db
from .models import (
    LISDatagram, LISPatient, LISOrder, LISComment, LISResult
)
from .records import (
    QuidelHeaderRecord,
)


pp = pprint.PrettyPrinter(indent=4)
logger = logging.getLogger(__name__)


class AgentRecordDispatcher(BaseRecordsDispatcher):
    def __init__(self, encoding=None):
        super().__init__(encoding=encoding)
        # messages
        self.messages = []
        # Header
        self.is_vial_uaxx = False
        self.is_vialid_test = False
        self.is_skipped = False
        self.is_uploaded = False
        self.is_error = False

        self.datagram = {}
        self.patient = {}
        self.order = {}
        self.comments = []
        self.results = []

    def __call__(self, message):
        """
        Stash message into database before futher propagation
        """
        print(message)
        self.messages.append(message)
        super().__call__(message)

    def print_record(self, title, record):
        if type(record) == str:
            logger.info(f"{title}: {record}")
        elif type(record) == list:
            logger.info(
                f"{title}: [{', '.join([str(i or 'None') for i in record])}]"
            )

    @with_appcontext
    def on_header(self, record):
        super().on_header(record)
        notfail = not (len(record) < 14)
        if(record[4] and type(record[4]) == list):
            self.datagram['instrument_model'], self.datagram['instrument_serial_number'] = record[4]
        else:
            self.datagram['instrument_model'], self.datagram['instrument_serial_number'] = (None, None)
        self.datagram['instrument_firmware'] = record[12] if notfail else None
        self.datagram['instrument_timestamp'] = record[13] if notfail else None
        if(self.datagram['instrument_timestamp']):
            try:
                self.datagram['instrument_timestamp'] = datetime.strptime(
                    self.datagram['instrument_timestamp'],
                    "%Y%m%d%H%M%S"
                )
            except ValueError:
                logger.info(
                    f"ERROR '{self.datagram['instrument_timestamp']}'"
                    " TypeError to datetime!"
                )
                self.datagram['instrument_timestamp'] = None

    def on_patient(self, record):
        super().on_patient(record)
        notfail = not (len(record) <= 25)
        self.patient['patient_id'] = record[2] if notfail else None
        self.patient['location'] = record[25] if notfail else None

    def on_order(self, record):
        super().on_order(record)
        notfail = not (len(record) <= 15)
        self.order['order_id'] = record[2] if notfail else None
        self.order['test_type'] = record[4] if notfail else None
        self.order['operator_id'] = record[10] if notfail else None
        self.order['sample_type'] = record[15] if notfail else None

    def on_comment(self, record):
        super().on_comment(record)
        notfail = not (len(record) <= 3)
        comment = record[3] if notfail else None
        self.comments.append(comment)

    def on_result(self, record):
        super().on_result(record)
        result = {}
        notfail1 = not (len(record) <= 12)
        notfail2 = notfail1 and (not (len(record[2]) <= 3))
        result['analyte_name'] = record[2][3] if notfail2 else None
        result['test_value'] = record[3] if notfail1 else None
        result['test_units'] = record[4] if notfail1 else None
        result['test_range'] = record[5] if notfail1 else None
        result['test_flag'] = record[6] if notfail1 else None
        result['test_type'] = record[8] if notfail1 else None
        result['completion'] = record[12] if notfail1 else None
        if(result['completion']):
            try:
                result['completion'] = datetime.strptime(
                    result['completion'], "%Y%m%d%H%M%S"
                )
            except (ValueError):
                logger.error(str(b'\n'.join(self.messages)))
                logger.error(
                    f"ERROR on RESULT, field pos 12: '{result['completion']}'"
                    " TypeError to datetime!"
                )
        self.results.append(result)

    @with_appcontext
    def on_terminator(self, record):
        super().on_order(record)
        payload = self.generate_payload()
        # ONLY SEND UAXX-????? or TSTXX-?????? or TT-??? labels
        if(re.match(r'^UA[0-9]{2}-[0-9]*', payload['vialId'])):
            self.is_vialid_uaxx = True
            self.is_vialid_test = False
            self.send_payload(
                payload,
                current_app.config['SARS_UPLINK_API_URL'],
                current_app.config['SARS_UPLINK_API_KEY'],
                disable_send=current_app.config['DISABLE_UPLINK'],
            )
        elif(re.match(r'^TT[a-zA-Z0-9]*$', payload['vialId'])):
            self.is_vialid_uaxx = False
            self.is_vialid_test = True
            self.send_payload(
                payload,
                current_app.config['SARS_UPLINK_API_URL'],
                current_app.config['SARS_UPLINK_API_KEY'],
                disable_send=current_app.config['DISABLE_UPLINK'],
            )
            self.slack_message(f"testid: {payload['vialId']} sent!")
        elif(
            re.match(r'^UA[0-9]{2}-TEST[0-9]{3}$', payload['vialId']) or
            re.match(r'^TST[0-9]{1}-[0-9]{7}$', payload['vialId'])
        ):
            # UA01-TEST001 or TST1-0000001
            self.is_vialid_uaxx = False
            self.is_vialid_test = True
            self.send_payload(
                payload,
                current_app.config['TEST_UPLINK_API_URL'],
                current_app.config['TEST_UPLINK_API_KEY'],
                disable_send=current_app.config['DISABLE_UPLINK'],
            )
            self.slack_message(f"testid: {payload['vialId']} sent!")
        else:
            logger.info(f"patient_id: {payload['vialId']} skipped")
            self.is_vialid_uaxx = False
            self.is_vialid_test = False
            self.is_uploaded = False
            self.is_error = False
            self.is_skipped = True
        # # @todo: need to visually display issue on pi?
        # #### self.print_record('terminator', record)
        self.save_datagram()

    def on_unknown(self, record):
        super().on_unknown(record)
        self.print_record('unknown', record)

    @with_appcontext
    def slack_message(self, message):
        """
        Push a notice to slack
        """
        hostname = current_app.config['HOSTNAME']
        slack_webhook = current_app.config['SLACK_WEBHOOK']
        slack_webhook_enabled = current_app.config['SLACK_CHANNEL_ENABLED']
        if(slack_webhook and slack_webhook_enabled):
            payload = {
                'text': f'{hostname}: {message}'
            }
            r = requests.post(slack_webhook, data=json.dumps(payload).encode('utf-8'))
            if(r.status_code != requests.codes.ok):
                logger.error(f"Failed to send slack notfication! {r.status_code}")
                try:
                    r.raise_for_status()
                except Exception as e:
                    logger.error(str(e))
        elif(slack_webhook_enabled):
            logger.warning("Slack hook empty!")

    @with_appcontext
    def save_datagram(self):
        """
        Save all data to database!!
        """
        if(not current_app.config['DISABLE_DATABASE']):
            datagram = {
                'instrument_model': self.datagram['instrument_model'],
                'instrument_serial_number': self.datagram['instrument_serial_number'],
                'instrument_firmware': self.datagram['instrument_firmware'],
                'instrument_timestamp': self.datagram['instrument_timestamp'],
                'messages': [ x.decode('utf-8') for x in self.messages ],
                'is_vialid_uaxx': self.is_vialid_uaxx,
                'is_vialid_test': self.is_vialid_test,
                'is_uploaded': self.is_uploaded,
                'is_error': self.is_error,
                'is_skipped': self.is_skipped,
            }
            self.db_obj = LISDatagram.create_without_fail(**datagram)
            if(self.db_obj):
                # Patient
                patient = copy.deepcopy(self.patient)
                patient['dgid'] = self.db_obj.id
                self.patient_obj = LISPatient.create_without_fail(**patient)
                # Order
                order = copy.deepcopy(self.order)
                order['dgid'] = self.db_obj.id
                self.order_obj = LISOrder.create_without_fail(**order)
                # Comments
                c_objs = []
                for c in self.comments:
                    c_obj = LISComment.create_without_fail(
                        sample_comment=c,
                        dgid=self.db_obj.id
                    )
                    c_objs.append(c_obj)
                # Results
                r_objs = []
                for r in self.results:
                    r['dgid'] = self.db_obj.id
                    r_obj = LISResult.create_without_fail(**r)
                    r_objs.append(r_obj)

    def generate_payload(self):
        """
        LIS1-A data might be messy, cleanup for sending payload
        """
        patient_id = self.patient['patient_id'] if 'patient_id' in self.patient else ''
        test_type = self.order['test_type'] if 'test_type' in self.order else ''
        if(len(self.results) == 1):
            test_value = self.results[0]['test_value'] if 'test_value' in self.results[0] else ''
            completion = self.results[0]['completion'] if 'completion' in self.results[0] else ''
        elif(len(self.results) > 1):
            logger.error(f"ERROR: more than one result for patient: '{patient_id}'")
            logger.error(pprint.pformat(self.results, indent=4))
            test_value = ''
            completion = ''
            # test_value = self.results[
            #     len(self.results)
            # ]['test_value'] if 'test_value' in self.results[0] else ''
            # completion = self.results[
            #     len(self.results)
            # ]['completion'] if 'completion' in self.results[0] else ''
        else:
            logger.error(f"ERROR: no result for patient: '{patient_id}'")
            test_value = ''
            completion = ''
        return {
            'vialId': patient_id,
            'testType': test_type,
            'results': test_value,
            'serialNo': self.datagram['instrument_serial_number'] if (
                'instrument_serial_number' in self.datagram
             ) else '',
            'resultTime': completion.strftime("%Y%m%d%H%M%S")
        }

    @with_appcontext
    def send_payload(self, payload, url, key, disable_send=False):
        """
        Send our data upstream
        """
        # pp.pprint(payload)
        self.is_uploaded = False
        self.is_error = False
        headers = {
            'Content-Type': 'application/json',
            'x-api-key': key
        }
        if(not disable_send):
            try:
                res = requests.post(url,data=json.dumps(payload),headers=headers)
                res.raise_for_status()
            except requests.exceptions.HTTPError as e:
                logger.error(repr(e))
                logger.error(f"url: '{url}'")
                logger.error(f"HTTP error with patient_id: '{payload['vialId']}'")
                self.is_error = True
            except requests.exceptions.ConnectionError as e:
                logger.error(repr(e))
                logger.error(f"url: '{url}'")
                logger.error(f"Connection error with patient_id: '{payload['vialId']}'")
                self.is_error = True
            except requests.exceptions.Timeout as e:
                logger.error(repr(e))
                logger.error(f"url: '{url}'")
                logger.error(f"Timeout with patient_id '{payload['vialId']}'")
                self.is_error = True
            except (requests.exceptions.RequestException, Exception) as e:
                logger.error(repr(e))
                logger.error(f"url: '{url}'")
                logger.error(f"Unknown error with patient_id '{payload['vialId']}'")
                self.is_error = True
            else:
                if(res.status_code == 200):
                    # Successfully uploaded data
                    self.is_uploaded = True
                else:
                    # This should be impossible
                    logger.error(f"HTTP ERROR '{res.status_code}': : {payload['vialId']}")
                    self.is_error = True
            finally:
                if(self.is_error):
                    self.slack_message("@channel ERROR Detected!")
        else:
            logger.info(f"UPLINK DISABLED: {payload['vialId']} skipped")
            self.is_skipped = True
