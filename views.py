from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from simplegraph.models import Node, Edge, COLOR_CHOICES, SHAPE_CHOICES
from simplegraph import graphviz
from simplegraph.graphviz import get_node, get_node_and_edges, get_nodes_and_edges
import random
import csv
from simplegraph.forms import NodeForm, EdgeForm, ParentForm, ChildForm, BaseEdgeForm
from datetime import datetime

############# Basics ############

IMAGE_TYPES = {
    'svg':dict(format='svg',mimetype="image/svg+xml"),
    'gif':dict(format='gif',mimetype="image/gif"),
    'vml':dict(format='vml',mimetype="image/vml"),    
    }

############# Views ###############


def index(request):
    colors = [x[0] for x in COLOR_CHOICES]
    shapes = [x[0] for x in SHAPE_CHOICES]    
    return render_to_response('index.html',{'colors':colors,'shapes':shapes})

def list_nodes(request):
    nodes = Node.objects.all().order_by('name')
    return render_to_response('list_nodes.html',{'nodes':nodes})
    
def dot_all(request):
    return render_to_response(nodes_and_edges_to_dot)
        
def dot_node(request,name):
    graph = get_node_and_edges(name)
    return render_to_response('dot.html',{'dot_export':graph.to_string()})
            
def node_detail(request,name):      
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
    graph.set_label('Random Image')
    image = graphviz.create_simplegraph(graph.to_string(),build_type=build_type)      
    return HttpResponse(image,mimetype="image/gif")    
    
def show_em_all(request):
    graph = get_nodes_and_edges()   
    image = graphviz.create_simplegraph(graph.to_string(),
        format='svg',
        build_type='dot')  
    ugly = image.index("Pages: 1 -->")  
    image = image[ugly+12:-1]
    from django.utils.safestring import mark_safe
    image = mark_safe(image)
    
    # emdtest
    return render_to_response('show_em_all.html',{'image':image})    
    
def csv_all(request):
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=export.csv'
    writer = csv.writer(response)
    writer.writerow(['NODE_ID','NODE_NAME','RESPONSIBLE PARTY','RESPONSIBLE_PARTY_EMAIL','NODE_TYPE','DESCRIPTION'])
    for node in Node.objects.all().order_by('name'):
        writer.writerow([node.pk,node.name, node.responsible_party, node.responsible_party_email, node.node_type, node.description])
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
    writer.writerow([node.pk,node.name, node.responsible_party, node.responsible_party_email, node.node_type, node.description])
    return response
    
def import_csv(request):  
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
 
            
        return render_to_response('import_csv.html',{'report':report})
        
def edit_node(request,name):     
    node = get_object_or_404(Node, name=name)             
    node_form = NodeForm(instance=node)            
    message = ''
    if request.method == 'POST':
        node_form = NodeForm(request.POST,instance=node)                
        if node_form.is_valid():
            node_form.save()
            message = '%s updated' % node.name            
            try:
                request.user.message_set(
                    message = message
                )
                return render_to_response('node_form.html',
                    {'nodes':stock_nodes,'node_form':node_form},
                    context_instance=RequestContext(request))
            except:
                pass
        else:
            message = 'Validation error'
    return render_to_response('node_form.html',{
                                'node_form':node_form,
                                'action':'Edit',
                                'node':node,
                                'message':message})
                                                                  
    
def add_node(request):
    message = ''
    node_form = NodeForm()    
    if request.method == 'POST':
        node_form = NodeForm(request.POST)
        if node_form.is_valid():
            node_form.save()
            name = request.POST['name']
            message = '%s added' % name
            return HttpResponseRedirect('/node/' + name)
        else:
            message = 'Validation error'
            
    return render_to_response('node_form.html',{
                    'node_form':node_form,
                    'action':'Add',
                    'message':message})    
                    
def edit_node_edges(request,name):
    node = get_object_or_404(Node, name=name)      
    problem_edge = None
    message = ''    
    if request.method == 'POST':
        edge = get_object_or_404(Edge, pk=request.POST['id'])      
        edge_form = EdgeForm(request.POST,instance=edge)
        if edge_form.is_valid():
            edge_form.save()        
            message = '%s updated' % (edge)
    parent_forms = []
    child_forms = []    
    for parent in Edge.objects.select_related().filter(child__name=name):
        parent_forms.append(ParentForm(instance=parent))
    for child in Edge.objects.select_related().filter(parent__name=name):
        child_forms.append(ChildForm(instance=child))
    return render_to_response('edges_form.html',{
                                'message':message,
                                'action':'Edit Edges',
                                'node':node,
                                'parent_forms':parent_forms,
                                'child_forms':child_forms})  

def add_edge(request):
    edge_form = BaseEdgeForm()
    message = ''    
    if request.method == 'POST':
        edge_form = BaseEdgeForm(request.POST)
        if edge_form.is_valid():
            edge_form.save()
            message = 'Edge added'
    return render_to_response('edge_form.html',{
            'edge_form':edge_form,
            'message':message
        }
    )
    
