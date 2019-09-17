#AUTOGENERATED! DO NOT EDIT! File to edit: dev/42_tabular_rapids.ipynb (unless otherwise specified).

__all__ = ['setups', 'encodes', 'setups', 'encodes', 'setups', 'encodes', 'encodes']

#Cell
from ..torch_basics import *
from ..test import *
from ..core import *
from ..data.all import *
from .core import *
from ..notebook.showdoc import show_doc

#Cell
try: import cudf,nvcategory
except: print("This requires rapids, see https://rapids.ai/ for installation details")

#Cell
@patch
def __array__(self:cudf.DataFrame): return self.pandas().__array__()

#Cell
def _to_str(c): return c if c.dtype == "object" else c.astype("str")
def _remove_none(c):
    if None in c: c.remove(None)
    return c

#Cell
@Categorify
def setups(self, to: TabularGPU):
    self.lbls = {n: nvcategory.from_strings(_to_str(to[:to.split,n]).data).keys() for n in to.all_cat_names}
    self.items = to.classes = {n: CategoryMap(_remove_none(c.to_host()), add_na=True) for n,c in self.lbls.items()}

@patch
def _apply_cats_gpu(self: Categorify, c):
    return cudf.Series(nvcategory.from_strings(_to_str(c).data).set_keys(self.lbls[c.name]).values()).add(1)

@Categorify
def encodes(self, to: TabularGPU): to.transform(to.all_cat_names, self._apply_cats_gpu)

#Cell
@Normalize
def setups(self, to: TabularGPU):
    self.means = {n: to[:to.split,n].mean()           for n in to.cont_names}
    self.stds  = {n: to[:to.split,n].std(ddof=0)+1e-7 for n in to.cont_names}

@Normalize
def encodes(self, to: TabularGPU):
    to.transform(to.cont_names, lambda c: (c-self.means[c.name])/self.stds[c.name])

#Cell
@patch
def median(self:cudf.Series):
    "Get the median of `self`"
    col = self.dropna().reset_index(drop=True).sort_values()
    return col[len(col)//2] if len(col)%2 != 0 else (col[len(col)//2]+col[len(col)//2-1])/2

#Cell
@FillMissing
def setups(self, to: TabularGPU):
    self.na_dict = {}
    for n in to.cont_names:
        col = to.loc[:to.split, n]
        if col.isnull().any(): self.na_dict[n] = self.fill_strategy(col, self.fill_vals[n])

@FillMissing
def encodes(self, to: TabularGPU):
    for n in to.cont_names:
        if n in self.na_dict:
            if self.add_col:
                to.items[n+'_na'] = to.items[n].isnull()
                if n+'_na' not in to.cat_names: to.cat_names.append(n+'_na')
            to.set_col(n, to.items[n].fillna(self.na_dict[n]))
        elif df[n].isnull().any():
            raise Exception(f"nan values in `{n}` but not in setup training set")

#Cell
from torch.utils.dlpack import from_dlpack

@ReadTabBatch
def encodes(self, to: TabularGPU):
    return (from_dlpack(to.cats.to_dlpack()).long(),from_dlpack(to.conts.to_dlpack()).float()), from_dlpack(to.targ.to_dlpack()).long()