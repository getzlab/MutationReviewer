"""
Connects with the local IGV app, outside of the dashboard. Takes a list of bams to load and a genomic coordinate to go to. 
"""
import pandas as pd
import numpy as np
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pickle
import dash_bio as dashbio

from AnnoMate.Data import Data, DataAnnotation
from AnnoMate.ReviewDataApp import ReviewDataApp, AppComponent
from AnnoMate.DataTypes.GenericData import GenericData

import os
import pickle
import sys

from .utils import load_bams_igv
from MutationReviewer.DataTypes.GeneralMutationData import GeneralMutationData


def load_igv_session(
    data: GeneralMutationData, 
    idx, 
    update_tracks_n_clicks,
    bam_table,
    bam_table_selected_rows,
    gen_data_mut_index_name_func,
):
    """
    Callback function to run when the data to review changes
    
    Parameters
    ----------
    update_tracks_n_clicks: State
        Dash.State of the number of times a button was clicked
        
    bam_table: State
        Dash.State object referencing a state of a dash component containing 
        a table with the bam files
        
    bam_table_selected_rows: State, list
        Dash.State object referencing a state of a dash component referencing 
        which rows are selected in a table with the bam files
        
    gen_data_mut_index_name_func: func
        Function used to parse the index to filter the mutation table
        
    Return
    ------
    
    No updates to the component will be made.
    
    """

    return [dash.no_update]

def load_igv_session_update(
    data: GeneralMutationData, 
    idx, 
    update_tracks_n_clicks,
    bam_table,
    bam_table_selected_rows,
    gen_data_mut_index_name_func,
):
    """
    Callback function to update local IGV when the Update Tracks button is clicked.
    
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
        
    gen_data_mut_index_name_func: func
        Function used to parse the index to filter the mutation table
        
    Return
    ------
    
    No updates to the component will be made.
    
    """
    
    # reset igv
    idx_mut_df = data.mutations_df.loc[
        data.mutations_df[data.mutation_groupby_cols].apply(
            lambda r: gen_data_mut_index_name_func(r.astype(str).tolist()), 
            axis=1
        ) == idx,
    ]

    bams_df = pd.DataFrame.from_records(bam_table)
    valid_indices = [i for i in bam_table_selected_rows if i in range(bams_df.shape[0])]
    
    load_bams_list = bams_df.loc[valid_indices]['bam'].tolist()
    load_bams_igv(load_bams_list, idx_mut_df.iloc[0][data.chrom_cols], idx_mut_df.iloc[0][data.pos_cols])
    
    return [dash.no_update]
    
    
    

def gen_igv_local_component(bam_table_data_state: State, bam_table_selected_rows_state: State):
    '''
    Returns a pre-built AppComponent with a button that will update a running local IGV session 
    on click given which rows are selected in a bam table located in a separate component.
    
    Parameters
    ----------
    bam_table_data_state: State
        Dash.State object referencing the "data" attribute of a dash table (ie State('bam-table', 'data')). 
        This table should contain bam file paths or urls
    
    bam_table_selected_rows_state: State
        Dash.State object that is a list of indices used to select rows from the data 
        in bam_table_data_state (ie State('bam-table', 'selected-rows')). 
        
    Returns
    -------
    AppComponent
        Interactive component that communicates with a local IGV app
    '''
    
    return AppComponent(
        name='Local IGV component',
        layout=gen_igv_local_layout(),
        new_data_callback=load_igv_session,
        internal_callback=load_igv_session_update,
        callback_output=[Output('local-igv-container', 'children')],
        callback_input=[Input('update-local-igv-button', 'n_clicks')],
        callback_state_external=[bam_table_data_state, bam_table_selected_rows_state]
    )

def gen_igv_local_layout():
    """
    Generates dash layout for interacting with a local IGV app
    
    Returns
    -------
    dash.html
        plotly dash layout
    """
    
    return html.Div([
        html.Button('Update local IGV from bam table', id='update-local-igv-button', n_clicks=0),
        dcc.Loading(
            children=html.P(
                """
                1. Open your local IGV
                2. Login with your google acount (Google > login) if bam paths are gsurls
                """
            ), 
            id='local-igv-container'
        ),
    ])
    