# MutationReviewer

Suite of reviewers for annotating mutations with IGV.

![MutationReviewer Demo](https://github.com/getzlab/MutationReviewer/blob/master/images/Screen%20Recording%202023-04-20%20at%205.13.38%20PM_compressed.gif)

**References**

Barnell EK, Ronning P, Campbell KM, Krysiak K, Ainscough BJ, Sheta LM, Pema SP, Schmidt AD, Richters M, Cotto KC, Danos AM, Ramirez C, Skidmore ZL, Spies NC, Hundal J, Sediqzad MS, Kunisaki J, Gomez F, Trani L, Matlock M, Wagner AH, Swamidass SJ, Griffith M, Griffith OL. Standard operating procedure for somatic variant refinement of sequencing data with paired tumor and normal samples. Genet Med. 2019 Apr;21(4):972-981. doi: 10.1038/s41436-018-0278-z. Epub 2018 Oct 5. PMID: 30287923; PMCID: PMC6450397.

James T Robinson, Helga Thorvaldsdottir, Douglass Turner, Jill P Mesirov, igv.js: an embeddable JavaScript implementation of the Integrative Genomics Viewer (IGV), Bioinformatics, Volume 39, Issue 1, January 2023, btac830, https://doi.org/10.1093/bioinformatics/btac830

Thorvaldsdóttir H, Robinson JT, Mesirov JP. Integrative Genomics Viewer (IGV): high-performance genomics data visualization and exploration. Brief Bioinform. 2013 Mar;14(2):178-92. doi: 10.1093/bib/bbs017. Epub 2012 Apr 19. PMID: 22517427; PMCID: PMC3603213.

Robinson JT, Thorvaldsdóttir H, Winckler W, Guttman M, Lander ES, Getz G, Mesirov JP. Integrative genomics viewer. Nat Biotechnol. 2011 Jan;29(1):24-6. doi: 10.1038/nbt.1754. PMID: 21221095; PMCID: PMC3346182.

# Install

## Activate or Set up Conda Environment

This is **_highly_** recommended to manage different dependencies required by different reviewers.

See [Set up Conda Environment](https://github.com/getzlab/JupyterReviewer/blob/master/README.md#set-up-conda-environment) for details on how to download conda and configure an environment.
    
## Install MutationReviewer

Clone 
```
git clone git@github.com:getzlab/MutationReviewer.git --recurse-submodules

# or in an existing repo
git submodule add git@github.com:getzlab/MutationReviewer.git --recurse-submodules
```

Install MutationReviewer and igv_remote (this package connects to your local IGV app)
```
cd MutationReviewer
conda activate <your_env>
pip install -e .
pip install -e MutationReviewer/igv_remote/.
```

# Basic usage

See `example_notebooks` for basic examples and demos of the mutation reviewers.

See `MutationReviewer/Reviewers` to see available pre-built reviewer options.

See `MutationReviewer/DataTypes` to see pre-built data configurations for mutation review.

# Custom and advanced usage

See `MutationReviewer/AppComponents` for pre-built components and their customizable parameters, and additional utility functions. 

For customizing annotations, adding new components, and other features, see [Intro_to_Reviewers.ipynb](https://github.com/getzlab/JupyterReviewer/blob/master/example_notebooks/Intro_to_Reviewers.ipynb).

For creating your own prebuilt reviewer, see [Developer_Jupyter_Reviewer_Tutorial.ipynb](https://github.com/getzlab/JupyterReviewer/blob/master/example_notebooks/Developer_Jupyter_Reviewer_Tutorial.ipynb).
