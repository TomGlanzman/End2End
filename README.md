# End2End
Prepare data and workflow to exercise many/all LSST/DESC processing steps

I. Prepare DM repo containing a selection of ingested simulated sky images.

- Identify source of image data (either simulation code output, or ingested 'raw' data)
- run tract2visit.py to summarize sky coverage in an sqlite3 database
- Define area of sky to target for testing (tract list)
- select specific sensor-visits based on tract2visit db -> image file list
- prepare DM repository with calibs, BF kernels, ref cats, and images

- once verified, create a tar file of virgin repository (no reruns) to
  serve as future starting points



II. end-to-end workflow.  Eventually, this may include initial catalog
generation (stars, galaxies, lenses, transients, etc.), simulation,
and DRP.  Maybe other steps, as needed.

