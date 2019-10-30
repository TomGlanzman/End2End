# Create symlinks between i-band flat calib files and flats for ugrzy bands.
#
#  Revised 30 Oct 2019 - TG

# Script must be executed from 'CALIB' directory
# symlinks are *RELATIVE* so that the CALIB directory is relocatable
#  Note this requires intimate knowledge of the DM file structure

import os
import glob
import sqlite3

calib_dir = os.path.abspath('.')
iband_flats = sorted(glob.glob(os.path.join(calib_dir, 'flat', 'i',
                                            '2022-08-06', 'flat_i-R*')))
for band in 'ugrzy':
    flat_dir = os.path.join(calib_dir, 'flat', band, '2022-08-06')
#    print('band ',band,', flat_dir=',flat_dir)
    os.makedirs(flat_dir, exist_ok=True)
    os.chdir(flat_dir)
    
    for iflat in iband_flats:
        ofile = os.path.basename(iflat).replace('i-R', '{}-R'.format(band))
        rpath = os.path.relpath(os.path.dirname(iflat),flat_dir)
        riflat = os.path.join(rpath,os.path.basename(iflat))
        try:
            os.symlink(riflat,ofile)
        except FileExistsError:
            pass
    pass
os.chdir(calib_dir)

# Update the calibRegistry.sqlite3 file with entries for the flats
# in the ugrzy bands.
conn = sqlite3.connect('calibRegistry.sqlite3')
curs = conn.cursor()

# Get the entries for the i-band flats.
query = 'select raftName, detectorName, detector, calibDate, validStart, validEnd from flat where filter="i"'
curs.execute(query)
entries = [x for x in curs]

for band in 'ugrzy':
    for row in entries:
        my_row = [band] + list(row)
        query = "insert into flat (filter, raftName, detectorName, detector, calibDate, validStart, validEnd) values ('{}', '{}', '{}', {}, '{}', '{}', '{}')".format(*my_row)
        try:
            curs.execute(query)
        except sqlite3.IntegrityError:
            pass
    conn.commit()
