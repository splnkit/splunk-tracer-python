""" Utility functions
"""
import random
import sys
import time
import math
import socket
import struct
from . import constants

guid_rng = random.Random()   # Uses urandom seed


def _collector_url_from_hostport(secure, host, port):
    """
    Create an appropriate collector URL given the parameters.

    `secure` should be a bool.
    """
    if secure:
        protocol = 'https://'
    else:
        protocol = 'http://'

    return ''.join([protocol, host, ':', str(port), '/services/collector'])


def _generate_guid():
    """
    Construct a guid - a random 64 bit integer
    """
    return guid_rng.getrandbits(64) - 1

def _id_to_hex(id):
    return '{0:x}'.format(id)

def _now_micros():
    """
    Get the current time in microseconds since the epoch.
    """
    return _time_to_micros(time.time())

def _time_to_micros(t):
    """
    Convert a time.time()-style timestamp to microseconds.
    """
    return math.floor(round(t * constants.SECONDS_TO_MICRO))

def _time_to_seconds_nanos(t):
    """
    Convert a time.time()-style timestamp to a tuple containing
    seconds and nanoseconds.
    """
    seconds = int(t)
    nanos = int((t - seconds) * constants.SECONDS_TO_NANOS)
    return (seconds, nanos)

def _merge_dicts(*dict_args):
    """Destructively merges dictionaries, returns None instead of an empty dictionary.

    Elements of dict_args can be None.
    Keys in latter dicts override those in earlier ones.
    """
    result = {}
    for dictionary in dict_args:
        if dictionary:
            result.update(dictionary)
    return result if result else None

if sys.version_info[0] == 2:

    # Coerce to ascii (bytes) under Python 2.
    def _coerce_str(val):
        return _coerce_to_bytes(val)
else:

    # Coerce to utf-8 under Python 3.
    def _coerce_str(val):
        return _coerce_to_unicode(val)

def _coerce_to_bytes(val):
    if isinstance(val, bytes):
        return val
    try:
        return val.encode('utf-8', 'replace')
    except Exception:
        try:
            return bytes(val)
        except Exception:
            # Never let these errors bubble up
            return '(encoding error)'

def _coerce_to_unicode(val):
    if isinstance(val, str):
        return val
    try:
        return val.decode('utf-8')
    except Exception:
        try:
            return str(val)
        except Exception:
            # Never let these errors bubble up
            return '(encoding error)'

def local_ip():
    """Get the local network IP of this machine"""
    try:
        ip = socket.gethostbyname(socket.gethostname())
    except IOError:
        ip = socket.gethostbyname('localhost')
    if ip.startswith('127.'):
        ip = get_local_ip_by_interfaces()
        if ip is None:
            ip = get_local_ip_by_socket()
    return ip


def get_local_ip_by_socket():
    # Explanation : https://stackoverflow.com/questions/166506
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except IOError:
        ip = None
    finally:
        s.close()
    return ip


def get_local_ip_by_interfaces():
    ip = None
    # Check eth0, eth1, eth2, en0, ...
    interfaces = [
        i + bytes(n) for i in (b'eth', b'en', b'wlan') for n in range(3)
    ]  # :(
    for interface in interfaces:
        try:
            ip = interface_ip(interface)
            if ip is not None:
                break
        except IOError:
            pass
    return ip


def interface_ip(interface):
    try:
        import fcntl
        """Determine the IP assigned to us by the given network interface."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(
            fcntl.ioctl(
                sock.fileno(), 0x8915, struct.pack('256s', interface[:15])
            )[20:24]
        )
    except ImportError:
        return None
