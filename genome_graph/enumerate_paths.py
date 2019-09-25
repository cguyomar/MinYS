#!/usr/bin/env python3

"""
Enumerate all paths going through the longest node of a gfa graph
-> Enumerates paths in one connected component only for now
"""

import argparse

import genome_graph

import shutil
import os
from csv import reader
from progress.bar import Bar



def write2fasta(seq,seqName,fileName):
        ofile = open(os.path.join(fileName), "w")
        ofile.write(">" + seqName + "\n" + seq + "\n")
        ofile.close()

def run_pyani(tempDir):
        #if os.path.isdir("./temp/ani"):
        ##        shutil.rmtree("./temp/ani")
        #os.mkdir("./temp/ani")
        #shutil.copyfile("./temp/path_"+str(i)+".fa","./temp/ani/"+str(pathi)+".fa")
        #shutil.copyfile("./temp/path_"+str(j)+".fa","./temp/ani/"+str(pathj)+".fa")

        os.system("average_nucleotide_identity.py -i "+tempDir+" -o "+tempDir+"/ani_out -m ANIm")
        identity = min(read_pyani_output(os.path.join(tempDir,"ani_out/ANIm_percentage_identity.tab")))
        cov = min(read_pyani_output(os.path.join(tempDir,"ani_out/ANIm_alignment_coverage.tab")))

        shutil.rmtree(os.path.join(tempDir,"./ani_out"))
        
        return(identity,cov)

def read_pyani_output(file):
        tsv_reader = reader(open(file,"r"), quotechar="\"", delimiter='\t')
        line_count = 0
        val1 = None
        val2 = None
        for row in tsv_reader:
                if line_count == 1:
                        val1 = row[2]
                elif line_count == 2:
                        val2 = row[1]
                line_count += 1
        return(float(val1),float(val2))

def compare_paths(paths,outDir):
        print("Comparing "+str(len(paths))+" paths")

        # Preparing dirs
        tmpDir = os.path.join(outDir,"temp")
        if os.path.isdir(outDir):
                shutil.rmtree(outDir)
        os.mkdir(outDir)

        if os.path.isdir(tmpDir):
                shutil.rmtree(tmpDir)
        os.mkdir(tmpDir)
        #shutil.copyfile("./temp/path_"+str(i)+".fa","./temp/ani/"+str(pathi)+".fa")
        #shutil.copyfile("./temp/path_"+str(j)+".fa","./temp/ani/"+str(pathj)+".fa")
        unique_paths = []
        nb_unique_paths = 0

        bar = Bar('Comparing paths', max=len(paths))
        for p in paths:
                #print("\n")
                #print(p.nodeIds)
                seq = p.getSeq(g)
                if nb_unique_paths==0:
                        #unique_path.append(i)
                        write2fasta(seq,"path_1",os.path.join(outDir,"path1.fa"))
                        nb_unique_paths += 1
                        print("Added 1 unique path")
                else:
                        # Write to the dir where pyani will run
                        seqName = "path_" + str(nb_unique_paths+1)

                        write2fasta(seq,seqName,os.path.join(tmpDir,seqName+".fa"))

                        # Now compare to each of the ref seq
                        refPaths = filter(os.path.isfile, os.listdir(outDir))
                        newSeq = True
                        maxCov = 0
                        maxId = 0
                        for refPath in refPaths:
                                # print("Comparing with "+refPath)

                                # Copy the current ref in the ani dir
                                shutil.copyfile(os.path.join(outDir,refPath),os.path.join(tmpDir,refPath))
                                identity,coverage = run_pyani(tmpDir)

                                if identity > maxId:
                                        maxId = identity
                                if coverage > maxCov:
                                        maxCov = coverage
                                # print("Coverage : "+str(coverage))
                                # print("Identity : "+str(identity))

                                if coverage > 0.99 and identity > 0.99:
                                        # ref is identical
                                        # print("Found similar sequence in refseq - skipping")
                                        os.remove(os.path.join(tmpDir,refPath))
                                        os.remove(os.path.join(tmpDir,seqName+".fa"))
                                        newSeq = False
                                        break
                                else:
                                        os.remove(os.path.join(tmpDir,refPath))

                        #No break -> the sequence is unique
                        if newSeq:
                                print("Found a new path with cov ="+str(maxCov)+" and id="+str(maxId))
                                nb_unique_paths += 1
                                shutil.move(os.path.join(tmpDir,seqName+".fa"),os.path.join(outDir,seqName+".fa"))
                
                bar.next()
        bar.finish()
        print("Number of unique Paths : "+str(nb_unique_paths)+"\n")



op = argparse.ArgumentParser()
op.add_argument("infile")
op.add_argument("outdir")
opts = op.parse_args()

# Prepare out dir
if os.path.isdir(opts.outdir):
        shutil.rmtree(opts.outdir)
os.mkdir(opts.outdir)

# Read graph
print("Loading graph")
g = genome_graph.GenomeGraph.read_gfa(opts.infile) 

# List connected components
comps = g.connected_components()
print("Found "+str(len(comps))+" connected components \n")

# Enumerate for each comp
compIter = 1
for comp in comps:
    print("Searching paths in component "+str(compIter))
    startNode = g.longest_node(comp)
    paths = g.find_all_paths(startNode)

    print("Found "+str(len(paths))+" paths in component "+str(compIter)+"\n")

    compDir = os.path.join(opts.outdir,"comp_"+str(compIter))
    compare_paths(paths,compDir)

    compIter += 1




