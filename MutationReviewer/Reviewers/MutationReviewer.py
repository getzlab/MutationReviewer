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
        
        self.group_muts_cols = [chrom_col, start_pos_col]
        # self.index = mutations_df[self.group_muts_cols].unique()
        

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
        
        def update_mut_table(data: MutationData, idx, mutation_table_display_cols):
            df = data.mutations_df.loc[
                data.mutations_df.apply(
                    lambda r: f'{str(r[data.chrom_col])}:{str(r[data.start_pos_col])}', axis=1
                ) == idx,
                mutation_table_display_cols
            ]
            return [dbc.Table.from_dataframe(df=df)]
        
        app.add_component(
            AppComponent(
                name='Mutation Table',
                layout=html.Div(
                    children=[dbc.Table.from_dataframe(df=pd.DataFrame())],
                    id='mut-table'
                ),
                callback_output=[Output('mut-table', 'children')],
                new_data_callback=update_mut_table
            ),
            mutation_table_display_cols=mutation_table_display_cols
        )
        
        
        def update_bam_table(data: MutationData, idx, bam_table_display_cols, bai_col):
            chrom, pos = idx.split(':')
            pos = int(pos)
            samples = data.mutations_df.loc[
                (data.mutations_df[data.chrom_col] == chrom) & (data.mutations_df[data.start_pos_col] == pos),
                data.mutations_df_sample_col
            ].tolist()
            bams_df = data.bams_df.loc[data.bams_df[data.bam_df_sample_col].isin(samples), bam_table_display_cols]
            load_bams_list = bams_df[data.bam_col].tolist()
            # load_bais_list = bams_df[data.bai_col].tolist()
            load_bais_list = bams_df[bai_col].tolist()
            
            if len(load_bams_list) > 0:
                # load igv
                try:
                    ir.connect()
                except AssertionError:
                    ir.close()
                    ir.connect()
                ir.new()
                ir.set_viewopts(view_type="collapsed", sort="base")
                ir.goto(chrom, pos)
                ir.load(*load_bams_list)
                # ir.load_w_index(load_bams_list, load_bais_list)
                ir.close()
            else:
                ir.connect()
                ir.new()
                ir.close()
            
            return [dbc.Table.from_dataframe(df=bams_df)]
            
            
        app.add_component(
            AppComponent(
                name='Sample Bam table',
                layout=html.Div(
                    children=[dbc.Table.from_dataframe(df=pd.DataFrame())],
                    id='bam-table'
                ),
                callback_output=[Output('bam-table', 'children')],
                new_data_callback=update_bam_table
            ),
            bam_table_display_cols=bam_table_display_cols,
            bai_col=bai_col,
        )
        
        return app
        
    def set_default_review_data_annotations(self):
        self.add_review_data_annotation('Notes', DataAnnotation('string'))
        
    def set_default_review_data_annotations_app_display(self):
        self.add_review_data_annotations_app_display('Notes', 'textarea')
        
    def set_default_autofill(self):
        pass
    