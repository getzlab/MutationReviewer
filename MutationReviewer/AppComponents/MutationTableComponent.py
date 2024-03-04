"""
Table of mutations. Mutations can be grouped by different features, and all mutations that are within a group are displayed (ie by patient (tumors and normal) or exclusively by sample).
"""
import pandas as pd
import numpy as np
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pickle

from AnnoMate.Data import Data, DataAnnotation
from AnnoMate.ReviewDataApp import ReviewDataApp, AppComponent
from AnnoMate.DataTypes.GenericData import GenericData

import os
import pickle
import sys

from MutationReviewer.DataTypes.GeneralMutationData import GeneralMutationData


def gen_mutation_table_component():
    """
    Generates table of occurences of the mutation from a maf file
    
    Returns
    -------
    AppComponent
        Interactive component displaying all occurences of the selected mutation
    """
    return AppComponent(
        name='Mutation Table',
        layout=gen_mutation_table_layout(),
        callback_output=[Output('mut-table', 'children')],
        new_data_callback=update_mut_table
    )

def gen_mutation_table_layout():
    """
    Generates dash layout for the mutation table in the dashboard
    
    Returns
    -------
    dash.html
        plotly dash layout
    """
    return html.Div(
        children=[dbc.Table.from_dataframe(df=pd.DataFrame())],
        id='mut-table'
    )

def update_mut_table(
    data: GeneralMutationData, 
    idx, 
    mutation_table_display_cols,
    gen_data_mut_index_name_func,
):
    """
    Callback function to update the mutation table when a new mutation is selected
    
    Parameters
    ----------
    data: GeneralMutationData
        Data object storing the relevant data for mutation review
        
    idx: str
        Current mutation to be reviewed
        
    mutation_table_display_cols: List[str]
        List of column names in the maf file to display in the mutation table
        
    gen_data_mut_index_name_func: func
        Function that regenerates the mutation index to match which rows in the maf to display given the currently selected mutation
        
    Returns
    -------
    dash.Table
        Dash table displaying all relevant mutations given the selected mutation
    """
    df = data.mutations_df.loc[
        data.mutations_df.apply(
            lambda r: gen_data_mut_index_name_func(r[data.mutation_groupby_cols].astype(str).tolist()), 
            axis=1
        ) == idx,
        mutation_table_display_cols
    ]
    return [dbc.Table.from_dataframe(df=df)]
