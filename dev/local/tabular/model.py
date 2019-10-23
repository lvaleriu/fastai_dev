#AUTOGENERATED! DO NOT EDIT! File to edit: dev/41_tabular_model.ipynb (unless otherwise specified).

__all__ = []

#Cell
from ..torch_basics import *
from ..test import *
from .core import *

#Cell
@typedispatch
def show_results(x:Tabular, y:Tabular, samples, outs, ctxs=None, max_n=10, **kwargs):
    df = x.all_cols[:max_n]
    df[to.y_names+'_pred'] = y[to.y_names][:max_n].values
    display_df(df)