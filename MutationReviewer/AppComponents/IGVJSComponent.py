"""
Displays an internal IGV session inside the dashboard. Takes a list of bams to load and a genomic coordinate to go to. 
"""
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
from MutationReviewer.DataTypes.GeneralMutationData import GeneralMutationData


import os
import shlex
from subprocess import Popen, PIPE

def get_gcs_oauth_token(
    set_env_command=None, 
    access_token_command='gcloud auth application-default print-access-token'
):
    '''
    Generates gcloud oauth token for data access
    
    Parameters
    ----------
    set_env_command: str
        bash command to run to set the environment before running the command to get the access token
    access_token_command: str
        bash command to get the access token. Default is for gcloud
    
    Returns
    -------
    str
        Authorization token for loading remote bams in IGV
    '''
    if set_env_command:
        full_command = f'bash -c "{set_env_command}; {access_token_command}"'
    else:
        full_command = access_token_command
        
    command = shlex.split(full_command)
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
    gen_data_mut_index_name_func,
    set_env_command=None,
):
    """
    Callback function to generate an IGV.js window centered around the locus/loci of interest 
    and specified bams loaded when the Update Tracks button is clicked.
    
    Parameters
    ------
    update_tracks_n_clicks: State
        Dash.State of the number of times a button was clicked
        
    bam_table: State
        Dash.State object referencing a state of a dash component containing 
        a table with the bam files
        
    bam_table_selected_rows: State, list
        Dash.State object referencing a state of a dash component referencing 
        which rows are selected in a table with the bam files
        
    genome: string, default='hg19'
            Name of genome to use in IGV.js
        
    track_height: int, default=400
        Height to display each track in IGV.js mode

    minimumBases: int, default=200
        Minimum number of bases to display in a window in IGV.js mode
        
    gen_data_mut_index_name_func: func
        Function used to parse the index to filter the mutation table
        
    Return
    ------
    A dash_bio.IGV component
        Contains the tracks specified to load and window centering around the locus (or loci) of interest
    
    """
    
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
            'oauthToken': get_gcs_oauth_token(set_env_command=set_env_command),
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
    gen_data_mut_index_name_func,
    set_env_command=None,
):
    '''
    See gen_igv_session()
    '''
    
    return [html.Div()]
    


def gen_igv_session_layout(genome, tracks, locus, minimumBases):
    """
    Generate layout for displaying IGV inside the dashboard. See https://dash.plotly.com/dash-bio/igv
    
    Parameters
    ----------
    genome: str
        Select a genome using an identifier string (e.g. "hg19"). A list of pre-defined genomes hosted by IGV can be found here: https://s3.amazonaws.com/igv.org.genomes/genomes.json.
        
    tracks: 
        Array of configuration objects defining tracks initially displayed when app launches. See https://github.com/igvteam/igv.js/wiki/Tracks-2.0
        
    locus: str, List[str]
        String or list of strings formatted for querying regions of the genome (ie 'chr#', 'chr#:###-###', ['chr2', 'chr3']
        
    minimumBases: int
        Minimum window size in base pairs when zooming in
        
    Returns
    -------
    plotly.dash.html
        Layout for dash
    """
    
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

def gen_igv_js_component(bam_table_state: State, bam_table_selected_rows_state: State) -> AppComponent:
    '''
    Returns a pre-built AppComponent with a button that will update a running local IGV session 
    on click given which rows are selected in a bam table located in a separate component.
    
    Parameters
    ----------
    bam_table_state: State
        Dash.State object referencing the "data" attribute of a dash table (ie State('bam-table', 'data')). 
        This table should contain bam file paths or urls
    
    bam_table_selected_rows_state: State
        Dash.State object that is a list of indices used to select rows from the data 
        in bam_table_state (ie State('bam-table', 'selected-rows')). 
        
    Returns
    -------
    AppComponent
        Interactive component rendering IGV.js
    '''
    
    return AppComponent(
        name='IGV.js embedded component',
        layout=gen_igv_js_layout(),
        new_data_callback=gen_igv_session_update,
        internal_callback=gen_igv_session,
        callback_output=[Output('default-igv-container', 'children')],
        callback_input=[Input('update-tracks-button', 'n_clicks')],
        callback_state_external=[bam_table_state, bam_table_selected_rows_state]
    )

def gen_igv_js_layout():
    """
    Generates dash layout container to hold the igv.js element
    
    Returns
    -------
    dash.html
        Plotly dash layout
    """
    
    return html.Div([
        html.Button('Update tracks from bam table', id='update-tracks-button', n_clicks=0),
        dcc.Loading(children="Press button to load IGV", id='default-igv-container'),
    ])
    