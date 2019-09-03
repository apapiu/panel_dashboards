from subprocess import Popen

def load_jupyter_server_extension(nbapp):
    """serve the bokeh-app directory with bokeh server"""
    Popen(["panel", "serve", "apps/s_and_p_500.ipynb", "--allow-websocket-origin=*"])
