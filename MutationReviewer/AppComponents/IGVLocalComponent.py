import pandas as pd
import numpy as np
import dash
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


from .utils import load_bams_igv, load_bam_igv
from MutationReviewer.DataTypes.GeneralMutationData import GeneralMutationData


def load_igv_session(
    data: GeneralMutationData, 
    idx, 
    update_tracks_n_clicks,
    bam_table,
    bam_table_selected_rows,
    gen_data_mut_index_name_func
):
    
#     idx_mut_df = data.mutations_df.loc[
#         data.mutations_df[data.mutation_groupby_cols].apply(
#             lambda r: gen_data_mut_index_name_func(r.astype(str).tolist()), 
#             axis=1
#         ) == idx,
#     ]

#     bams_df = pd.DataFrame.from_records(bam_table)
#     valid_indices = [i for i in bam_table_selected_rows if i in range(bams_df.shape[0])]
    
#     load_bams_list = bams_df.loc[valid_indices]['bam'].stack().tolist()
#     load_bams_igv(load_bams_list, idx_mut_df.iloc[0][data.chrom_cols], idx_mut_df.iloc[0][data.pos_cols])
    
    return [dash.no_update]

def load_igv_session_update(
    data: GeneralMutationData, 
    idx, 
    update_tracks_n_clicks,
    bam_table,
    bam_table_selected_rows,
    gen_data_mut_index_name_func
):
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
    
    
    

def gen_igv_local_component(bam_table_state: State, bam_table_selected_rows_state: State):
    
    return AppComponent(
        name='Local IGV component',
        layout=gen_igv_local_layout(),
        new_data_callback=load_igv_session,
        internal_callback=load_igv_session_update,
        callback_output=[Output('local-igv-container', 'children')],
        callback_input=[Input('update-local-igv-button', 'n_clicks')],
        callback_state_external=[bam_table_state, bam_table_selected_rows_state]
    )

def gen_igv_local_layout():
    
    return html.Div([
        html.Button('Update local IGV from bam table', id='update-local-igv-button', n_clicks=0),
        dcc.Loading(
            children=html.P(
                """
                1. Open your local IGV
                2. Login with your google acount (Google > login)
                """
            ), 
            id='local-igv-container'
        ),
    ])
    