from django.http import HttpResponse
from django.shortcuts import render_to_response
from simplegraph.models import Node
from simplegraph import graphviz
from pydot import Graph, Edge
from pydot import Node as GNode
import random
from string import ascii_letters

############# utility ###############

valid_after_cleanup = ascii_letters + '_0123456789'



def cleanup(text):
    for char in text:
        if char not in valid_after_cleanup:
            text = text.replace(char,'')            
    return text
    

    
def node_to_dot(node):
    dot = ''
    dot += '%s' % cleanup(node.name)
    dot += ' [label="%s" '% node.name
    if node.node_look:
        dot += ' style=filled color=%s shape=%s' % (node.node_look.color, node.node_look.shape)
    dot += '];\n'    
    return dot
        
def nodes_and_edges_to_dot():
    graph = Graph(cleanup('everything'))    
    edges = []
    node_check = []
    dot = 'graph {\n'
    for node in Node.objects.select_related():
        # gets nodes
        #node = Node(cleanup(node.name))
        dot += node_to_dot(node)

        for parent in node.parent.iterator():
            edges.append((cleanup(parent.parent.name),cleanup(parent.child.name)))

        for child in node.child.iterator():
            edges.append((cleanup(child.parent.name),cleanup(child.child.name)))            

    # remove duplicates        
    edges = list(set(edges))
    for edge in edges:
        dot += '%s -- %s [arrowhead=vee];' % (edge[0], edge[1])
    dot += '}'
    return dot
    
############## new utils ###########    
    
def get_node(name):
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

    
def get_nodes_and_edges(name):
    pass

############# Views ###############


def index(request):
    nodes = Node.objects.all().order_by('name')    
    return render_to_response('index.html',{'nodes':nodes})

def list_nodes(request):
    nodes = Node.objects.all().order_by('name')
    return render_to_response('list_nodes.html',{'nodes':nodes})
    
def dot_all(request):
    return render_to_response(nodes_and_edges_to_dot)
        
def dot_node(request,name):
    graph = get_node_and_edges(name)
    return render_to_response('dot.html',{'dot_export':graph.to_string()})
            
def node_detail(request,name):
    nodes = Node.objects.all().order_by('name')        
    node = Node.objects.select_related().get(name=name)
    parents = [x for x in node.child.iterator()]
    children = [x for x in node.parent.iterator()]
    responsible_party = None
    if node.responsible_party_email and node.responsible_party:
        responsible_party = '<a href="mailto:%s">%s</a>' % (node.responsible_party_email, node.responsible_party)
    elif node.responsible_party_email:
        responsible_party = '<a href="mailto:%s">%s</a>' % (node.responsible_party_email, node.responsible_party_email)
    elif node.responsible_party:
        responsible_party = node.responsible_party
    
    return render_to_response('node_detail.html',{'node':node,
            'nodes':nodes,
            'parents':parents,
            'children':children,
            'responsible_party':responsible_party})
    
def simplegraph_all(request,build_type='dot'):
    image = graphviz.create_simplegraph(nodes_and_edges_to_dot(),build_type=build_type)      
    return HttpResponse(image,mimetype="image/gif")
    
def simplegraph_detail(request,name,build_type='dot'):
    graph = get_node_and_edges(name)
    image = graphviz.create_simplegraph(graph.to_string(),build_type=build_type)      
    return HttpResponse(image,mimetype="image/gif")
    
def random_image(request,build_type='dot'):
    node = random.choice(Node.objects.all())
    graph = get_node_and_edges(node.name)
    image = graphviz.create_simplegraph(graph.to_string(),build_type=build_type)      
    return HttpResponse(image,mimetype="image/gif")    
    
def show_em_all(request):
    nodes = Node.objects.all().order_by('name')    
    return render_to_response('show_em_all.html',{'nodes':nodes})    
