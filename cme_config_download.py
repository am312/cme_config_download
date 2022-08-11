import configparser
import ftplib
import gzip
import os
import shutil
from datetime import date


def get_config_dict():
    if not hasattr(get_config_dict, 'config_dict'):
        get_config_dict.config_dict = dict(config.items('SECTION_NAME'))
    return get_config_dict.config_dict

def delete(filename: str):
    if os.path.exists(filename):
        print('deleting ' + filename)
        os.remove(filename)

if __name__ == '__main__':
    print('starting CME file collector')

    config = configparser.RawConfigParser()
    config.read('./cme_config_download.cfg')
    cfg = dict(config.items('CME_CONFIG_DOWNLOAD'))

    collected = 0

    secdef_file = 'secdef.dat.gz'
    secdef_file_tmp = '/tmp/' + secdef_file

    config_file = 'config.xml'
    config_file_tmp = '/tmp/' + config_file

    delete(secdef_file_tmp)
    delete(config_file_tmp)

    with ftplib.FTP(cfg['hostname'], cfg['username'], cfg['password']) as ftp:
        ftp.cwd('/SBEFix/Production')
        with open(secdef_file_tmp, 'wb') as f:
            ftp.retrbinary('RETR ' + secdef_file, f.write)
            collected += 1
        ftp.cwd('/SBEFix/Production/Configuration')
        with open(config_file_tmp, 'wb') as f:
            ftp.retrbinary('RETR ' + config_file, f.write)
            collected += 1

    # TODO push collected value to datadog.  Set alert on values <2

    print('collected ' + str(collected) + ' files.')

    target_dir = cfg['data_dir']
    if os.path.exists(target_dir):
        print('path exists: ' + target_dir)
    else:
        print('create dir: ' + target_dir)
        os.makedirs(target_dir)

    start_date = date.today().strftime('%Y-%m-%d')

    secdef_file_with_date = secdef_file[:-3] + '.' + start_date + '.gz'
    secdef_file_with_path = target_dir + '/' + secdef_file_with_date

    config_file_with_date = config_file[:-4] + '.' + start_date + '.xml'
    config_file_with_path = target_dir + '/' + config_file_with_date

    os.rename(secdef_file_tmp, secdef_file_with_path)
    os.rename(config_file_tmp, config_file_with_path)

    os.chdir(target_dir)

    if os.path.isfile(secdef_file):
        secdef_target = os.readlink(secdef_file)
        delete(secdef_target)

    delete(secdef_file)
    delete(config_file)

    with gzip.open(secdef_file_with_path, 'rb') as f_in:
        with open(secdef_file[:-3], 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

    os.symlink(config_file_with_date, config_file)
