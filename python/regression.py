#!/usr/bin/env python
import os
import glob
from collections import OrderedDict
import shutil
import subprocess
import numpy as np
import numpy.random as random
from argparse import ArgumentParser

def sensors(phosimdir, telescope='lsst', layout='focalplanelayout.txt',
            science_only=True):
    """
    Get the list of science sensors from the focalplanelayout.txt file
    in the phosim installation area.
    """
    fpfile = os.path.join(phosimdir, 'data', telescope, layout)
    my_sensors = []
    corner_rafts = set()
    for line in open(fpfile):
        if line[0] == '#':
            continue
        sensor_id = line.split()[0]
        if sensor_id.find('_C') != -1:
            corner_rafts.add(sensor_id.split('_')[0])
        my_sensors.append(sensor_id)
    if science_only:  
        my_sensors = [x for x in my_sensors 
                      if x.split('_')[0] not in corner_rafts]
    return np.array(my_sensors)

def star(ra, dec, mag):
    "Catalog entry for a star with flat SED."
    star_template = 'object 0 %.5f %.5f %.2f ../sky/sed_flat.txt 0 0 0 0 0 0 star none none'
    return star_template % (ra, dec, mag)

def magnitude(count):
    "Approximate apparent magnitude as a function of # of incident photons."
    mref = 20.
    cref = 507967.
    return mref - 2.5*np.log10(count/cref)

class InstCat(OrderedDict):
    """
    Class to generate an instance catalog of stars randomly
    distributed over the LSST focal plane, all with the same nominal
    incident photon count.
    """
    def __init__(self, instcat):
        "instcat is the "
        super(InstCat, self).__init__()
        self.instcat = instcat
        for line in open(instcat):
            tokens = line.strip().split()
            self[tokens[0]] = ' '.join(tokens[1:])
    def _cast(self, value):
        try:
            try:
                return int(value)
            except ValueError:
                return float(value)
        except ValueError:
            return value
    def __getitem__(self, key):
        return self._cast(OrderedDict.__getitem__(self, key))
    def generate_stars(self, args):
        xmin, xmax = (self['Unrefracted_RA_deg'] - args.fov/2.,
                      self['Unrefracted_RA_deg'] + args.fov/2.)
        ymin, ymax = (self['Unrefracted_Dec_deg'] - args.fov/2.,
                      self['Unrefracted_Dec_deg'] + args.fov/2.)

        RA = random.uniform(xmin, xmax, args.nstars)
        Dec = random.uniform(ymin, ymax, args.nstars)
        # Sort by Dec to make visual searching for stars in catalog easier.
        index = np.argsort(Dec)
        self.RA = RA[index]
        self.Dec = Dec[index]
        self.mag = magnitude(args.count)
    def write(self, outfile):
        shutil.copy(self.instcat, outfile)
        output = open(outfile, 'a')
        for ra, dec in zip(self.RA, self.Dec):
            output.write(star(ra, dec, self.mag) + '\n')
        output.close()
    def ds9_regfile(self, outfile):
        header="""# Region file format: DS9 version 4.1
global color=green dashlist=8 3 width=1 font="helvetica 10 normal roman" select=1 highlite=1 dash=0 fixed=0 edit=1 move=1 delete=1 include=1 source=1
"""
        output = open(outfile, 'w')
        output.write(header)
        output.write('fk5\n')
        for ra, dec in zip(self.RA, self.Dec):
            output.write('point(%f,%f) # point=circle\n' % (ra, dec))
        output.close()

def copy_output(phosimdir, targetdir):
    #
    # Copy output image files.
    #
    try:
        output_dir = os.path.join(targetdir, 'output')
        os.makedirs(output_dir)
    except OSError:
        pass
    for item in glob.glob(os.path.join(phosimdir, 'output', '*')):
        shutil.copy(item, output_dir)
    #
    # Copy work area files.
    #
    try:
        work_dir = os.path.join(targetdir, 'work')
        os.makedirs(work_dir)
    except OSError:
        pass
    for item in glob.glob(os.path.join(phosimdir, 'work', '*')):
        shutil.copy(item, work_dir)

if __name__ == '__main__':
    parser = ArgumentParser('Regression testing for phosim')
    parser.add_argument('dest_dir', type=str,
                        help='destination directory for copies of phosim output')
    parser.add_argument('--default_instcat', type=str,
                        default=None, help='phosim configuration parameters')
    parser.add_argument('--catalog', type=str,
                        default='instcat_regression_test',
                        help='filename for instance catalog passed to phosim.py')
    parser.add_argument('-n', '--nsensors', type=int, default=5,
                        help='Number of sensors to simulate (<190)')
    parser.add_argument('--fov', type=float, default=3.5,
                        help='Field of view size (degrees)')
    parser.add_argument('--nstars', type=int, default=1000,
                        help='Number of stars to generate in focal plane')
    parser.add_argument('--count', type=int, default=100000, 
                        help='nominal number of incident photons per star')
    parser.add_argument('--seed', type=int, default=481041,
                        help='random number seed')
    parser.add_argument('--phosimdir', type=str, default=None,
                        help='phosim install directory')
    parser.add_argument('-v', '--verbose', dest='verbose', 
                        action="store_true", default=False,
                        help='Verbosity flag')
    args = parser.parse_args()

    dest_dir = args.dest_dir
    if args.default_instcat is None:
        pythonpath = os.path.split(os.path.abspath(__file__))[0]
        default_instcat = os.path.join(pythonpath, '..', 'data',
                                       'default_instcat')
    else:
        default_instcat = args.instcat

    my_instcat = args.catalog
    nsensors = args.nsensors
    if args.phosimdir is None:
        phosimdir = os.environ['PHOSIMDIR']
    else:
        phosimdir = args.phosimdir

    #
    # Set the seed.
    #
    random.seed(seed=args.seed)
    #
    # Generate the input catalog of stars, appending to the input configuration
    #
    inst_cat = InstCat(default_instcat)
    inst_cat.generate_stars(args)
    inst_cat.write(my_instcat)
    inst_cat.ds9_regfile(os.path.join(phosimdir, 'output', 'ds9.reg'))

    my_sensors = sensors(phosimdir)
    index = (np.array(random.randint(len(my_sensors), size=args.nsensors)),)
    my_sensors = sorted(my_sensors[index])

    curdir = os.path.abspath('.')
    instcat = os.path.join(curdir, my_instcat)
    for sensor in my_sensors:
        os.chdir(phosimdir)
        command = './phosim %s -s %s -c examples/nobackground' % (instcat, sensor)
        if args.verbose:
            print command
        subprocess.call(command, shell=True)
        os.chdir(curdir)
    copy_output(phosimdir, dest_dir)
