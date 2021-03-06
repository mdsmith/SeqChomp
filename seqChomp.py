#! /usr/bin/env python

import os, sys
import argparse
import glob
import re

def head_fix(header, length):
    new_header = []
    for line in header:
        if re.search("DIMENSIONS", line.upper()) != None:
            nchar_start = re.search("NCHAR", line.upper()).start()
            pre = line[:nchar_start]
            tail = line[nchar_start:]
            post = tail.split('=')[1:]
            post = post[0].split()[1:] + post[1:]
            new_header.append(pre)
            new_header.append("NCHAR = " + str(length))
            new_header.append(" ".join(post))
            if len(post) == 0:
                new_header.append(";")
            new_header.append("\n")
        else:
            new_header.append(line)
    return new_header

def chunk(input_file):
    # open file, get parts
    infile = open(input_file, 'r')
    lines = infile.readlines()
    infile.close()
    header = []
    pre_seqs = []
    footer = []
    matrix = False
    in_footer = False
    for line in lines:
        if not matrix and not footer:
            header.append(line)
            if re.search("MATRIX", line) != None or re.search("Matrix",
            line) != None:
                matrix = True
        elif matrix:
            if (re.search("END;", line) != None or
                re.search("End;", line) != None):
                matrix = False
                in_footer = True
                footer.append(line)
            else:
                if len(line.strip()) != 0 and line.strip()[0] != ";":
                    if list(line.strip())[0] != "[":
                        pre_seqs.append(line)
        else:
            footer.append(line)
    seqs = {}
    for seq in pre_seqs:
        key, value = seq.split()
        seqs[key] = value
    return header, seqs, footer

def make_lines(seq_dict):
    seqs = []
    for key, value in seq_dict.items():
        seqs.append("\t" + key + "\t" + value + "\n")
    return seqs

def write_file( file_name,
                header,
                seqs,
                footer):
    outfile = open(file_name, 'w')
    outfile.writelines(header)
    outfile.writelines(make_lines(seqs))
    outfile.writelines(footer)
    outfile.close()

def nchars(seq_dict):
    for key,value in seq_dict.items():
        return len(list(value))

def chomp(input_file, output_directory, length, suffix):
    # header = list of lines (strings) to be modded and written out
    # seqs = a dictionary of seqs by leaf name
    # footer = anything at the bottom of the file to be written out
    header, seqs, footer = chunk(input_file)
    if len(seqs) == 0:
        print("File skipped: " + input_file)
        return
    else:
        align_len = nchars(seqs)
        if int(length) > int(align_len):
            length = align_len
        header = head_fix(header, length)
        new_seqs = {}
        for node,seq in seqs.items():
            new_seqs[node] = seq[:int(length)]
        write_file( output_directory    + os.sep
                                        + os.path.basename(input_file)
                                        + suffix,
                    header,
                    new_seqs,
                    footer)
        return

def get_files(input):
    if os.path.isfile(input):
        return [input]
    else:
        file_list = glob.glob(input + os.sep + "*")
        return file_list

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="input file or directory")
    parser.add_argument("length", help="desired sequence length")
    parser.add_argument("--output",
                        help="directory",
                        default=".")
    parser.add_argument("--suffix",
                        help="output file suffix",
                        default=".short")
    args = parser.parse_args()

    file_list = get_files(args.input)
    for file in file_list:
        chomp(file, args.output, args.length, args.suffix)
