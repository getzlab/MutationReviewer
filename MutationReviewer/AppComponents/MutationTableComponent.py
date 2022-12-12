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

from MutationReviewer.DataTypes.GeneralMutationData import GeneralMutationData


def gen_mutation_table_component():
    return AppComponent(
        name='Mutation Table',
        layout=gen_mutation_table_layout(),
        callback_output=[Output('mut-table', 'children')],
        new_data_callback=update_mut_table
    )

def gen_mutation_table_layout():
    return html.Div(
        children=[dbc.Table.from_dataframe(df=pd.DataFrame())],
        id='mut-table'
    )

def update_mut_table(
    data: GeneralMutationData, 
    idx, 
    mutation_table_display_cols
):
    df = data.mutations_df.loc[
        data.mutations_df.apply(
            lambda r: ':'.join(r[data.group_muts_cols].astype(str).tolist()), axis=1
        ) == idx,
        mutation_table_display_cols
    ]
    return [dbc.Table.from_dataframe(df=df)]
