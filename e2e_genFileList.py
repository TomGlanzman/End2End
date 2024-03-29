## e2e_genFileList.py - generate a list of sim files for ingesting into a DM repo
##
## Use the sqlite3 db generated by tract2visit.py to select those
## sensor-visits which overlap any in a list of tracts.  This list is
## then used to construct file names for a DM repo ingest step.

## Python dependencies: sqlite3

## T.Glanzman - Autumn 2019
__version__ = "0.1.0"

import sys,os
import sqlite3
#from tabulate import tabulate
import datetime
import argparse

## These are the tracts of interest for the end-to-end data set
tracts = '3636,3637,3638,3639,3830,3831,3832,4028,4029,4030,4229,4230,4231,4232'
#tracts = '3636'

## raftIDs are used when converting to/from detector numbers
raftIDs = ['R01','R02','R03','R10','R11','R12','R13','R14','R20','R21','R22','R23','R24','R30','R31','R32','R33','R34','R41','R42','R43']

class overlap(object):
    ## Table overlap contains: [id,tract,patch,visit,detector,filter,layer]
    overlapSQL = "select distinct visit,detector,filter from overlaps where tract in ($1) order by visit,detector;"
    #TEST#    overlapSQL = "select distinct * from overlaps order by visit,detector;"

    def __init__(self,dbfile='tract2visit.db',tractList=None):
        ## Instance variables
        self.dbfile = dbfile
        self.tractList = tractList
        print('dbfile = ',self.dbfile)
        print('tractList = ',self.tractList)
        self.dbInit = False
        return

    
    def __del__(self):
        ## Class destructor 
        self.con.close()
        self.dbInit = False
        return

    
    def initDB(self):
        ## Open sqlite3 DB file and create cursor
        self.con = sqlite3.connect(self.dbfile)      ## connect to sqlite3 file
        self.con.row_factory = sqlite3.Row           ## optimize output format
        self.cur = self.con.cursor()                 ## create a 'cursor'
        self.dbInit = True
        return


    def closeDB(self):
        self.con.close()
        self.dbInit = False
        return


    def stdQuery(self,sql):
        ## Perform a DB query, fetch all results and column headers
        if self.dbInit == False: return [],[]
        print('SQL = ',sql)
        result = self.cur.execute(sql)
        rows = result.fetchall()   # <-- This is a list of db rows in the result set
        ## This will generate a list of column headings (titles) for the result set
        titlez = result.description
        ## Convert silly 7-tuple title into a single useful value
        titles = []
        for title in titlez:
            titles.append(title[0])
            pass
        return rows,titles


    def run(self):
        self.initDB()
        rows,titles = self.stdQuery(self.overlapSQL.replace('$1',tracts))
        self.closeDB()
        return rows, titles
###  End of class



def d2rs(detector):
    ## Convert a DM "detector number" to raft/sensor format, e.g.,
    ## "R22" "S11"
    det = int(detector)
    if det > 189 or det < 0: raise Exception("Bad detector number")
    raft = int(det/9)
    raftID = raftIDs[raft]
    s1 = det%9
    s2 = int(s1/3)
    s3 = s1 % 3
    sensorID = f'S{s2}{s3}'
    return raftID, sensorID


def rs2d(raftID,sensorID):
    # Convert a raft sensor string of form "Rnn" and "Smm" to a DM
    # "detector number" (int from 0 to 188)
    raft = raftIDs.index(raftID)
    det = int(raft)*9+int(sensorID[-2])*3+int(sensorID[-1])
    return det



if __name__ == '__main__':

    ## Define defaults
    defaultFile = 'tract2visit.db'
    defsimpre = '/global/projecta/projectdirs/lsst/production/DC2_ImSim/Run2.1.1i/sim/agn-test'

    
    ## Parse command line arguments
    parser = argparse.ArgumentParser(description='Generate sim file list based on tract overlap')
    parser.add_argument('-o','--overlapsFile',default=defaultFile,help='Name of overlap db file (default = %(default)s)')
    parser.add_argument('-v','--version', action='version', version=__version__)
    parser.add_argument('-s','--simFileList',default=None,help='Name of sim file list file to produce (default = %(default)s)')
    parser.add_argument('-p','--plots',action='store_true',default=False,help='Show plots')
    parser.add_argument('-P','--Prefix',default=defsimpre,help='Path prefix to raw image files (default=%(default)s)')

    args = parser.parse_args()

    print('args = ',args)
    
    ## Open and query tracts2visit (sqlite3) database
    myo = overlap(dbfile=args.overlapsFile,tractList=tracts)
    rows,titles = myo.run()

    print('table columns = ',titles)
    xvisit=titles.index('visit')
    xdet=titles.index('detector')
    xfilt=titles.index('filter')
    print('#sensor-visits returned = ',len(rows))
    # Sim FITS file naming convention:     lsst_a_425529_R14_S00_y.fits
    fileList = []
    visitList = []
    sensorList = {}
    tractList = tracts.split(',')
    print('tractList = ',tractList)
    
    ## Summarize data
    n = 0
    simpre=args.Prefix
    for rowz in rows:
        n += 1
        row = list(rowz)
        viz = row[xvisit]
        if viz not in visitList:
            visitList.append(viz)
            sensorList[viz] = []
            
        ## Construct sim file name
        rr,ss = d2rs(row[xdet])
        sensorList[viz].append(rr+'_'+ss)
        file = 'lsst_a_'+str(viz)+'_'+rr+'_'+ss+'_'+str(row[xfilt])+'.fits'
        viz8 = f'{viz:08}'
        if viz < 445379:
            file = os.path.join(simpre,'00385844to00445379',viz8,file)
        else:
            file = os.path.join(simpre,'00445379to00497969',viz8,file)
            pass
        fileList.append(file)
        #if n<20:print(file)
        pass

    ## Write out a file of sim filenames, if requested
    if args.simFileList != None:
        vz = open(args.simFileList,'w')
        for file in fileList:
            vz.write(file+'\n')
            pass
        vz.close()
        print('A list of all ',len(fileList),' sim files has been written out to ',args.simFileList)


    ## Summary
    print('There are ',len(visitList),' visits.')
    print('There are ',len(fileList),' files.')


    print('================================================\n\nPart II...')

    ## Looking further...
    import numpy as np
    import matplotlib.mlab as mlab
    import matplotlib.pyplot as plt

    sensorDist = []
    for sensor in sensorList:
        sensorDist.append(len(sensorList[sensor]))
        pass
    #print('sensorDist = ',sensorDist)
    
    #mySQL = "select visit,detector,filter,patch,tract from overlaps where tract in ("+tracts+") order by visit,detector;"
    mySQL = "select visit,detector,filter,patch,tract from overlaps order by visit,detector;"
    myo.initDB()
    rz,tz = myo.stdQuery(mySQL)
    myo.closeDB()
    print('tz = ',tz)
    print('len(rz) = ',len(rz))

    ## detectors(sensors) per visit, patches per detector
    n=0
    detDist = []
    patchDist = []
    patch2Dist = []
    viz = 0
    det = -1
    nPatch = -1
    nPatch2 = -1
    nDet = -1
    for rw in rz:
        n+=1
        row=list(rw)
        #print(n, row)
        if row[0] != viz:
            #print(n," *********************************** New visit! ",row[0])
            if nPatch != -1:
                patchDist.append(nPatch)
                patch2Dist.append(nPatch2)
                detDist.append(nDet)
                pass
            viz = row[0]
            det = row[1]
            nPatch = 0
            nPatch2 = 0
            nDet = 0
            pass
        if row[1] != det:
            #print(n," #################   New detector! ",row[1])
            det = row[1]
            patchDist.append(nPatch)
            nPatch = 0
            nDet += 1
            pass
        nPatch += 1
        nPatch2 += 1
        #print('-----------> nDet=',nDet,', nPatch=',nPatch,', nPatch2=',nPatch2)
        #if n>5000:break
        pass

    print('len(detDist) = ',len(detDist))
    #print('detDist = ',detDist)
    print('len(patchDist) = ',len(patchDist))
    print('min(patchDist) = ',min(patchDist))
    print('max(patchDist) = ',max(patchDist))
    #print('patch2Dist = ',patch2Dist)
    print('len(patch2Dist) = ',len(patch2Dist))
    print('min(patch2Dist) = ',min(patch2Dist))
    print('max(patch2Dist) = ',max(patch2Dist))


    ## Produce plots
    if args.plots:
        fig,axs = plt.subplots(1,2,tight_layout=True)
        axs[0].hist(detDist,bins=10,range=(1,190),align='left')
        axs[0].set_xlabel('Sensors per Visit (full list)')
        axs[0].set_ylabel('Frequency')
        axs[0].grid(True)
        #axs[0].title('Sensors per Visit')

        axs[1].hist(sensorDist,bins=10,range=(1,190),align='left')
        axs[1].set_xlabel('Sensors per Visit (tract selection)')
        axs[1].set_ylabel('Frequency')
        axs[1].grid(True)
        #axs[0].title('Sensors per Visit')

        # axs[1].hist(patchDist,bins=6,range=(4,10),align='left')
        # axs[1].set_xlabel('Patches per Sensor')
        # axs[1].set_ylabel('Frequency')
        # #axs[1].ticklabel_format(style='sci',scilimits=(0,0),axis='y')
        # #axs[1].title('Patches per Sensor')

        # axs[2].hist(patch2Dist,bins=50,range=(800,1200),align='left')
        # axs[2].set_xlabel('DB entries per Visit')
        # axs[2].set_ylabel('Frequency')
        # #axs[2].title('Patches per visit')

        plt.show()
        pass
    
    sys.exit()
    
