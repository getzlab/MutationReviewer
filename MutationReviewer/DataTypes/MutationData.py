from JupyterReviewer.DataTypes.GenericData import GenericData
from JupyterReviewer.Data import Data, DataAnnotation

import pandas as pd
import numpy as np
from typing import Union, List, Dict

class MutationData(Data):
    def __init__(
        self,
        index,
        description,
        mutations_df: pd.DataFrame,
        bams_df: pd.DataFrame,
        mutations_df_sample_col: str,
        chrom_col: str,
        start_pos_col: str,
        bam_df_sample_col: str,
        bam_col: str,
        bai_col: str = None,
        annot_df: pd.DataFrame = None,
        annot_col_config_dict: Dict = None,
        history_df: pd.DataFrame = None,
    ):
        """
        Parameters
        ==========
        mutations_df: pd.DataFrame
            Dataframe with mutations for each sample
        
        """
        super().__init__(
            index=index,
            description=description,
            annot_df=annot_df,
            annot_col_config_dict=annot_col_config_dict,
            history_df=history_df,
        )
        
        required_mutations_df_cols = [mutations_df_sample_col, chrom_col, start_pos_col]
        if not set(
            required_mutations_df_cols
        ).issubset(mutations_df.columns):
            missing_cols = [c for c in required_mutations_df_cols if c not in mutations_df.columns]
            raise ValueError(f'Following columns do not exist in mutations_df dataframe: {missing_cols}')
            
        required_bam_df_cols = [bam_df_sample_col, bam_col]
        if not set(
            required_bam_df_cols
        ).issubset(bams_df.columns):
            missing_cols = [c for c in required_bam_df_cols if c not in bams_df.columns]
            raise ValueError(f'Following columns do not exist in bams_df dataframe: {missing_cols}')
        
        self.mutations_df = mutations_df
        self.bams_df = bams_df
        
        self.mutations_df_sample_col = mutations_df_sample_col
        self.chrom_col = chrom_col
        self.start_pos_col = start_pos_col
        
        self.bam_df_sample_col = bam_df_sample_col
        self.bam_col = bam_col
        self.bai_col = bai_col
        
        self.group_muts_cols = [chrom_col, start_pos_col]
        # self.index = mutations_df[self.group_muts_cols].unique()