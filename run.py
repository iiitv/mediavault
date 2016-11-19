#!/usr/bin/python3
import subprocess

if __name__ == '__main__':
    print('The server may run on following IPs - ')
    subprocess.call('ifconfig | grep inet\ addr', shell=True)
    print('on port 8000')
    subprocess.call('cd mediavault && python3 manage.py runserver 0.0.0.0:8000',
                    shell=True)
