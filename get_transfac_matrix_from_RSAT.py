#!/usr/bin/python3
# Notes: V1.0, 02/03/2019
# Author(s): Velez Santiago Jesus
# Email(s): jvelez@lcg.unam.mx

#==============================================================================#
# Objetive:
# Input:
#
# Output:
#   Option: [-t, --out_type] default: independent.
#   [independent]: Return a file for each query founded.
#   [combined]: Return a single file for with all queries founded.
#   [all]: Return all above.
# Help:
#   python get_transfac_matrix_from_RSAT.py [-h, --help]
# Example of usage:
#   python get_transfac_matrix_from_RSAT.py -a M01444 MA0712_1 -d hocomoco jaspar_non -t all -p OTX2 -o motifss
#   python get_transfac_matrix_from_RSAT.py -i transfac_queries.csv -o motifs
#       With 'transfac_queries.csv' as follows:
#           M01444,hocomoco
#           MA0712_1,jaspar_non
#==============================================================================#

import os
import sys
import argparse
import urllib.request as urllib2
from itertools import product

system_databases = {
    'jaspar_non': 'http://rsat.sb-roscoff.fr//motif_databases/JASPAR/Jaspar_2018/nonredundant/JASPAR2018_CORE_vertebrates_non-redundant_pfms_transfac.tf',
    'hocomoco': 'http://rsat.sb-roscoff.fr//motif_databases/HOCOMOCO/HOCOMOCO_2017-10-17_Human.tf'
}

def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("File {} does not exist.".format(arg))
    else:
        return arg

def read_queries_file(file, sep = ','):
    with open(file, 'r') as f:
        try:
            raw_queries = [row.strip('\n').split(sep)[0:2] for row in f if not row.startswith('\n')]
            fails = [query for query in raw_queries if query[1] not in system_databases]
            queries = [query for query in raw_queries if query[1] in system_databases]

            for accession, database in fails:
                print('#Database {} not recognized. Query "{}{}{}" was ignored.'.format(database,accession,sep,database))
            return queries
        except:
            raise ValueError()

def get_queries(args):
    if args.inputfile:
        queries = read_queries_file(args.inputfile, sep = args.sep)
    elif len(args.accessions) != len(args.databases):
        queries = product(args.accessions, args.databases)
    else:
        queries = zip(args.accessions, args.databases)
    return queries

def get_transfac_matrix(accesion, database):
    accesion = accesion.replace('.','_')
    data = urllib2.urlopen(system_databases[database])

    found = False
    transfac = []
    for line in data: # files are iterable
        line = str(line, 'utf-8').strip('\n')
        if found and ('//' in line):
            transfac.append(line)
            break
        elif found:
            transfac.append(line)
        if ('AC  ' + accesion) in line:
            found = True
            transfac.append(line)
            print('#Accession {} was found in {} database.'.format(accesion, database))
    else:
        print('#Accession {} was not found in {} database.'.format(accesion, database))
    return (accesion + '_' + database, '\n'.join(transfac))

def write_transfacs(transfac, outpath, out_type, prefix):
    if not os.path.exists(outpath):
        os.makedirs(outpath)

    if out_type == 'all':
        with open(os.path.join(outpath,prefix + '_reference_motifs.tf'), 'w') as combined:
            for name, transfac in transfacs:
                combined.write(transfac + '\n')
                with open(os.path.join(outpath, prefix + '_' + name + '.tf'), 'w') as independent:
                    independent.write(transfac)
    elif out_type == 'combined':
        with open(os.path.join(outpath, prefix + '_reference_motifs.tf'), 'w') as outFile:
            for name, transfac in transfacs:
                outFile.write(transfac + '\n')
    elif out_type == 'independent':
        for name, transfac in transfacs:
            with open(os.path.join(outpath, prefix + '_' + name + '.tf'), 'w') as independent:
                independent.write(transfac)

def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--accessions', help = 'Accession codes for factors to extract.', nargs = '+')
    parser.add_argument('-d', '--databases',  help = 'Select databases to extract transfac matrixs.', choices = system_databases.keys(), nargs = '+')
    parser.add_argument('-o', '--outpath',    help = 'Path to redirect output files.', default = os.getcwd())
    parser.add_argument('-t', '--out_type',   help = 'Type of Output', choices = ['all','combined','independent'], default = 'independent')
    parser.add_argument('-p', '--prefix',     help = 'Prefix to output file.', nargs = '?', default = 'factor')
    parser.add_argument('-i', '--inputfile',  help = 'Read queries from file. Format: [accesion,database]', default = None, metavar="FILE", type=lambda arg: is_valid_file(parser, arg))
    parser.add_argument('-s', '--sep',        help = 'Separator character to split inputfile.', nargs = '?', default = ',')
    return parser

if __name__ == '__main__':

    print('#python ' + ' '.join(sys.argv))
    parser = create_parser()
    args = parser.parse_args()
    queries = get_queries(args)
    transfacs = [get_transfac_matrix(accesion, database) for accesion, database in queries]
    transfacs = [transfac for transfac in transfacs if transfac[1] != '']

    write_transfacs(transfacs, args.outpath, args.out_type, args.prefix)
    print('#Done!')
