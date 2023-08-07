from JupyterReviewer.DataTypes.GenericData import GenericData
from JupyterReviewer.Data import Data, DataAnnotation

import pandas as pd
import numpy as np
from typing import Union, List, Dict
from pathlib import Path
import os

class GeneralMutationData(Data):
    """
    Data object containing the relevant data needed for mutation review. Can be used to review single variants or observe multiple loci at once (ie breakpoints for the same event)
    """
    def __init__(
        self,
        index,
        description,
        mutations_df: pd.DataFrame,
        mutation_groupby_cols: list, # columns to groupby
        mutations_df_bam_ref_col: str, 
        chrom_cols: Union[str, list], # if a list, must be same length as start_pos_cols
        pos_cols: Union[str, list],
        bams_df: pd.DataFrame,
        bams_df_ref_col: str,
        bam_cols: Union[str, list],
        bai_cols: Union[str, list],
        annot_df: pd.DataFrame = None,
        annot_col_config_dict: Dict = None,
        history_df: pd.DataFrame = None,
    ):
        """
        Parameters
        ==========
        mutations_df: pd.DataFrame
            Dataframe with mutations to review
            
        mutation_groupby_cols: list
            list of columns in mutation_df to groupby. 
                ex. by chromosome, start position, sample
                ex. by chromosome, start position, patient to compare across mutations across samples in patient
                ex. by chromosome and start position to compare across samples
                
        mutations_df_bam_ref_col: Any
            Column in mutations_df with value to reference bam files in bams_df
                ex. sample id, patient
                
        chrom_cols: str, list
            Column(s) in mutations_df referencing chromosome of mutation to review. 
            There can be multiple chromosomes if reviewing structural variants like translocations or fusions
            
        pos_cols: str, list
            Column(s) in mutation_df referencing the position of the mutation to view.
            There can be multiple positions if reviewing large strcutural variants like translocations or fustions.
                ex. start and end of a large insertion or tandem duplication
                ex. Translocation
            **Must be the same length as chrom_cols
            
        bams_df: pd.DataFrame
            Dataframe with bam files
            
        bams_df_ref_col: Any
            Column in bams_df to query the bam files (ie sample, participant)
            
        bam_cols: str, list
            Column(s) in bams_df with the bam file paths or urls
            
        bai_cols:
            Column(s) in bams_df with the bai file paths or urls. 
            Must be same length as bam_cols and corresponding bam/bai columns must be in the same order
        """
        super().__init__(
            index=index,
            description=description,
            annot_df=annot_df,
            annot_col_config_dict=annot_col_config_dict,
            history_df=history_df,
        )
        
        bam_cols = [bam_cols] if isinstance(bam_cols, str) else bam_cols
        bai_cols = [bai_cols] if isinstance(bai_cols, str) else bai_cols
        
        chrom_cols = [chrom_cols] if isinstance(chrom_cols, str) else chrom_cols
        pos_cols = [pos_cols] if isinstance(pos_cols, str) else pos_cols
        
        required_mutations_df_cols = [mutations_df_bam_ref_col] + chrom_cols + pos_cols
        if not set(
            required_mutations_df_cols
        ).issubset(mutations_df.columns):
            missing_cols = [c for c in required_mutations_df_cols if c not in mutations_df.columns]
            raise ValueError(f'Following columns do not exist in mutations_df dataframe: {missing_cols}')
            
        required_bam_df_cols = [bams_df_ref_col] + bam_cols + bai_cols
        if not set(
            required_bam_df_cols
        ).issubset(bams_df.columns):
            missing_cols = [c for c in required_bam_df_cols if c not in bams_df.columns]
            raise ValueError(f'Following columns do not exist in bams_df dataframe: {missing_cols}')
        
        self.mutations_df = mutations_df
        self.mutation_groupby_cols = mutation_groupby_cols
        self.mutations_df_bam_ref_col = mutations_df_bam_ref_col
        self.chrom_cols = chrom_cols
        self.pos_cols = pos_cols
        
        self.bams_df = bams_df
        self.bams_df_ref_col = bams_df_ref_col
        self.bam_cols = bam_cols
        self.bai_cols = bai_cols
