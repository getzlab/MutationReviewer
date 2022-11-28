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

import igv_remote as ir

from .utils import load_bams_igv
from MutationReviewer.DataTypes.MutationData import MutationData


def gen_mutation_table_igv_component():
    
    return AppComponent(
        name='Sample Bam table',
        layout=gen_mutation_table_igv_layout(),
        callback_output=[Output('bam-table', 'children')],
        new_data_callback=update_bam_table
    )

def gen_mutation_table_igv_layout():
    return html.Div(
        children=[dbc.Table.from_dataframe(df=pd.DataFrame())],
        id='bam-table'
    )

def update_bam_table(
    data: MutationData, 
    idx, 
    bam_table_display_cols
):
    chrom, pos = idx.split(':')
    pos = int(pos)
    samples = data.mutations_df.loc[
        (data.mutations_df[data.chrom_col] == chrom) & (data.mutations_df[data.start_pos_col] == pos),
        data.mutations_df_sample_col
    ].tolist()
    bams_df = data.bams_df.loc[data.bams_df[data.bam_df_sample_col].isin(samples), bam_table_display_cols]
    load_bams_list = bams_df[data.bam_col].tolist()

    load_bams_igv(load_bams_list, chrom, pos)

    return [dbc.Table.from_dataframe(df=bams_df)]


