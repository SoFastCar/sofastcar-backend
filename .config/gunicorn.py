daemon = False
chdir = '/srv/sofastcar/app'
bind = 'unix:/run/sofastcar.sock'
accesslog = '/var/log/gunicorn/access.log'
errorlog = '/var/log/gunicorn/error.log'
capture_output = True
