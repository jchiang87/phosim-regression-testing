#!/usr/bin/env python
import os
import sys
import glob
import subprocess
from argparse import ArgumentParser

def popen(command):
    p = subprocess.Popen(command, shell=True,
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT,
                         close_fds=True)
    return p.stdin, p.stdout

def have_executable(exe):
    command = 'which %s' % exe
    path = [x for x in popen(command)[1]][0].strip()
    return os.path.exists(path)

if __name__ == '__main__':
    parser = ArgumentParser('Compare phosim output for regression testing')
    parser.add_argument('target_dir', type=str, 
                        help='Directory of target data for comparison to reference data.')
    parser.add_argument('-r', '--reference_dir', dest='ref_dir', type=str,
                        default='reference_data',
                        help='Directory of reference data.')
    parser.add_argument('-v', '--verbose', dest='verbose', 
                        action="store_true", default=False,
                        help='Verbosity flag')
    args = parser.parse_args()

    target_dir = args.target_dir
    ref_dir = args.ref_dir
    verbose = args.verbose

    failures = []
    for subdir in ('output', 'work'):
        infiles = sorted(glob.glob(os.path.join(ref_dir, subdir, '*')))
        for item in infiles:
            filename = os.path.basename(item)
            if verbose:
                print "working on", filename
            # Use fdiff for FITS files if it is available.
            if (have_executable('fdiff') and 
                (filename[-5:] == '.fits' or filename[-8:] == '.fits.gz')):
                exe = 'fdiff'
            else:
                exe = 'diff'
            command = '%s %s %s' % (exe, item,
                                    os.path.join(target_dir, subdir, filename))
            if verbose:
                print command
            stdin, stdout = popen(command)
            output = [x for x in stdout]
            if (exe == 'fdiff' and 
                output[-1].find(' 0 differences were found') == -1):
                failures.append(filename)
                if verbose:
                    print output[-1].strip()
            elif exe == 'diff':
                if output:
                    failures.append(filename)
                if verbose:
                    for x in output:
                        print x.strip()
    if failures:
        print "Failed comparisons:"
        for item in failures:
            print item
