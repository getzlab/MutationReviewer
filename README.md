# MutationReviewer

Suite of reviewers for annotating mutations with IGV.

![MutationReviewer Demo](https://github.com/getzlab/MutationReviewer/blob/master/images/Screen%20Recording%202023-04-20%20at%205.13.38%20PM_compressed.gif)

# Install

## Activate or Set up Conda Environment

This is **_highly_** recommended to manage different dependencies required by different reviewers.

See [Set up Conda Environment](https://github.com/getzlab/JupyterReviewer/blob/master/README.md#set-up-conda-environment) for details on how to download conda and configure an environment.
    
## Install MutationReviewer inside conda environment

```
git clone git@github.com:getzlab/MutationReviewer.git
cd MutationReviewer
conda activate <your_env>
pip install -e .
```

# Basic usage

See `example_notebooks` for basic examples and demos of the mutation reviewers.

See `MutationReviewer/Reviewers` to see available pre-built reviewer options.

See `MutationReviewer/DataTypes` to see pre-built data configurations for mutation review.

# Custom and advanced usage

See `MutationReviewer/AppComponents` for pre-built components and their customizable parameters, and additional utility functions. 

For customizing annotations, adding new components, and other features, see [Intro_to_Reviewers.ipynb](https://github.com/getzlab/JupyterReviewer/blob/master/example_notebooks/Intro_to_Reviewers.ipynb)

For creating your own prebuilt reviewer, see [Developer_Jupyter_Reviewer_Tutorial.ipynb](https://github.com/getzlab/JupyterReviewer/blob/master/example_notebooks/Developer_Jupyter_Reviewer_Tutorial.ipynb)