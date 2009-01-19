from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from simplegraph.models import Node, Edge, COLOR_CHOICES, SHAPE_CHOICES
from simplegraph import graphviz
from simplegraph.graphviz import get_node, get_node_and_edges, get_nodes_and_edges
import random
import csv
from simplegraph.forms import NodeForm


############# Basics ############

IMAGE_TYPES = {
    'svg':dict(format='svg',mimetype="image/svg+xml"),
    'gif':dict(format='gif',mimetype="image/gif"),
    'vml':dict(format='vml',mimetype="image/vml"),    
    }

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
    
def graph_all(request,format,build_type='dot'):
    graph = get_nodes_and_edges()
    format = IMAGE_TYPES[format]['format']
    mimetype = IMAGE_TYPES[format]['mimetype']    
    image = graphviz.create_simplegraph(graph.to_string(),
        format=format,
        build_type=build_type)
    return HttpResponse(image,mimetype=mimetype)
    
def graph_detail(request,name,format,build_type='dot'):
    graph = get_node_and_edges(name)
    format = IMAGE_TYPES[format]['format']
    mimetype = IMAGE_TYPES[format]['mimetype']    
    image = graphviz.create_simplegraph(graph.to_string(),
        format = format,
    build_type=build_type)      
    return HttpResponse(image,mimetype=mimetype)
    
def random_image(request,build_type='dot'):
    node = random.choice(Node.objects.all())
    graph = get_node_and_edges(node.name)
    image = graphviz.create_simplegraph(graph.to_string(),build_type=build_type)      
    return HttpResponse(image,mimetype="image/gif")    
    
def show_em_all(request):
    nodes = Node.objects.all().order_by('name')
    # test
    graph = get_nodes_and_edges()   
    image = graphviz.create_simplegraph(graph.to_string(),
        format='svg',
        build_type='dot')  
    ugly = image.index("Pages: 1 -->")  
    image = image[ugly+12:-1]
    from django.utils.safestring import mark_safe
    image = mark_safe(image)
    
    # emdtest
    return render_to_response('show_em_all.html',{'nodes':nodes,'image':image})    
    
def csv_all(request):
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=export.csv'
    writer = csv.writer(response)
    writer.writerow(['NODE_ID','NODE_NAME','RESPONSIBLE PARTY','RESPONSIBLE_PARTY_EMAIL','NODE_TYPE','DESCRIPTION'])
    for node in Node.objects.all().order_by('name'):
        writer.writerow([node.pk,node.name, node.responsible_party, node.responsible_party_email, node.node_look, node.description])
    writer.writerow([])
    writer.writerow(['EDGE_ID','EDGE_PARENT','EDGE_CHILD','EDGE_TYPE'])
    for edge in Edge.objects.all():
        writer.writerow([edge.pk,edge.parent,edge.child,edge.edge_type])
    return response
    
def csv_node(request,name):
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=export.csv'
    writer = csv.writer(response)
    writer.writerow(['NODE_ID','NODE_NAME','RESPONSIBLE PARTY','RESPONSIBLE_PARTY_EMAIL','NODE_TYPE','DESCRIPTION'])
    node = Node.objects.get(name=name)
    writer.writerow([node.pk,node.name, node.responsible_party, node.responsible_party_email, node.node_look, node.description])
    return response
    
def import_csv(request):
    stock_nodes = Node.objects.all().order_by('name')    
    if request.method == 'GET': 
        
        return render_to_response('import_csv.html',{'nodes':stock_nodes})
    
    if request.method == 'POST': 
        report = []
        row_type = ''
        for i,row in enumerate(csv.reader(request.FILES['import_file'])):
            if (i == 0) and row[0] == 'NODE_ID':
                row_type = 'NODE'
                continue
            try:
                if (i > 0) and row[0] == 'EDGE_ID':
                    row_type = 'EDGE'
                    continue
            except:
                continue
 
            if row_type == 'NODE':
                nodes = Node.objects.filter(pk=row[0])
                if not nodes:
                    # add a node
                    pass
                elif len(nodes) == 1:
                    # edit a node
                    node = nodes[0]

                    node.name = row[1] #'NODE_NAME'
                    node.responsible_party = row[2]
                    node.responsible_party_email = row[2]
                    node.description = row[4]
                    node.save()
                    report.append(row[1] + ' updated.')
                else:
                    # report a problem
                    pass

                
            if row_type == 'EDGE':
                pass
 
            
        return render_to_response('import_csv.html',{'nodes':stock_nodes,'report':report})
        
def edit_node(request,name):
    stock_nodes = Node.objects.all().order_by('name') 
    node = get_object_or_404(Node, name=name)      
    if request.method == 'POST':
        node.save()                        
    node_form = NodeForm(instance=node)        
    return render_to_response('node_form.html',{'nodes':stock_nodes,'node_form':node_form})    