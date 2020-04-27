#!/bin/sh
# WARNING: might want to use the GUI for this, current jupyter lab version
#   fails to rebuild frontend after installing them
jupyter labextension install @jupyterlab/toc
jupyter labextension install @aquirdturtle/collapsible_headings
