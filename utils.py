CLEANUP_TARGETS = ('.',' ','-')

def cleanup(text):
    for target in CLEANUP_TARGETS:
        text = text.replace(target,'')
    return text
    
cleanup    
    
def node_to_dot(node):
    dot = ''
    dot += '%s' % cleanup(node.name)
    dot += ' [label="%s" '% node.name
    if node.nodeLook:
        dot += ' style=filled color=%s shape=%s' % (node.nodeLook.color, node.nodeLook.shape)
    dot += '];\n'    
    return dot
    
def make_all_dot():
    edges = []
    dot = 'simplegraph {\n'
    for application in Application.objects.select_related():
        # gets apps
        dot += application_dot(application)
        for parent in application.parent.iterator():
            edges.append((cleanup(parent.parents.name),cleanup(parent.children.name)))

        for child in application.child.iterator():
            edges.append((cleanup(child.parents.name),cleanup(child.children.name)))            

    # remove duplicates        
    edges = list(set(edges))
    for edge in edges:
        dot += '%s -- %s [arrowhead=vee];' % (edge[0], edge[1])
    dot += '}'
    return dot
    
def make_detail_dot(name=None):
    edges = []
    other_nodes = []
    dot = 'simplegraph {\n'
    application = Application.objects.select_related().get(name=name)
    # gets apps
    dot += application_dot(application)
    for parent in application.parent.iterator():
        edges.append((cleanup(parent.parents.name),cleanup(parent.children.name)))
        other_nodes.append(parent.children)

    for child in application.child.iterator():
        edges.append((cleanup(child.parents.name),cleanup(child.children.name)))            
        other_nodes.append(child.parents)        

    # remove duplicates        
    edges = list(set(edges))
    
    for node in other_nodes:
        dot += application_dot(node)
    
    for edge in edges:
        dot += '%s -- %s [arrowhead=vee];' % (edge[0], edge[1])
    dot += '}'
    return dot    
