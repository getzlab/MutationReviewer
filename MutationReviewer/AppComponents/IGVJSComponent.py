import pandas as pd
import numpy as np
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pickle
import dash_bio as dashbio

from JupyterReviewer.Data import Data, DataAnnotation
from JupyterReviewer.ReviewDataApp import ReviewDataApp, AppComponent
from JupyterReviewer.DataTypes.GenericData import GenericData

import os
import pickle
import sys

# import igv_remote as ir

# from .utils import load_bams_igv, load_bam_igv
from MutationReviewer.DataTypes.GeneralMutationData import GeneralMutationData


import os
import shlex
from subprocess import Popen, PIPE
def get_gcs_oauth_token():
    command = shlex.split('gcloud auth application-default print-access-token')
    process = Popen(command, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    GCS_OAUTH_TOKEN = stdout.decode()
    return GCS_OAUTH_TOKEN

def gen_igv_session(
    data: GeneralMutationData, 
    idx, 
    # bam_table_selected_rows,
    bam_table_display_cols, # not including the bam and bai cols
    genome,
    track_height,
    gen_data_mut_index_name_func
):
    
    idx_mut_df = data.mutations_df.loc[
        data.mutations_df[data.mutation_groupby_cols].apply(
            lambda r: gen_data_mut_index_name_func(r.astype(str).tolist()), 
            axis=1
        ) == idx,
    ]
    
    bam_ref_values = idx_mut_df[data.mutations_df_bam_ref_col].tolist()
    
    bams_df = data.bams_df.loc[data.bams_df[data.bams_df_ref_col].isin(bam_ref_values)].copy()

    stack_cols = [data.bams_df_ref_col] + bam_table_display_cols
    
    stack_bams_df = pd.concat(
        [
            bams_df.set_index(stack_cols)[data.bam_cols].stack().reset_index().rename(columns={0: 'bam'}), 
            bams_df.set_index(stack_cols)[data.bai_cols].stack().reset_index().rename(columns={0: 'bai'}), 
        ],
        axis=1
    )
    
    stack_bams_df = stack_bams_df.loc[:,~stack_bams_df.columns.duplicated()]

    tracks = [
        {
            'name': r[data.bams_df_ref_col],
            'url': str(r['bam']),
            'indexURL': str(r['bai']),
            'displayMode': "COLLAPSED",
            'oauthToken': get_gcs_oauth_token(),
            'showCoverage': True,
            'height': track_height,
            'color': 'rgb(170, 170, 170)'
        } for _, r in stack_bams_df.iterrows()
    ]
    
    locus = [f'{idx_mut_df.iloc[0][chrom]}:{idx_mut_df.iloc[0][pos]}' for chrom, pos in zip(data.chrom_cols, data.pos_cols)]
    return gen_igv_session_layout(
        genome=genome, 
        tracks=tracks, 
        locus=locus, 
        # minimumBases=
    )

def gen_igv_session_layout(genome, tracks, locus):
    
    
    return [
        dashbio.Igv(
            children='igv',
            id='default-igv',
            genome=genome,
            minimumBases=100,
            locus=locus,
            tracks=tracks
        )
    ]

def gen_igv_js_component():
    
    return AppComponent(
        name='IGV.js embedded component',
        layout=gen_mutation_table_igv_layout(),
        new_data_callback=gen_igv_session,
        internal_callback=gen_igv_session,
        callback_output=[Output('default-igv-container', 'children')],
    )

def gen_mutation_table_igv_layout():
    
    return html.Div([
        dcc.Loading(children='test', id='default-igv-container'),
    ])
    