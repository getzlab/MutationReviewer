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
    update_tracks_n_clicks,
    bam_table,
    bam_table_selected_rows,
    genome,
    track_height,
    minimumBases,
    gen_data_mut_index_name_func
):
    
    idx_mut_df = data.mutations_df.loc[
        data.mutations_df[data.mutation_groupby_cols].apply(
            lambda r: gen_data_mut_index_name_func(r.astype(str).tolist()), 
            axis=1
        ) == idx,
    ]

    bams_df = pd.DataFrame.from_records(bam_table)
    valid_indices = [i for i in bam_table_selected_rows if i in range(bams_df.shape[0])]
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
        } for _, r in bams_df.iloc[valid_indices].iterrows()
    ]
    
    locus = [f'{idx_mut_df.iloc[0][chrom]}:{idx_mut_df.iloc[0][pos]}' for chrom, pos in zip(data.chrom_cols, data.pos_cols)]
    return gen_igv_session_layout(
        genome=genome, 
        tracks=tracks, 
        locus=locus, 
        minimumBases=minimumBases
    )

def gen_igv_session_update(
    data: GeneralMutationData, 
    idx, 
    update_tracks_n_clicks,
    bam_table,
    bam_table_selected_rows,
    genome,
    track_height,
    minimumBases,
    gen_data_mut_index_name_func
):
    
    return [html.Div()]
    
    # return gen_igv_session_layout(
    #     genome=genome, 
    #     tracks=None, 
    #     locus=None, 
    #     minimumBases=minimumBases
    # )
    


def gen_igv_session_layout(genome, tracks, locus, minimumBases):
    
    
    return [
        dashbio.Igv(
            children='igv',
            id='default-igv',
            genome=genome,
            minimumBases=minimumBases,
            locus=locus,
            tracks=tracks
        )
    ]

def gen_igv_js_component(genome, bam_table_state: State, bam_table_selected_rows_state: State):
    
    return AppComponent(
        name='IGV.js embedded component',
        layout=gen_igv_js_layout(genome),
        new_data_callback=gen_igv_session_update,
        internal_callback=gen_igv_session,
        callback_output=[Output('default-igv-container', 'children')],
        callback_input=[Input('update-tracks-button', 'n_clicks')],
        callback_state_external=[bam_table_state, bam_table_selected_rows_state]
    )

def gen_igv_js_layout(genome):
    
    return html.Div([
        html.Button('Update tracks from bam table', id='update-tracks-button', n_clicks=0),
        dcc.Loading(children="Press button to load IGV", id='default-igv-container'),
    ])
    