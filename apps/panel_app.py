import numpy as np
import panel as pn
import pandas as pd

import panel.widgets as pnw


import altair as alt
pn.extension('vega')
alt.renderers.enable('notebook')
pn.extension()


N = 600
seed = 3423# 42
np.random.seed(seed)


source = pd.DataFrame(#np.cumsum(np.random.randn(1000, 1), 0).round(2),
                    np.random.normal(1, 1, N),
                    columns=['A'], index=pd.RangeIndex(N, name='x'))
source = source.reset_index().melt('x', var_name='category', value_name='y')
source["y"] = np.exp(source["y"])

window_size  = pnw.IntSlider(name='size', value=10, start=0, end=50)

variable_list = ['y_rolling', 'y_rolling_median']
variable = pnw.Select(options=variable_list, name='Variable')

@pn.depends(window_size.param.value)
def update_source(size):
    
    source["y_rolling"] = source["y"].rolling(size).mean(center = True)
    source["y_rolling_median"] = source["y"].rolling(size).median(center = True)
    
    return None
    

@pn.depends(window_size.param.value, variable.param.value)
def plot_lines(size, param):
    

    line = alt.Chart(source).mark_line().encode(
        x='x',
        y='y'
    )

    cf  = alt.Chart(source).mark_line(color="red").encode(
        x='x',
        y='y_rolling'
    )
    
    cf_2  = alt.Chart(source).mark_line(color="green").encode(
        x='x',
        y='y_rolling_median'
    )

    plat = line+cf+cf_2
    
    return plat.properties(width=800,height=300)


@pn.depends(window_size.param.value, variable.param.value)
def plot_lines_mean(size, param):
    

    line = alt.Chart(source).mark_line().encode(
        x='x',
        y='y'
    )

    cf  = alt.Chart(source).mark_line(color="red").encode(
        x='x',
        y='y_rolling'
    )
    
    cf_2  = alt.Chart(source).mark_line(color="green").encode(
        x='x',
        y='y_rolling_median'
    )

    plat = cf+cf_2
    return plat.properties(width=800,height=300)


@pn.depends(variable.param.value, window_size.param.value)
def plot_hist(col, size):
    plat = alt.Chart(source).mark_bar().encode(alt.X(col, bin=True),
    y='count()')
    
    return plat


widgets = pn.Column(window_size, variable)

panelz = pn.Column(widgets, pn.Column(update_source, plot_lines, plot_lines_mean, plot_hist))

#panelz.servable()
panelz.show()

