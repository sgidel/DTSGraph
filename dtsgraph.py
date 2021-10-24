#!/usr/bin/env python3
# MIT License
#
# Copyright (c) 2021 Sam Gidel
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import sys
import argparse
import pathlib
import json

# only enable graph support if the module can be loaded
try:
    import pygraphviz as pgv
    graphviz_supported = True
except Exception as e:
    print("pygraphviz couldnt be loaded. Disabling image support.\n" + str(e), file=sys.stderr)
    graphviz_supported = False



parser = argparse.ArgumentParser(description="Generate a graph of device tree dependencies")

parser.add_argument('srcdir', help="Source directory to look in")
parser.add_argument('dts', help="Top level device tree to parse, relative to srcdir")
# Disable graphviz support when it isnt available
ofdefault = 'graphimg' if graphviz_supported else 'none'
ofchoices = ['json', 'graphimg', 'dot'] if graphviz_supported else ['json']
parser.add_argument('-f', '--format', choices=ofchoices, default=ofdefault, dest='format', help="Graph output type, defaults to " + ofdefault)
parser.add_argument('-o', '--outputfile', dest='filename', default=None, help="Use custom output file name, defaults to dts name. In JSON mode, 'stdout' will print directly to console")
parser.add_argument('-n', '--noheader', dest='noheader', action='store_true', help="Disable resolution of .h files")
args = parser.parse_args()

srcdir = pathlib.Path(args.srcdir)
if not srcdir.exists():
    print('srcdir {} not found. Check and try again'.format(str(srcdir)), file=sys.stderr)
    exit(1)

# Find all dts/dtsi/h files in src directory
paths_full = []
if(args.noheader is True):
    glob = '*.dts*'
else:
    glob = '*.[h,dts]*'
for path in srcdir.rglob(glob):
    rpath = path.relative_to(srcdir)
    paths_full.append(rpath)

# Look up a partial path and see if it is in the src directory,
# returns full path relative to srcdir
def searchFile(filename):
    for path in paths_full:
        if filename in str(path):
            return path
        
    return None
# parse include statements out of given file and return a list of partial filenames
def read_includes(file):
    includes = []
    try:
        with open(srcdir.joinpath(pathlib.Path(file))) as f:
            for ln in f:
                if ln.startswith('#include'):
                    incl_name = ln.split(' ')[1].strip('"<>\n')
                    includes.append(incl_name)
    except Exception as e:
        print("Failed to open file: " + str(e), file=sys.stderr)
        exit(3)
    return includes

# recursively resolve all includes starting from the given top level device tree
def recurse_resolve(file, node, graph):
    
    includes = read_includes(file)
    for include in includes:
        incfile = searchFile(include)
        if incfile is not None:
            # add nodes to graph if in graphviz mode
            if graph is not None:
                graph.add_edge(str(file), str(incfile))
            node[str(incfile)] = {}
            recurse_resolve(incfile, node[str(incfile)], graph)

top_file = pathlib.Path(args.dts)
if not srcdir.joinpath(top_file).exists():
    print("Error: Top level device tree {} not found in {}".format(str(top_file), str(srcdir)), file=sys.stderr)
    exit(2)

# recursion state keeper and json output tree
depgraph = {str(top_file): {}}

if(args.format == "graphimg" or args.format == "dot"):
    dotgraph = pgv.AGraph(directed=True, strict=True)
    dotgraph.graph_attr["ranksep"] = "10"
    dotgraph.node_attr['shape'] = 'rectangle'
    dotgraph.node_attr['height'] = '1'
else:
    dotgraph = None

recurse_resolve(top_file, depgraph[str(top_file)], dotgraph)


# write output
try:
    if(args.format == "graphimg"):
        if(args.filename is not None):
            outputfile = args.filename
        else:
            outputfile = str(top_file.stem) + '-graph.svg'
        dotgraph.draw(outputfile, prog='dot')
        exit(0)
    elif(args.format == "dot"):
        if(args.filename is not None):
            outputfile = args.filename
        else:
            outputfile = str(top_file.stem) + '-graph.dot'
        dotgraph.write(outputfile)
        exit(0)
    else:
        # JSON mode
        jsongraph = json.dumps(depgraph, indent=4)
        if(args.filename == "stdout"):
            print(jsongraph)
            exit(0)
        elif(args.filename is not None and args.filename != "stdout"):
            filename = args.filename
        else:
            filename = str(top_file.stem) + '-graph.json'
        with open(filename, 'w') as f:
            f.write(jsongraph)
            f.close()
        exit(0)
except Exception as e:
    print("Failed open output file for writing: " + str(e), file=sys.stderr)
    exit(4)