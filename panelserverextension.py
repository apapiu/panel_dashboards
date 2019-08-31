from subprocess import Popen

def load_jupyter_server_extension(nbapp):
    """serve the bokeh-app directory with bokeh server"""
    Popen(["panel", "serve", "apps/mean_filter.ipynb", "--allow-websocket-origin=*"])
