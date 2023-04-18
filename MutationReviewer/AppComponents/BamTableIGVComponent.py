import pandas as pd
import numpy as np
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pickle

from JupyterReviewer.Data import Data, DataAnnotation
from JupyterReviewer.ReviewDataApp import ReviewDataApp, AppComponent
from JupyterReviewer.DataTypes.GenericData import GenericData

import os
import pickle
import sys

# import igv_remote as ir

from .utils import load_bams_igv, load_bam_igv
from MutationReviewer.DataTypes.GeneralMutationData import GeneralMutationData


def gen_mutation_table_igv_component(
    bam_table_display_cols,
    bam_table_page_size=10,
    init_max_bams_view=3
):
    
    return AppComponent(
        name='Sample Bam table',
        layout=gen_mutation_table_igv_layout(bam_table_display_cols, bam_table_page_size, init_max_bams_view),
        callback_output=[Output('bam-table', 'data')],
        callback_input=[Input('bam-table', 'selected_rows')],
        new_data_callback=update_bam_table
    )

def gen_mutation_table_igv_layout(
    bam_table_display_cols,
    bam_table_page_size,
    init_max_bams_view
):
    return html.Div(
        children=[
            # dbc.Table.from_dataframe(df=pd.DataFrame())
            dash_table.DataTable(
                id='bam-table',
                columns=[
                    {"name": i, "id": i} for i in bam_table_display_cols
                ],
                data=pd.DataFrame().to_dict('records'),
                filter_action="native",
                sort_action="native",
                sort_mode="multi",
                column_selectable="single",
                row_selectable="multi",
                selected_rows=list(range(init_max_bams_view)),
                page_action="native",
                page_current= 0,
                page_size=bam_table_page_size,
            )
        ],
    )

def update_bam_table(
    data: GeneralMutationData, 
    idx, 
    bam_table_selected_rows,
    bam_table_display_cols
):
    chrom, pos = idx.split(':', 1)
    pos = int(pos)
    samples = data.mutations_df.loc[
        (data.mutations_df[data.chrom_col] == chrom) & (data.mutations_df[data.start_pos_col] == pos),
        data.mutations_df_sample_col
    ].tolist()
    bams_df = data.bams_df.loc[data.bams_df[data.bam_df_sample_col].isin(samples), bam_table_display_cols]
    load_bams_list = bams_df[data.bam_col].tolist()

    # load_bams_igv(load_bams_list, chrom, pos)
    
    return [bams_df.to_dict('records')]
    
    
