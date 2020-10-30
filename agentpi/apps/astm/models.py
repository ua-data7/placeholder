"""Database models."""
import datetime
import logging
import json
import pprint
import requests

from sqlalchemy.types import CHAR
from sqlalchemy.dialects.postgresql import JSONB

from agentpi import db


logger = logging.getLogger(__name__)
pp = pprint.PrettyPrinter(indent=4)


# LIS1-A spec
class LISDatagram(db.Model):
    """
    HEADER / TERMINATOR -> Full datagram
    """
    __tablename__ = 'lis_datagram'

    id = db.Column('dgid', db.Integer, primary_key=True)
    # HEADER
    instrument_model = db.Column(
        db.String(12),
        index=False,
        unique=False,
        nullable=True
    )
    instrument_serial_number = db.Column(
        db.String(12),
        index=False,
        unique=False,
        nullable=True
    )
    instrument_firmware = db.Column(
        db.String(12),
        index=False,
        unique=False,
        nullable=True,
    )
    instrument_timestamp = db.Column(
        db.DateTime,
        index=False,
        unique=False,
        nullable=True
    )
    # Data stream
    messages = db.Column(JSONB)  # WARNING: Object is Immutable!!!
    # GENERAL
    created_at = db.Column(
        db.DateTime,
        default=datetime.datetime.utcnow,
        index=False,
        unique=False,
        nullable=True
    )

    is_vialid_uaxx = db.Column(db.Boolean, unique=False, default=False)
    is_vialid_test = db.Column(db.Boolean, unique=False, default=False)
    is_uploaded = db.Column(db.Boolean, unique=False, default=False)
    is_error = db.Column(db.Boolean, unique=False, default=False)
    is_skipped = db.Column(db.Boolean, unique=False, default=False)

    # results = db.relationship("ASTMResult", backref="datagram", lazy='dynamic')
    patient = db.relationship("LISPatient", uselist=False)
    order = db.relationship("LISOrder", uselist=False)
    comments = db.relationship("LISComment", backref="datagram", lazy='dynamic')
    results = db.relationship("LISResult", backref="datagram", lazy='dynamic')

    def __repr__(self):
        return f"<ASTM Message {self.id}>"

    @classmethod
    def create_without_fail(cls, **kwargs):
        try:
            obj = cls(**kwargs)
            db.session.add(obj)
            db.session.commit()
        except Exception as e:
            ## DO NOT BREAK!!!
            logger.error("WARNING -> DB failure on LISDatagram")
            logger.error(str(e))
            return None
        else:
            logger.info(f"+LISDatagram(id={obj.id})")
            return obj


class LISPatient(db.Model):
    """
    Patient data (OneToOne -> LISDatagram)
    """
    __tablename__ = 'lis_patient'
    id = db.Column('pid', db.Integer, primary_key=True)
    patient_id = db.Column(
        db.String(12),
        index=False,
        unique=False,
        nullable=True,
    )
    location = db.Column(
        db.String(32),
        index=False,
        unique=False,
        nullable=True,
    )
    dgid = db.Column(db.Integer, db.ForeignKey('lis_datagram.dgid'))
    datagram = db.relationship('LISDatagram')

    @classmethod
    def create_without_fail(cls, **kwargs):
        """
        """
        try:
            obj = cls(**kwargs)
            db.session.add(obj)
            db.session.commit()
        except Exception as e:
            ## DO NOT BREAK!!!
            logger.error("WARNING -> DB failure on LISPatient")
            logger.error(str(e))
            return None
        else:
            logger.info(f"+LISPatient(id={obj.id})")
            return obj


class LISOrder(db.Model):
    """
    Order
    """
    __tablename__ = 'lis_order'
    id = db.Column('oid', db.Integer, primary_key=True)
    order_id = db.Column(
        db.String(12),
        index=False,
        unique=False,
        nullable=True,
    )
    test_type = db.Column(
        db.String(12),
        index=False,
        unique=False,
        nullable=True,
    )
    operator_id = db.Column(
        db.String(12),
        index=False,
        unique=False,
        nullable=True,
    )
    sample_type = db.Column(
        CHAR,
        index=False,
        unique=False,
        nullable=True,
    )
    dgid = db.Column(db.Integer, db.ForeignKey('lis_datagram.dgid'))
    datagram = db.relationship('LISDatagram')

    @classmethod
    def create_without_fail(cls, **kwargs):
        """
        """
        try:
            obj = cls(**kwargs)
            db.session.add(obj)
            db.session.commit()
        except Exception as e:
            ## DO NOT BREAK!!!
            logger.error("WARNING -> DB failure on LISOrder")
            logger.error(str(e))
            return None
        else:
            logger.info(f"+LISOrder(id={obj.id})")
            return obj


class LISComment(db.Model):
    """
    Comment (ManyToOne) -> LISDatagram
    """
    __tablename__ = 'lis_comment'
    id = db.Column('cid', db.Integer, primary_key=True)
    sample_comment = db.Column(
        db.String(64),
        index=False,
        unique=False,
        nullable=True,
    )
    dgid = db.Column(db.Integer, db.ForeignKey('lis_datagram.dgid'))
    # datagram = db.relationship('LISDatagram')

    @classmethod
    def create_without_fail(cls, **kwargs):
        """
        """
        try:
            obj = cls(**kwargs)
            db.session.add(obj)
            db.session.commit()
        except Exception as e:
            ## DO NOT BREAK!!!
            logger.error("WARNING -> DB failure on LISComment")
            logger.error(str(e))
            return None
        else:
            logger.info(f"+LISComment(id={obj.id})")
            return obj


class LISResult(db.Model):
    __tablename__ = 'lis_result'
    id = db.Column('rid', db.Integer, primary_key=True)
    analyte_name = db.Column(
        db.String(12),
        index=False,
        unique=False,
        nullable=True
    )
    test_value = db.Column(
        db.String(12),
        index=False,
        unique=False,
        nullable=True
    )
    test_units = db.Column(
        db.String(12),
        index=False,
        unique=False,
        nullable=True
    )
    test_range = db.Column(
        db.String(12),
        index=False,
        unique=False,
        nullable=True
    )
    test_flag = db.Column(
        db.String(12),
        index=False,
        unique=False,
        nullable=True
    )
    test_type = db.Column(
        CHAR,
        index=False,
        unique=False,
        nullable=True
    )
    completion = db.Column(
        db.DateTime,
        index=False,
        unique=False,
        nullable=True
    )
    dgid = db.Column(db.Integer, db.ForeignKey('lis_datagram.dgid'))
    # datagram = db.relationship('LISDatagram')

    @classmethod
    def create_without_fail(cls, **kwargs):
        """
        """
        try:
            obj = cls(**kwargs)
            db.session.add(obj)
            db.session.commit()
        except Exception as e:
            ## DO NOT BREAK!!!
            logger.error("WARNING -> DB failure on LISComment")
            logger.error(str(e))
            return None
        else:
            logger.info(f"+LISComment(id={obj.id})")
            return obj

def publish_results(current_app):
    """
    """
    from agentpi.apps.astm.models import LISDatagram
    lds = db.session.query(LISDatagram)
    stop_this = False
    for ld in lds:
        if(not ld.is_vialid_uaxx):
            continue
        print(f"{ld.id}:{ld.patient.patient_id} - is_uploaded: {ld.is_uploaded} - is_error: {ld.is_error} - is_skipped: {ld.is_skipped}")
        results = ld.results.all()
        if(len(results) == 1):
            if(not ld.is_uploaded and ld.is_error):
                url = current_app.config['SARS_UPLINK_API_URL']
                key = current_app.config['SARS_UPLINK_API_KEY']
                payload = {
                    'vialId': ld.patient.patient_id,
                    'testType': ld.order.test_type,
                    'results': results[0].test_value,
                    'serialNo': ld.instrument_serial_number,
                    'resultTime': results[0].completion.strftime("%Y%m%d%H%M%S") if results[0].completion else ''
                }
                headers = {
                    'Content-Type': 'application/json',
                    'x-api-key': key
                }
                if(results[0].completion > datetime.datetime(2020,10,15,0,0,0)):
                    print("PUBLISHING...")
                    print(f"url: {url}")
                    pp.pprint(payload)
                    try:
                        stop_this = True
                        res = requests.post(url, data=json.dumps(payload), headers=headers)
                        res.raise_for_status()
                    except requests.exceptions.HTTPError as e:
                        logger.error(repr(e))
                        logger.error(f"url: '{url}'")
                        logger.error(f"HTTP error with patient_id: '{payload['vialId']}'")

                    except requests.exceptions.ConnectionError as e:
                        logger.error(repr(e))
                        logger.error(f"url: '{url}'")
                        logger.error(f"Connection error with patient_id: '{payload['vialId']}'")

                    except requests.exceptions.Timeout as e:
                        logger.error(repr(e))
                        logger.error(f"url: '{url}'")
                        logger.error(f"Timeout with patient_id '{payload['vialId']}'")

                    except (requests.exceptions.RequestException, Exception) as e:
                        logger.error(repr(e))
                        logger.error(f"url: '{url}'")
                        logger.error(f"Unknown error with patient_id '{payload['vialId']}'")
                    else:
                        if(res.status_code == 200):
                            # Successfully uploaded data
                            ld.is_uploaded = True
                            ld.is_error = False
                            db.session.commit()
                        else:
                            # This should be impossible
                            logger.error(f"HTTP ERROR '{res.status_code}': : {payload['vialId']}")
        else:
            print(f"Couldn't upload [patient_id]: {ld.patient.patient_id}")
        # if(stop_this):
        #     break


def show_results(current_app):
    """
    """
    from agentpi.apps.astm.models import LISDatagram
    lds = db.session.query(LISDatagram)
    for ld in lds:
        results = ld.results.all()
        if(results[0].completion > datetime.datetime(2020,10,15,0,0,0)):
            print(
                f"[{ld.id}]:[{ld.patient.patient_id}] - is_uploaded: "
                f"{ld.is_uploaded} - is_error: {ld.is_error} - "
                f"is_skipped: {ld.is_skipped} - is_vialid_uaxx: "
                f"{ld.is_vialid_uaxx}"
            )

__all__ = [
    'LISDatagram', 'LISPatient', 'LISOrder', 'LISComment', 'LISResult'
]
