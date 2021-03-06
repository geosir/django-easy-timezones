from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured
from django.utils import timezone
import pytz
import pygeoip
import geoip2.database
import os

from .signals import detected_timezone
from .utils import get_ip_address_from_request, is_valid_ip, is_local_ip

db_loaded = False
using_geoip2 = False
db = None
db_v6 = None

def load_db_settings():
    
    # Using MaxMind's GeoLite2 City Database
    GEOIP2_DATABASE = getattr(settings, 'GEOIP_DATABASE', 'GeoLite2-City.mmdb')
    
    if not GEOIP2_DATABASE:
        GEOIP_DATABASE = getattr(settings, 'GEOIP_DATABASE', 'GeoLiteCity.dat')

        if not GEOIP_DATABASE:
            raise ImproperlyConfigured("One of GEOIP2_DATABASE or GEOIP_DATABASE must be defined.")

        if not os.path.exists(GEOIP_DATABASE):
            raise ImproperlyConfigured("GEOIP_DATABASE setting is defined, but file does not exist.")

        GEOIPV6_DATABASE = getattr(settings, 'GEOIPV6_DATABASE', 'GeoLiteCityv6.dat')

        if not GEOIPV6_DATABASE:
            raise ImproperlyConfigured("GEOIPV6_DATABASE setting has not been properly defined.")

        if not os.path.exists(GEOIPV6_DATABASE):
            raise ImproperlyConfigured("GEOIPV6_DATABASE setting is defined, but file does not exist.")
    else:
        if not os.path.exists(GEOIP2_DATABASE):
            raise ImproperlyConfigured("GEOIP2_DATABASE setting is defined, but file does not exist.")
        
        GEOIP_DATABASE = None
        GEOIPV6_DATABASE = None

    return (GEOIP2_DATABASE, GEOIP_DATABASE, GEOIPV6_DATABASE)

load_db_settings()

def load_db():

    GEOIP2_DATABASE, GEOIP_DATABASE, GEOIPV6_DATABASE = load_db_settings()

    global db, using_geoip2
    if GEOIP2_DATABASE:
        db = geoip2.database.Reader(GEOIP2_DATABASE)
        using_geoip2 = True
    else:
        db = pygeoip.GeoIP(GEOIP_DATABASE, pygeoip.MEMORY_CACHE)

        global db_v6
        db_v6 = pygeoip.GeoIP(GEOIPV6_DATABASE, pygeoip.MEMORY_CACHE)

    global db_loaded
    db_loaded = True

class EasyTimezoneMiddleware(object):
    def process_request(self, request):
        """
        If we can get a valid IP from the request,
        look up that address in the database to get the appropriate timezone
        and activate it.

        Else, use the default.

        """

        if not request:
            return

        if not db_loaded:
            load_db()

        tz = request.session.get('django_timezone')

        if not tz:
            # use the default timezone (settings.TIME_ZONE) for localhost
            tz = timezone.get_default_timezone()

            client_ip = get_ip_address_from_request(request)
            ip_addrs = client_ip.split(',')
            for ip in ip_addrs:
                if is_valid_ip(ip) and not is_local_ip(ip):
                    if using_geoip2:
                        tz = db.city(ip).location.time_zone
                    else:
                        if ':' in ip:
                            tz = db_v6.time_zone_by_addr(ip)
                            break
                        else:
                            tz = db.time_zone_by_addr(ip)
                            break
                        
        if tz:
            timezone.activate(tz)
            request.session['django_timezone'] = str(tz)
            if getattr(settings, 'AUTH_USER_MODEL', None):
                detected_timezone.send(sender=get_user_model(), instance=request.user, timezone=tz)
        else:
            timezone.deactivate()
