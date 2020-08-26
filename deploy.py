#!/usr/bin/env  python3.7

import os
import subprocess
from pathlib import Path

IDENTITY_FILE = os.path.join(str(Path.home()), '.ssh', 'sofastcar.pem')
USER = 'ubuntu'
HOST = '13.209.3.76'
TARGET = f'{USER}@{HOST}'
DOCKER_IMAGE_TAG = 'hsw0905/sofastcar'
PROJECT_NAME = 'sofastcar'
ENV_FILE = os.path.join(os.path.join(str(Path.home()), 'Documents/dev', 'sofastcar-backend'), '.env')

DOCKER_OPTIONS = (
    ('--rm', ''),
    ('-it', ''),
    ('-d', ''),
    ('-p', '80:80'),
    ('-p', '443:443'),
    ('-v', '"/etc/letsencrypt:/etc/letsencrypt"'),
    ('--name', f'{PROJECT_NAME}'),
)


def run(cmd, ignore_error=False):
    process = subprocess.run(cmd, shell=True)

    if not ignore_error:
        process.check_returncode()


def ssh_run(cmd, ignore_error=False):
    run(f'ssh -o StrictHostKeyChecking=no -i {IDENTITY_FILE} {TARGET} {cmd}', ignore_error=ignore_error)


def local_build_push():
    run(f'poetry export -f requirements.txt > requirements.txt')
    run(f'docker system prune -f')
    run(f'docker build -t {DOCKER_IMAGE_TAG} .')
    run(f'docker push {DOCKER_IMAGE_TAG}')


def server_init():
    ssh_run(f'sudo apt -y update')
    ssh_run(f'sudo apt -y dist-upgrade')
    ssh_run(f'sudo apt -y autoremove')
    ssh_run(f'sudo apt -y install docker.io')


def server_pull_run():
    ssh_run(f'sudo docker pull {DOCKER_IMAGE_TAG}')
    ssh_run(f'sudo docker stop {PROJECT_NAME}', ignore_error=True)
    ssh_run(f'sudo docker system prune -f')
    ssh_run('sudo docker run {options} {tag}'.format(
        options=' '.join([f'{key} {value}' for key, value in DOCKER_OPTIONS]),
        tag=DOCKER_IMAGE_TAG
    ))


# env 비밀값들 ec2에 복사 -> (docker run 후) docker에 복사
def copy_secrets():
    run(f'scp -i {IDENTITY_FILE} {ENV_FILE} {TARGET}:/tmp')
    ssh_run(f'sudo docker cp /tmp/.env {PROJECT_NAME}:/srv/{PROJECT_NAME}')


def server_exec():
    ssh_run(f'sudo docker exec {PROJECT_NAME} python manage.py collectstatic --noinput')
    ssh_run(f'sudo docker exec -d {PROJECT_NAME} supervisord -c /srv/{PROJECT_NAME}/.config/supervisord.conf')


if __name__ == '__main__':
    try:
        print('--- DEPLOY START! ---')
        local_build_push()
        print('---> LOCAL BUILD AND PUSH COMPLETED.')
        server_init()
        print('---> SERVER INITIAL SETTINGS COMPLETED.')
        server_pull_run()
        print('---> SERVER PULL AND RUN COMPLETED.')
        copy_secrets()
        print('---> SECRETS COPY COMPLETED.')
        server_exec()
        print('---> SERVER EXECUTE COMPLETED.')
        print('--- DEPLOY SUCCESS! ---')

    except subprocess.CalledProcessError as e:
        print('--- DEPLOY FAILED... ---')
        print('CMD >> ', e.cmd)
        print('RETURNCODE >> ', e.returncode)
        print('OUTPUT >> ', e.output)
        print('STDOUT >> ', e.stdout)
        print('STDERR >> ', e.stderr)
