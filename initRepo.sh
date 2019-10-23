#/bin/bash

## initRepo.sh - establish a DM-style repository for singleFrameDriver, et al
## Started 7/19/2019 at Hack Day with Heather and Johann

## NOTE: you must have a DM environment set up prior to running this
## script.


echo `date`"  Entering initRepo.sh"
 
PWDSAVE=$PWD

##### Initialize output repo (but only once!)
###if [ ! -d ${PT_REPODIR} ]; then
    mkdir ${PT_REPODIR}
    cd ${PT_REPODIR}

    echo "lsst.obs.lsst.imsim.ImsimMapper" > ${PT_REPODIR}/_mapper

    # echo `date` " [Setup CALIB]"
    tar -xvzf /global/projecta/projectdirs/lsst/production/DC2_ImSim/Run2.1i/CALIB/CALIB_run2-1i-v1.tar.gz
    echo "[rc = "$?"]"
    cd CALIB
    python symlink_flats.py      ## Link all filters to i-band
    echo "[rc = "$?"]"
    cd ..

    ## Copy in Reference Catalogs
    echo `date` " [Setup Reference Catalogs]"
    tar -xvf /global/projecta/projectdirs/lsst/production/DC2_ImSim/Run2.1i/ref_cats/ref_cat-v3/dc2_run2.1i_ref_cats_190513-v3.tar

    ## Copy in the (fake) brighter-fatter gains
    echo `date` " [Setup BF gains]"
    #mkdir ${PT_REPODIR}/calibrations
    #cp -pr ${PT_REPODIR}/../fake/bfGain*.pkl ${PT_REPODIR}/calibrations
    cp -pr /global/projecta/projectdirs/lsst/production/DC2_ImSim/Run2.1i/CALIB/bfkernels-v1/calibrations ${PT_REPODIR}

    ## Ingest some simulated data
    echo `date` " [ingestDriver.py image data]"
    # Note that "--cores" can probably be '1' as we're only creating sym-links
    ingestDriver.py ${PT_REPODIR} @$PWDSAVE/${PT_INGEST} --cores 5 --mode link --output ${PT_REPODIR} -c allowError=True register.ignore=True
    echo "[rc = "$?"]"

    cd $PWDSAVE    # return to original directory
# else
#     echo "%ALERT: the requested repo directory already exists.  No action taken"
#     echo ${PT_REPODIR}
# fi


echo `date`"  Exiting initRepo.sh"
 

exit 
