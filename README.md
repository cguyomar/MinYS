# MinYS - MineYourSymbiont



MinYS allows targeted assembly of bacterial genomes using a reference-guided pipeline. It consists in 3 steps :

- Mapping metagenomic reads on a reference genome using BWA. And assembling the recruited reads using [Minia](https://github.com/GATB/minia).
- Gapfilling the contig set using [MindTheGap](https://github.com/GATB/MindTheGap) in *contig mode*.
- Simplifying the GFA output of MindTheGap.



MinYS was developed in [GenScale](https://team.inria.fr/genscale/) by :

- Cervin Guyomar
- Claire Lemaitre



### Requirements

- [MindTheGap](https://github.com/GATB/MindTheGap)
- [BWA](http://bio-bwa.sourceforge.net/) (read mapping)
- [Minia](https://github.com/GATB/minia) (contig assembly)
- [Bandage](https://github.com/rrwick/Bandage) (Optionnal, for assembly graph visualization)

### Installation

```
git clone https://github.com/cguyomar/MinYS
cd MinYS
make -C graph_simplification/nwalign/
./MinYS.py
```

### Usage

```
[main options]:
  -in                   (1 arg) :    input reads file
  -1                    (1 arg) :    input reads first file
  -2                    (1 arg) :    input reads second file
  -fof                  (1 arg) :    input file of read files
  -out                  (1 arg) :    output directory for result files [Default: ./mtg_results]

[mapping options]:
  -ref                  (1 arg) :    bwa index

[assembly options]:
  -minia-bin            (1 arg) :    path to Minia binary
  -assembly-kmer-size   (1 arg) :    kmer size used for Minia assembly (should be given even if bypassing minia assembly step, usefull knowledge for gap-filling) [Default: 31]
  -assembly-abundance-min
                        (1 arg) :    Minimal abundance of kmers used for assembly [Default: auto]
  -min-contig-size      (1 arg) :    minimal size for a contig to be used in gapfilling [Default: 0]

[gapfilling options]:
  -mtg-dir              (1 arg) :    path to MindTheGap build directory
  -gapfilling-kmer-size
                        (1 arg) :    kmer size used for gapfilling [Default: 31]
  -gapfilling-abundance-min
                        (1 arg) :    Minimal abundance of kmers used for gapfilling [Default: auto]
  -max-nodes            (1 arg) :    Maximum number of nodes in contig graph [Default: 100]
  -max-length           (1 arg) :    Maximum length of gapfilling (nt) [Default: 10000]

[continue options]:
  -contigs              (1 arg) :    Contigs in fasta format - override mapping and assembly
  -graph                (1 arg) :    Graph in h5 format - override graph creation

[core options]:
  -nb-cores             (1 arg) :    number of cores [Default: 0]
```

- If *minia* of *MindTheGap* are not in $PATH, a path to the minia binary of MindTheGap build directory has to be supplied using `-minia-bin` or `-mtg-dir`
- `-contigs` and `-graph` may be used to bypass the mapping/assembly step, or the graph creation. 
  In the first case, `-assembly-kmer-size` should be supplied as the overlap between contigs.


### Utility scripts :

Some utility scripts are supplied along with MinYS in order to facilitate the post processing of the gfa graph :

- `graph_simplification/enumerate_paths.py in.gfa out_dir`
  Enumerate all the paths in connected components of a graph. Returns paths with a significant difference (ANI < 99\% or alignment coverage <99\%)

- `graph_simplification/filter_components.py in.gfa min_size`
   Return a sub-graph containing all the connected components longer than `min_size`

- `graph_simplification/gfa2fasta.py in.gfa out.fa`
  Return each sequence of the graph in a multi-fasta file
