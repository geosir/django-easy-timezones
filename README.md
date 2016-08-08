![Timezones. Yuck.](http://i.imgur.com/Qc2W47H.gif)

django-easy-timezones [![Build Status](https://travis-ci.org/Miserlou/django-easy-timezones.svg)](https://travis-ci.org/Miserlou/django-easy-timezones) [![PyPI](https://img.shields.io/pypi/dm/django-easy-timezones.svg?style=flat)](https://pypi.python.org/pypi/django-easy-timezones/)
=====================

Easy IP-based timezones for Django (>=1.7) based on MaxMind GeoIP, with IPv6 support.

Quick start
-----------

1. Install django-easy-timezones

    ```python
    pip install django-easy-timezones
    ```

1. Add "easy-timezones" to your INSTALLED_APPS setting like this:

    ```python
    INSTALLED_APPS = (
      ...
      'easy_timezones',
    )
    ```

1. Add EasyTimezoneMiddleware to your MIDDLEWARE_CLASSES 

    ```python
    MIDDLEWARE_CLASSES = (
      ...
      'easy_timezones.middleware.EasyTimezoneMiddleware',
    )
    ```

1. Tell EasyTimezones where your [MaxMind GeoLite2 City Database](http://dev.maxmind.com/geoip/geoip2/geolite2/) is in your settings.py. Here's a [direct download link](http://geolite.maxmind.com/download/geoip/database/GeoLite2-City.mmdb.gz).

    ```python
    GEOIP2_DATABASE = '/path/to/your/geoip2/database/GeoLite2-City.mmdb'
    ```

    Need the [legacy MaxMind GeoIP cities databases](http://dev.maxmind.com/geoip/legacy/geolite/)? No problem! Just include both the IPv4 and IPv6 versions like this:

    ```python
    GEOIP_DATABASE = '/path/to/your/geoip/database/GeoLiteCity.dat'
    GEOIPV6_DATABASE = '/path/to/your/geoip/database/GeoLiteCityv6.dat'
    ```

1. Enable localtime in your templates.

    ```python
    {% load tz %}
        The UTC time is {{ object.date }}
    {% localtime on %}
        The local time is {{ object.date }}
    {% endlocaltime %}
    ```
1. Twist one up, cause you're done, homie!

## Signals

You can also use signals to perform actions based on the timezone detection.

1. To hook into the Timezone detection event to, say, save it to the request's user somewhere more permanent than a session, do something like this:

	```python
	from easy_timezones.signals import detected_timezone	

	@receiver(detected_timezone, sender=MyUserModel)
	def process_timezone(sender, instance, timezone, **kwargs):
    	if instance.timezone != timezone:
        	instance.timezone = timezone
        	instance.save()
	```
