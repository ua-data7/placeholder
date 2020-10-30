import re
import logging
import netifaces as ni
from datetime import datetime

from astm import client
from astm.records import (
    HeaderRecord, PatientRecord, OrderRecord, TerminatorRecord
)

from agentpi.library import is_ipv4
from .records import (
    QuidelHeaderRecord, QuidelPatientRecord, QuidelOrderRecord,
    QuidelCommentRecord, QuidelResultRecord
)


logger = logging.getLogger(__name__)


test_string_01 = [
    b'\x021H|\\^&|||Sofia^29000021|||||||P|1.7.0|20200727154724\r\x03AD\r\n',
    b'\x022P|1|TST1-0000001|||||||||||||||||||||||reallylonglocation|\r\x03A1\r\n',
    b'\x023O|1|TST1-0000001||SARS||||||1234|||||P\r\x031C\r\n',
    b'\x024C|1||Read-Now Mode\r\x03AE\r\n',
    b'\x025R|1|^^^SARS|negative|||||F||||20200727154712\r\x034C\r\n',
    b'\x026L|1|N\r\x0309\r\n'
]

## TEST PASSED

# FAKEd : b'\x021H|\\^&|||Sofia^29000021|||||||P|1.7.0|20200727154724\r\x03A2\r\n' 
# REAL  : b'\x021H|\\^&|||Sofia^29000021|||||||P|1.7.0|20200727154724\r\x03AD\r\n'

# FAKEd : b'\x022P|1|TST1-0000001|||||||||||||||||||||||\r\x0389\r\n'
# REAL  : b'\x022P|1|TST1-0000001|||||||||||||||||||||||\r\x03A1\r\n'

# FAKEd : b'\x023O|1|TST1-0000001||SARS||||||1234|||||P\r\x0304\r\n'
# REAL  : b'\x023O|1|TST1-0000001||SARS||||||1234|||||P\r\x031C\r\n'

# FAKEd : b'\x024C|1||Read-Now Mode\r\x03AE\r\n'
# REAL  : b'\x024C|1||Read-Now Mode\r\x03AE\r\n'

# FAKEd : b'\x025R|1|^^^SARS|negative|||||F||||20200727154712\r\x034C\r\n' 
# REAL  : b'\x025R|1|^^^SARS|negative|||||F||||20200727154712\r\x034C\r\n'

# FAKEd : b'\x026L|1|N\r\x0309\r\n'
# REAL  : b'\x026L|1|N\r\x0309\r\n'


test_string_02 = [
    b'\x021H|\\^&|||Sofia^29000021|||||||P|1.7.0|20200727155632\r\x03AC\r\n',
    b'\x022P|1|TST1-0000002|||||||||||||||||||||||\r\x03A9\r\n',
    b'\x023O|1|TST1-0000002||SARS||||||1234|||||P\r\x0324\r\n',
    b'\x024C|1||Read-Now Mode\r\x03AE\r\n',
    b'\x025R|1|^^^SARS|negative|||||F||||20200727155620\r\x034B\r\n',
    b'\x026L|1|N\r\x0309\r\n'
]

test_string_03 = [
    b'\x021H|\\^&|||Sofia^29000021|||||||P|1.7.0|20200727153957\r\x03B4\r\n',
    b'\x022P|1|UA01-TEST001|||||||||||||||||||||||\r\x0319\r\n',
    b'\x023O|1|||SARS|||||||||||P\r\x0390\r\n',
    b'\x024C|1||Read-Now Mode\r\x03AE\r\n',
    b'\x025R|1|^^^SARS|positive|||||F||||20200605135056\r\x0367\r\n',
    b'\x026L|1|N\r\x0309\r\n'
]

test_string_04 = [
    b'\x021H|\\^&|||Sofia^29000021|||||||P|1.7.0|20200727153952\r\x03AF\r\n',
    b'\x022P|1|UA01-TEST002|||||||||||||||||||||||\r\x0389\r\n',
    b'\x023O|1|||SARS|||||||||||P\r\x0390\r\n',
    b'\x024C|1||Read-Now Mode\r\x03AE\r\n',
    b'\x025R|1|^^^SARS|negative|||||F||||20200603132814\r\x0344\r\n',
    b'\x026L|1|N\r\x0309\r\n'
]

def generate_record_from_byte_string(input):
    unicode_string = ''.join([chr(x) for x in input])
    clean_string1 = re.sub(r'^\x02', '', unicode_string)  # drop 1st character (\x02)
    clean_string2 = re.sub(r'\r\x03[A-F0-9]{2}\r\n$', '', clean_string1)  # drop last character \r\x03...
    record = clean_string2.split('|')

    if(record[0] == '1H'):
        # HEADER
        qhr = QuidelHeaderRecord()
        qhr.instrument = record[4]
        qhr.firmware = record[12]
        qhr.timestamp = datetime.strptime(
            record[13],
            "%Y%m%d%H%M%S"
        )
        return qhr
    elif(record[0] == '2P'):
        # PATIENT
        qpr = QuidelPatientRecord()
        qpr.patient_id = record[2]
        qpr.location = record[25]
        return qpr
    elif(record[0] == '3O'):
        qor = QuidelOrderRecord()
        qor.order_id = record[2]
        qor.test_type = record[4]
        qor.operator_id = record[10]
        qor.sample_type = record[15]
        return qor
    elif(record[0] == '4C'):
        qcr = QuidelCommentRecord()
        qcr.sample_comment = record[3]
        return qcr
    elif(record[0] == '5R'):
        qrr = QuidelResultRecord()
        qrr.analyte_name = record[2]
        qrr.test_value = record[3]
        qrr.test_units = record[4]
        qrr.test_range = record[5]
        qrr.test_flag = record[6]
        qrr.test_type = record[8]
        qrr.completion = datetime.strptime(
            record[12],
            "%Y%m%d%H%M%S"
        )
        return qrr
    elif(record[0] == '6L'):
        return TerminatorRecord()
    else:
        raise Exception(f"Malformed string: {input}")


def string_emitter():
    """
    Given recorded strings, emit LIS1-A messaging...
    """
    emit_list = [
       generate_record_from_byte_string(x) for x in test_string_01
    ]
    patient = False
    for gr in emit_list:
        if gr.type == 'H':
            assert (yield gr), 'header was rejected'
        elif gr.type == 'P':
            patient = yield gr
        elif gr.type in ['O', 'C', 'R'] and patient:
            assert (yield gr)
        elif gr.type == 'L':
            yield gr
        else:
            yield TerminatorRecord()


def emitter():
    qhr = QuidelHeaderRecord()
    qhr.model = 'Sopfia'
    qhr.serial = '29000021'
    qhr.firmware = '1.7.0'
    qhr.timestamp = '20000101000000'

    qprs = []
    qors = []
    qcrs = []
    qrrs = []
    for i in range(2, 3):
        qpr = QuidelPatientRecord()
        qpr.patient_id = f'TST1-{i:07d}'
        qpr.location = ':)'
        qprs.append(qpr)

        qor = QuidelOrderRecord()
        qor.sample_id = f'TST1-{i:07d}'
        qor.test = 'SARS'
        qor.operator_id = '1234'
        qor.sample_type = 'T'
        qors.append(qor)

        qcr = QuidelCommentRecord()
        qcr.sample_comment = 'Read-Now Mode'
        qcrs.append(qcr)

        qrr = QuidelResultRecord()
        qrr.analyte_name = '^^^Flu A'
        qrr.test_value = 'positive'
        qrr.test_units = ''
        qrr.test_range = ''
        qrr.test_flag = ''
        qrr.test_type = 'F'
        qrr.completion = datetime.now()
        qrrs.append(qrr)

    assert (yield qhr), 'header was rejected'
    ok = yield qprs[0]
    if ok:
        assert (yield qors[0])
        assert (yield qcrs[0])
        assert (yield qrrs[0])
    yield TerminatorRecord()


def run_client(current_app):
    astm_nic = current_app.config['DEFAULT_LIS_NIC']
    astm_port = int(current_app.config['DEFAULT_LIS_PORT'])
    if(is_ipv4(astm_nic)):
        ip = astm_nic
    else:
        try:
            ni.ifaddresses(astm_nic)
            ip = ni.ifaddresses(astm_nic)[ni.AF_INET][0]['addr']
        except Exception as e:
            print(str(e))
            return
    logger.info(f"Launching client service on {astm_nic}: {ip}:{astm_port}")
    c = client.Client(
        string_emitter,
        host=ip,
        port=astm_port,
        encoding=None,
        timeout=10,
    )
    c.run()
