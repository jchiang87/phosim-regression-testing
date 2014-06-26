Regression Testing for phosim
=============================

These are scripts to do basic regression testing of the phosim code.

* **regression.py**: This generates an input catalog of stars which
  are distributed throughout the focal plane with a specified
  magnitude.  A set of default configuration commands are taken from
  the default_instcat file. A subset of the 189 science sensors are
  simulated and the output files are copied to a local directory. The
  number of stars, their nominal count, the number of sensors to
  simulate, and the random seed are all configurable.  Backgrounds are
  turned off.

* **compare_output.py**: This does a file-by-file comparison of all of
  the saved output files for a reference dataset with a target
  dataset.  For FITS files (.fits or .fits.gz extensions), it uses
  fdiff since GNU diff will report differences, even though the FITS
  data are identical.

* **default_instcat**: A copy of the default_instcat in the phosim
  install directory.

* **setup.[c]sh**: Setup scripts to add the install directory to the 
  user's PYTHONPATH.
