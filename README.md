# MinYS - MineYourSymbiont



MinYS allows targeted assembly of bacterial genomes using a reference-guided pipeline. It consists in 3 steps :

- Mapping metagenomic reads on a reference genome using BWA. And assembling the recruited reads using [Minia](https://github.com/GATB/minia).
- Gapfilling the contig set using [MindTheGap](https://github.com/GATB/MindTheGap) in *contig mode*.
- Simplifying the GFA output of MindTheGap.



MinYS was developed in the [GenScale lab](https://team.inria.fr/genscale/) by :

- Cervin Guyomar
- [Claire Lemaitre](http://people.rennes.inria.fr/Claire.Lemaitre/index.php)



### Requirements

- [BWA](http://bio-bwa.sourceforge.net/) (read mapping)
- [Minia](https://github.com/GATB/minia) (contig assembly)
- [MindTheGap](https://github.com/GATB/MindTheGap) (gap-filling)
- [Bandage](https://github.com/rrwick/Bandage) (Optionnal, for assembly graph visualization)

### Installation

#### With Conda

```
conda install -c bioconda minys
```

#### From source
```
git clone https://github.com/cguyomar/MinYS
cd MinYS
make -C graph_simplification/nwalign/
./MinYS.py
```

#### Test run
```
MinYS.py -1 test_data/reads.1.fq -2 test_data/reads.2.fq -ref test_data/ref.fa -out MinYS_result
# look at the output file:
head MinYS_results/gapfilling/minia_k31_abundancemin_auto_filtered_400_gapfilling_k31_abundancemin_auto.simplified.gfa
# should contain only one sequence node of 15,722 bp, or see also the logs:
more MinYS_results/logs/simplification.log
```

### Options

```
[main options]:
  -in                   (1 arg) :    Input reads file
  -1                    (1 arg) :    Input reads first file
  -2                    (1 arg) :    Input reads second file
  -fof                  (1 arg) :    Input file of read files (if paired files, 2 columns tab-separated)
  -out                  (1 arg) :    output directory for result files [Default: ./MinYS_results]

[mapping options]:
  -ref                  (1 arg) :    Bwa index
  -mask                 (1 arg) :    Bed file for region removed from mapping

[assembly options]:
  -minia-bin            (1 arg) :    Path to Minia binary (if not in $PATH
  -assembly-kmer-size   (1 arg) :    Kmer size used for Minia assembly (should be given even if bypassing minia assembly step, usefull knowledge for gap-filling) [Default: 31]
  -assembly-abundance-min
                        (1 arg) :    Minimal abundance of kmers used for assembly [Default: auto]
  -min-contig-size      (1 arg) :    Minimal size for a contig to be used in gap-filling [Default: 400]

[gapfilling options]:
  -mtg-dir              (1 arg) :    Path to MindTheGap build directory (if not in $PATH)
  -gapfilling-kmer-size
                        (1 arg) :    Kmer size used for gap-filling [Default: 31]
  -gapfilling-abundance-min
                        (1 arg) :    Minimal abundance of kmers used for gap-filling [Default: auto]
  -max-nodes            (1 arg) :    Maximum number of nodes in contig graph [Default: 300]
  -max-length           (1 arg) :    Maximum length of gap-filling (nt) [Default: 50000]

[simplification options]:
  -l                    (1 arg) :    Length of minimum prefix for node merging, default should work for most cases [Default: 100]

[continue options]:
  -contigs              (1 arg) :    Contigs in fasta format - override mapping and assembly
  -graph                (1 arg) :    Graph in h5 format - override graph creation

[core options]:
  -nb-cores             (1 arg) :    Number of cores [Default: 0]

```

- If *minia* or *MindTheGap* are not in the $PATH environment variable, a path to the minia binary or to the MindTheGap build directory has to be supplied using `-minia-bin` or `-mtg-dir` options
- `-contigs` and `-graph` may be used to bypass the mapping/assembly step, and the graph creation, respectively.
  In the first case, `-assembly-kmer-size` should be supplied as the overlap between contigs.


### Documentation

A [step by step tutorial](doc/tutorial.ipynb) of the analysis of one sample presented in the paper is available as a Jupyter notebook.

### Utility scripts :

Some utility scripts are supplied along with MinYS in order to facilitate the post processing of the output gfa graph :

- `graph_simplification/enumerate_paths.py in.gfa out_dir`
  Enumerate all the paths of each connected component of a graph. Returns paths that are substantially different from one another (ANI < 99\% or alignment coverage <99\%)

- `graph_simplification/filter_components.py in.gfa min_size`
   Return a sub-graph containing all the connected components larger than `min_size` (in total assembled nt)

- `graph_simplification/gfa2fasta.py in.gfa out.fa`
  Return all the sequences of the graph in a multi-fasta file
 
### Reference

MinYS: Mine Your Symbiont by targeted genome assembly in symbiotic communities. Guyomar C, Delage W, Legeai F, Mougel C, Simon JC, Lemaitre C. BioRxiv 2019, [doi:10.1101/2019.12.13.875021](https://www.biorxiv.org/content/10.1101/2019.12.13.875021v1)
