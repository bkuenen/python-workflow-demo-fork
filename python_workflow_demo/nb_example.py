# %% [markdown]
# This will work exactly the same as the ipynb when opened in jupyter
# %%
from hhnk_threedi_tools.core.api.calculation_gui_class import StartCalculationGui
from IPython.display import HTML, display

display(HTML("<style>.container {width:90% !important;}</style>"))

self = StartCalculationGui(data={})
display(self.tab)


# %%
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
# %%
print("This is a test")

# %%
df = pd.DataFrame([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
df.columns = ["a"]
df



# %%
