# Artic nCoV Wrapper
A simple wrapper script to automated the artic nCoV-2019 pipeline icluding the medaka variant calling.

The creation of this script followed the protocol outlined in the [Artic nCoV-2019 documentation](https://artic.network/ncov-2019/ncov2019-bioinformatics-sop.html)

## Installation
This tool is essentially just a script that utilizes the Artic nCOV-2019 dependencies, so installation follows the installation of the pipeline itself.

To install the Artic nCoV-2019 environment and this script enter the following commands:
```
git clone --recursive https://github.com/artic-network/artic-ncov2019.git
conda env create -f artic-ncov2019/environment.yml
conda activate artic-ncov2019

git clone https://github.com/rchapman2000/artic-ncov-wrapper.git
```

## Usage
The Artic nCoV pipeline consists of three distinct steps: basecalling, demultiplexing, and filtering/consensus generation. Depending on the software used for sequencing basecalling and/or demultiplexing may have already been performed. Thus, this script allows users to run the Artic nCoV pipeline starting at any of these steps.

### General Usage:
```
python3 artic-wrapper.py [options] --minLen INT --maxLen INT --demux-dir PATH --scheme-location PATH --primer-scheme STRING --sample-file FILE 
```

### Arguments: 

**Required Arguments:**

| Option tag | Option Description |
| ---------- | ------------------ |
| --minLen INT | The minimum amplicon length |
| --maxLen INT | The maximum amplicon length |
| --demux-dir PATH | Directory where barcodes are located (or will be written to if performing basecalling/demultiplexing) and where results will be written |
| --scheme-location PATH | Path to the artic nCoV primer schemes |
| --primer-scheme STRING | Primer scheme to be used (Ex: nCoV-2019/V3) |
| --sample-file FILE | A tab-delimited file containing samples names corresponding to the different barcodes. Should be in format (barcode# \t SampleName) | 

**Optional Arguments:**
| Option tag | Option Description |
| ---------- | ------------------ |
| --threads INT | Number of CPU threads available to use |
| --normalize INT | The normalize parameter to be used in the consensus generation step (Normalization corresponds to the # of reads to be normalized to post trimming) [Default = 200] |
| --basecall | Include this flag to tell the wrapper to perform base calling **(Requires that the --original-reads option is included)** |
| --demultiplex | Include this flag to tell the wrapper to perform demultiplexing **(Requires that --original-reads directory is included)** |
| --original-reads PATH | **Must be included if --basecall or --demultiplex was passed** Path to the directory containing either raw reads to be used in either basecalling or demultiplexing. For basecalling, this directory should contain a sub-directory fast5_pass/ which has all of your raw sequencing output. For demultiplexing, the directory should contain a subdirectory fastq_pass/ which has all of the multiplex fastqs. |

## Examples:
### Sample File
The sample file is a tab-delimited file with one column containing barcode numbers and another containing the corresponding sample name. The file should **not** include a header and the barcode should be labeled *barcode##* 

Here is an example:
```
barcode01 Sample1
barcode02 Sample2
barcode03 Sample3
```

### Running Filtering/Basecalling
Ensure you are in the artic conda environment 
```
conda activate artic-ncov2019
```
Below is an example of what the command to run the pipeline from the filtering/generate consensus step:
```
python3 articwrapper.py --minLen 400 --maxLen 700 --demux-dir /path/to/run/ \ 
        --scheme-location /path/to/primer-schemes --primer-scheme nCoV-2019/V3 --sample-file ./samples.txt
```
The output will be a folder for each sample placed into the --demux-dir option. The folders will be labeled SampleName-barcode##/

### Running Basecalling
Ensure you are in the artic conda environment 
```
conda activate artic-ncov2019
```
Say we have the filestructure:
```
 /Run1
    /raw-reads
       /fast5_pass
    /results
```
Below is the command to run the pipeline starting from the basecalling step based on this filestructure:
```
python3 articwrapper.py --basecall --original-reads /Run1/raw-reads/ \
        --minLen 400 --maxLen 700 --demux-dir /Run1/results/ --scheme-location /path/to/primer-schemes \
        --primer-scheme nCoV-2019/V3 --sample-file ./samples.txt
```
The output will be present in the /Run1/results directory and contain fastq files for each barcode as well as folders containing the consensuses. These folders will be labeled SampleName-barcode##/

## Running Demulitplexing
Ensure you are in the artic conda environment 
```
conda activate artic-ncov2019
```
Staring from demultiplexing is similar to starting from basecalling.
Say we have the filestructure:
```
 /Run1
    /raw-reads
       /fast5_pass
       /fastq_pass
    /results
```
Below is the command to run the pipeline starting from the demultiplexing step based on this filestructure:
```
python3 articwrapper.py --demultiplex --original-reads /Run1/raw-reads/ \
        --minLen 400 --maxLen 700 --demux-dir /Run1/results/ --scheme-location /path/to/primer-schemes \
        --primer-scheme nCoV-2019/V3 --sample-file ./samples.txt
```
