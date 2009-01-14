"""
graphviz.py

Created by Daniel Greenfeld on 2009-12-3.
"""

import os
import tempfile

from pydot import Graph, Edge
from pydot import Node as GNode
from string import ascii_letters
from simplegraph.models import Node

valid_after_cleanup = ascii_letters + '_0123456789'

def find_graphviz():
	"""Locate graphviz's executables in the system.

	Attempts  to locate  graphviz's  executables in a Unix system.
	It will look for 'dot', 'twopi' and 'neato' in all the directories
	specified in the PATH environment variable.
	It will return a dictionary containing the program names as keys
	and their paths as values.
	
	-- Adopted from pydot as written by Ero Carrera
    __author__ = 'Ero Carrera'
    __version__ = '0.9.10'
    __license__ = 'MIT'	"""
	progs = {'dot': '', 'twopi': '', 'neato': '', 'circo': '', 'fdp': ''}
	if not os.environ.has_key('PATH'):
		return None
	for path in os.environ['PATH'].split(os.pathsep):
		for prg in progs.keys():
			if os.path.exists(path+os.path.sep+prg):
				progs[prg] = path+os.path.sep+prg
			elif os.path.exists(path+os.path.sep+prg + '.exe'):
				progs[prg] = path+os.path.sep+prg + '.exe'
	return progs
	
def create_simplegraph(input_dot,format='gif',build_type='dot'):
    """ create a simplegraph from a dot script in the specified format
        Inspired by the create and write simplegraph methods from pydot.
    """
    dot = find_graphviz().get(build_type,None)
    if not dot:
        return None
    tmp_fd, tmp_name = tempfile.mkstemp()
    tmp_name = 'simplegraph.test.gif'
    os.close(tmp_fd)
    dot_file = file(tmp_name,'w+b')
    dot_file.write(input_dot)
    dot_file.close()
    command = dot + ' -T'+format+ ' '+tmp_name
    stdin, stdout, stderr = os.popen3(command,'b')
    stdin.close()
    stderr.close()
    data = stdout.read()
    stdout.close()
    os.unlink(tmp_name)
    return data




def cleanup(text):
    for char in text:
        if char not in valid_after_cleanup:
            text = text.replace(char,'')            
    return text

def get_node(name):
    # modify to accept orm_nodes
    node = GNode(cleanup(name))
    orm_node = Node.objects.select_related().get(name=name)    
    node.set_color(orm_node.node_look.color)
    node.set_shape(orm_node.node_look.shape)
    node.set_style('filled')
    return node

def get_node_and_edges(name):
    graph = Graph(cleanup(name))
    orm_node = Node.objects.select_related().get(name=name)    
    other_nodes = [x for x in orm_node.parent.iterator()]
    other_nodes += [x for x in orm_node.child.iterator()]
    edges = []
    node_check = [] # used to make sure we don't add the same node twice
    for other_node in other_nodes:
        if other_node.parent.name not in node_check:
            graph.add_node(get_node(other_node.parent.name))
            node_check.append(other_node.parent.name)
        if other_node.child.name not in node_check:
            graph.add_node(get_node(other_node.child.name))        
            node_check.append(other_node.child.name)

        # edges are tuples
        edges.append((cleanup(other_node.parent.name),cleanup(other_node.child.name))) 

    edges = list(set(edges)) # remove duplicates
    for edge in edges:
        e = Edge(edge[0],edge[1])
        e.set_arrowhead('vee')
        graph.add_edge(e)
    return graph


def get_nodes_and_edges(name='my_graph'):
    graph = Graph(cleanup(name))
    edges = []
    for orm_node in Node.objects.select_related():
        graph.add_node(get_node(orm_node.name))
        for parent in orm_node.parent.iterator():
            edges.append((cleanup(parent.parent.name),cleanup(parent.child.name)))

        for child in orm_node.child.iterator():
            edges.append((cleanup(child.parent.name),cleanup(child.child.name)))            

    edges = list(set(edges)) # remove duplicates   
    for edge in edges:
        e = Edge(edge[0],edge[1])
        e.set_arrowhead('vee')
        graph.add_edge(e)            
    return graph
    
    
if __name__ == '__main__':
    print find_graphviz()
    dot = """simplegraph uml {
    	one -- two;
    }"""
    t = create_simplegraph(dot)
    print len(t)
