from django.http import HttpResponse
from django.shortcuts import render_to_response
from simplegraph.models import Node, Edge, COLOR_CHOICES, SHAPE_CHOICES
from simplegraph import graphviz
from simplegraph.graphviz import get_node, get_node_and_edges, get_nodes_and_edges
import random
import csv
############# Views ###############


def index(request):
    nodes = Node.objects.all().order_by('name')
    colors = [x[0] for x in COLOR_CHOICES]
    shapes = [x[0] for x in SHAPE_CHOICES]    
    return render_to_response('index.html',{'nodes':nodes,'colors':colors,'shapes':shapes})

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
    graph = get_nodes_and_edges()
    image = graphviz.create_simplegraph(graph.to_string(),build_type=build_type)      
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
    
def csv_all(request):
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=export.csv'
    writer = csv.writer(response)
    writer.writerow(['NODE_NAME','RESPONSIBLE PARTY','RESPONSIBLE_PARTY_EMAIL','NODE_TYPE','DESCRIPTION'])
    for node in Node.objects.all().order_by('name'):
        writer.writerow([node.name, node.responsible_party, node.responsible_party_email, node.node_look, node.description])
    writer.writerow([])
    writer.writerow(['EDGE_PARENT','EDGE_CHILD','EDGE_TYPE'])
    for edge in Edge.objects.all():
        writer.writerow([edge.parent,edge.child,edge.edge_type])
    return response
    
def csv_node(request,name):
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=export.csv'
    writer = csv.writer(response)
    writer.writerow(['NODE_NAME','RESPONSIBLE PARTY','RESPONSIBLE_PARTY_EMAIL','NODE_TYPE','DESCRIPTION'])
    node = Node.objects.get(name=name)
    writer.writerow([node.name, node.responsible_party, node.responsible_party_email, node.node_look, node.description])
    return response
    
def import_csv(request):
    if request.method == 'GET': 
        nodes = Node.objects.all().order_by('name')    
        return render_to_response('import_csv.html',{'nodes':nodes})
    
    if request.method == 'POST': 
        nodes = Node.objects.all().order_by('name')
        lines = []
        for line in request.FILES['import_file'].readlines():
            lines.append(line)
        return render_to_response('import_csv.html',{'nodes':nodes,'files':lines})
        