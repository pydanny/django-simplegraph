from django.http import HttpResponse
from django.shortcuts import render_to_response
from simplegraph.models import Node
from simplegraph import graphviz

############# utility ###############

CLEANUP_TARGETS = ('.',' ','-')

def cleanup(text):
    for target in CLEANUP_TARGETS:
        text = text.replace(target,'')
    return text
    

    
def node_to_dot(node):
    dot = ''
    dot += '%s' % cleanup(node.name)
    dot += ' [label="%s" '% node.name
    if node.node_look:
        dot += ' style=filled color=%s shape=%s' % (node.node_look.color, node.node_look.shape)
    dot += '];\n'    
    return dot
    
def node_and_edges_to_dot(name):
    edges = []
    other_nodes = []
    dot = 'simplegraph {\n'
    node = Node.objects.select_related().get(name=name)
    dot += node_to_dot(node)
    
    for parent in node.parent.iterator():
        edges.append((cleanup(parent.parent.name),cleanup(parent.child.name)))
        other_nodes.append(parent.child)

    for child in node.child.iterator():
        edges.append((cleanup(child.parent.name),cleanup(child.child.name)))            
        other_nodes.append(child.parent)        

    # remove duplicates        
    edges = list(set(edges))

    for node in other_nodes:
        dot += node_to_dot(node)

    for edge in edges:
        dot += '%s -- %s [arrowhead=vee];' % (edge[0], edge[1])
    dot += '}'
    return dot    
    
def nodes_and_edges_to_dot():
    edges = []
    dot = 'simplegraph {\n'
    for node in Node.objects.select_related():
        # gets apps
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

############# Views ###############


def index(request):
    nodes = Node.objects.all().order_by('name')
    return render_to_response('index.html',{'nodes':nodes})
    
def dot_all(request):
    return render_to_response(nodes_and_edges_to_dot)
        
def dot_node(request,name):
    return render_to_response(node_and_edges_to_dot)
            
def node_detail(request,name):
    node = Node.objects.select_related().get(name=name)
    parents = [x for x in node.parent.iterator()]
    children = [x for x in node.child.iterator()]
    responsible_party = None
    if node.responsible_party_email and node.responsible_party:
        responsible_party = '<a href="mailto:%s">%s</a>' % (node.responsible_party_email, node.responsible_party)
    elif node.responsible_party_email:
        responsible_party = '<a href="mailto:%s">%s</a>' % (node.responsible_party_email, node.responsible_party_email)
    elif node.responsible_party:
        responsible_party = node.responsible_party
    
    return render_to_response('node_detail.html',{'node':node,
            'parents':parents,
            'children':children,
            'responsible_party':responsible_party})
    
def simplegraph_all(request,build_type='dot'):
    image = graphviz.create_simplegraph(nodes_and_edges_to_dot(),build_type=build_type)      
    return HttpResponse(image,mimetype="image/gif")
    
def simplegraph_detail(request,name,build_type='dot'):
    image = graphviz.create_simplegraph(node_and_edges_to_dot(name),build_type=build_type)      
    return HttpResponse(image,mimetype="image/gif")
    
