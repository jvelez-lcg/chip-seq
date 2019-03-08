#!/bin/bash
#
## Notes: V1.0, 02/03/2019
## Author(s): Velez Santiago Jesus
## Email(s): jvelez@lcg.unam.mx

#===================================================================================================#
# Objetive:
# Input:
#
# Output:
#
# Example:
#
#===================================================================================================#

function try {
    "$@"
    code=$?
    if [ $code -ne 0 ]; then
        echo "$1 did not work: exit status $code."
        exit 1
    fi
}

try module load rsat
try source activate python3

# Set RSAT parameters.
factor='OTX2'
bed_url='http://pedagogix-tagc.univ-mrs.fr/remap/download/remap2018/hg38/MACS/all_tf/OTX2/remap2018_OTX2_all_macs2_hg38_v1_2.bed.gz'
genome='hg38'
format='UCSC'
organism='Homo_sapiens_GRCh37'

# Outfiles
bed="$factor.bed"
bed_fasta="$factor.fasta"
bed_rand_fasta="$factor.random_genome_fragments.fasta"

# Set matrix parameters.
pythonf='python get_transfac_matrix_from_RSAT.py'
transfac_queries='transfac_queries.csv'
outtype='all'
outpath='./'
sep=','

# Download bed file of transcription factor.
if [ ! -f $bed ]; then
    try wget -O $bed.gz $bed_url && try gunzip $bed.gz
fi
echo "Download bed file of $factor done."

# RSAT - fetch-sequence.
if [ ! -f $bed_fasta ]; then
    try fetch-sequences  -v 1 -genome $genome -header_format $format -i $bed -o $bed_fasta
fi
echo 'RSAT - fetch-sequence done.'

# RSAT - random genome fragments.
if [ ! -f $bed_rand_fasta ]; then
    try random-genome-fragments -i $bed_fasta -org $organism  -return seq  -o $bed_rand_fasta
fi
echo 'RSAT - random genome fragments done.'

# Download transfac matrix from queries file.
try $pythonf -i $transfac_queries -p $factor -s $sep -t $outtype -o $outpath
echo 'Download transfac matrixs from queries done.'

echo 'All tasks have been performed.'
