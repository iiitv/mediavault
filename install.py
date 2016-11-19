#!/usr/bin/python3

import subprocess

if __name__ == '__main__':
    print('Initiating prerequisite check...\n\n')
    print('Checking pip3...')
    subprocess.call('pip --version', shell=True)
    print('\tFound\n')
    print('Checking SQLite3')
    subprocess.call('sqlite3 --version', shell=True)
    print('\tFound\n')
    print('All prerequisites satisfied')
    print('Starting installation')
    print('Installing pip3 requirements...')
    subprocess.call('sudo -H pip3 install -r requirements.txt', shell=True)
    print('Done with installing requirements.\n\n')
    print('Removing old database..')
    subprocess.call('rm mediavault/db.sqlite3', shell=True)
    print('Making new migrations..')
    subprocess.call('cd mediavault && python3 manage.py makemigrations',
                    shell=True)
    print('Creating new database..')
    subprocess.call('cd mediavault && python3 manage.py migrate', shell=True)
    print('Creating first master user..')
    subprocess.call('cd mediavault && python3 manage.py createsuperuser',
                    shell=True)

    print('\n\n\nInstallation completed successfully.')