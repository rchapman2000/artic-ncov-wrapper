import sys
import os
import argparse
import subprocess
import pandas as pd
import re

# Checks whether a path is relative or absolute
def checkPath(path, currentDir):
    
    print(os.path.isabs(path))
    if os.path.isabs(path):
        return path
    else:
        return currentDir + path

def runCommand(command):
    print(command)
    return subprocess.run(command, stdout=subprocess.PIPE, stderr=sys.stdout, shell=True)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--minLen', required=True, type=int, help='[Required] - Minimum amplicon length', action='store', dest='minLen')
    parser.add_argument('--maxLen', required=True, type=int, help='[Required] - Maximum amplicon length', action='store', dest='maxLen')
    parser.add_argument('--demux-dir', '-d', required=True, type=str, help='[Required] - Directoy where barcodes are located (or where they will be written to if performing basecalling or demultiplexing', action='store', dest='demuxDir')
    parser.add_argument('--scheme-location', required=True, type=str, help='[Required] - Path to primer scheme location', action='store', dest='pl')
    parser.add_argument('--primer-scheme', required=True, type=str, help='[Required] - Primer scheme to be used (Ex: nCov-2019/V3)', action='store', dest='ps')
    parser.add_argument('--sample-file', required=True, type=str, help='[Required] - tab separated file containing sample name corresponding to barode (Format: Barcode#\\tSample)', action='store', dest = 'sampFile')
    parser.add_argument('--normalize', type=str, help='Normalize value for medaka pipeline [Default = 200]', action='store', dest='normalize')
    parser.add_argument('--basecall', help='Include this flag to perform base calling', action='store_true', dest='basecall')
    parser.add_argument('--demultiplex', help='Include this flag to perform demultiplexing', action='store_true', dest='demultiplex')
    parser.add_argument('--original-reads', '-rd', type=str, help='Path to directory containing reads (Fast5 and FastQ). Must include for basecalling and demultiplexing', action='store', dest ='readDir')
    parser.add_argument('--threads', '-t', type=int, help='Number of CPU threads available (Default = 1)', action='store', dest='threads')

    args = parser.parse_args()
    currentDir = os.getcwd() + '/'

    minLen = args.minLen
    maxLen = args.maxLen
    demuxDir = checkPath(args.demuxDir, currentDir)
    if demuxDir[-1] != '/':
        demuxDir = demuxDir + '/'

    schemePath = checkPath(args.pl, currentDir)
    if (schemePath[-1] != '/'):
        schemePath += '/'
    primerScheme = args.ps
    print(schemePath + primerScheme)
    if (not os.path.isdir(schemePath + primerScheme)):
        print("Primer Scheme at {0} not found\nCheck that this path exists\nExiting...".format(schemePath + primerScheme))
        quit()

    sampleFile = open(checkPath(args.sampFile, currentDir))
 
    normalize = 200
    if args.normalize:
        normalize = args.normalize
    
    threads = 1
    if (args.threads):
        threads = args.threads
    
    workingDir = currentDir
    doBasecall = args.basecall
    doDemultiplex = args.demultiplex

    if (doBasecall or doDemultiplex):
        try:
            os.mkdir(demuxDir)
        except OSError as e:
            print("Directory {0} already exists - proceeding anyway...".format(demuxDir))
    os.chdir(demuxDir)

    if (doBasecall):
        if not (args.readDir):
            print("No directory containing Fast5/FastQ files was detected. Quitting...")
            quit()
        readDir = checkPath(args.readDir, workingDir)
        if readDir[-1] != '/':
            readDir = readDir + '/'

        process = subprocess.run("guppy_basecaller -c dna_r9.4.1_450bps_fast.cfg -i {0} -s {1} -x auto -r".format(readDir, 'automated-basecalling/fastq_pass'), shell=True)
        
        doDemultiplex = True
        readDir = demuxDir + 'automated-basecalling/'
        

    if (doDemultiplex):
        if not (args.readDir):
            print("No directory containing Fast5/FastQ files was detected. Quitting...")
            quit()
        
        readDir = checkPath(args.readDir, workingDir)
        if readDir[-1] != '/':
            readDir = readDir + '/'

        if not args.basecall:
            try:
                os.mkdir(demuxDir)
            except OSError as e:
                print("Directory {0} already exists - proceeding anyway...".format(demuxDir))

        process = subprocess.run('guppy_barcoder -t {0} --require_barcodes_both_ends -i {1} -s {2} --arrangements_files \"barcode_arrs_nb12.cfg barcode_arrs_nb24.cfg\"'.format(threads, readDir + 'fastq_pass', demuxDir), shell=True)

    barcodes = []
    dirs = []
    
    sampleDict = {}
    line = sampleFile.readline()
    while line:
        col = line.replace('\n', '').split('\t')
        sampleDict[col[0]] = col[1]
        barcodes.append(col[0])
        line = sampleFile.readline() 
    print(barcodes)
    
    for bc in barcodes:
        process = runCommand('artic guppyplex --min-length {0} --max-length {1} --directory {2} --prefix {3}'.format(minLen, maxLen, demuxDir + bc, sampleDict[bc]))
        print(process.stderr)
        print(process.stdout)
 
        process = runCommand('artic minion --medaka --normalise {0} --threads {1} --scheme-directory {2} --read-file {3} {4} {5}'.format(normalize, threads, schemePath, '*_' + bc + '.fastq', primerScheme, sampleDict[bc]))
        print(process.stderr)
        print(process.stdout)
        
        sampleResultsDir = (demuxDir + sampleDict[bc] + "-" + bc)
        try:
            os.mkdir(sampleResultsDir)
        except OSError as e:
            print("Directory {0} already exists - proceeding anyway...".format(sampleResultsDir))
       
        process = runCommand("mv {0}.* {1}".format(sampleDict[bc], sampleResultsDir))
   
        
   
    print("Pipeline Complete\nResults Located at {0}\n".format(workingDir))
    sampleFile.close()


if __name__ == "__main__":
    main()
