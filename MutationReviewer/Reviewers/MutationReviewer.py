from JupyterReviewer.ReviewerTemplate import ReviewerTemplate
from JupyterReviewer.ReviewDataApp import ReviewDataApp, AppComponent
from JupyterReviewer.DataTypes.GenericData import GenericData
from JupyterReviewer.Data import Data, DataAnnotation
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
from typing import Dict, List
import plotly.express as px
import dash_bootstrap_components as dbc
import igv_remote as ir

import pandas as pd
import numpy as np
from MutationReviewer.AppComponents.BamTableIGVComponent import gen_mutation_table_igv_component
from MutationReviewer.AppComponents.MutationTableComponent import gen_mutation_table_component
from MutationReviewer.DataTypes.MutationData import MutationData
        

class MutationReviewer(ReviewerTemplate):
    def gen_data(
        self,
        description: str,
        mutations_df: pd.DataFrame,
        bams_df: pd.DataFrame,
        mutations_df_sample_col: str,
        chrom_col: str,
        start_pos_col: str,
        bam_df_sample_col: str,
        bam_col: str,
        bai_col: str,
        annot_df: pd.DataFrame = None,
        annot_col_config_dict: Dict = None,
        history_df: pd.DataFrame = None,
        index: List = None,
    ) -> Data:
        """
        Parameters
        ==========
        mutations_df: pd.DataFrame,
        bams_df: pd.DataFrame,
        mutations_df_sample_col: str,
        chrom_col: str,
        start_pos_col: str,
        bam_df_sample_col: str,
        bam_col: str,
        bai_col: str,
        """
        index = [f'{chrom}:{pos}' for chrom, pos in mutations_df.groupby([chrom_col, start_pos_col]).sum().index]
        mutations_df[chrom_col] = mutations_df[chrom_col].astype(str)
        return MutationData(
            index=index,
            description=description,
            annot_df=annot_df,
            annot_col_config_dict=annot_col_config_dict,
            history_df=history_df,
            mutations_df=mutations_df,
            bams_df=bams_df,
            mutations_df_sample_col=mutations_df_sample_col,
            chrom_col=chrom_col,
            start_pos_col=start_pos_col,
            bam_df_sample_col=bam_df_sample_col,
            bam_col=bam_col,
            bai_col=bai_col
        )
        
        
    def gen_review_app(
        self,
        mutation_table_display_cols,
        bam_table_display_cols,
        bai_col
    ) -> ReviewDataApp:
        """
        Parameters
        ==========
        mutation_table_display_cols
        bam_table_display_cols
        """
        app = ReviewDataApp()
        
        app.add_component(
            gen_mutation_table_component(),
            mutation_table_display_cols=mutation_table_display_cols
        )
        
        app.add_component(
            gen_mutation_table_igv_component(),
            bam_table_display_cols=bam_table_display_cols,
        )
        
        return app
        
    def set_default_review_data_annotations(self):
        self.add_review_data_annotation('Notes', DataAnnotation('string'))
        
    def set_default_review_data_annotations_app_display(self):
        self.add_review_data_annotations_app_display('Notes', 'textarea')
        
    def set_default_autofill(self):
        pass
    