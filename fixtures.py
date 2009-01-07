from simplegraph.models import EdgeType, NodeLook

EDGE_TYPES = ('EMAIL','FTP','LDAP','REST','SOAP','XMLRPC')
#n,d,c,s
NODE_LOOKS = (
    dict(
        name = 'ColdFusion',
        color='lightblue',
        shape='box'
    ),
    dict(
        name = 'External Application',
        color='grey93',
        shape='circle'
    ),    
    dict(
        name = 'Java',
        color='yellow',
        shape='box'
    ),
    dict(
        name = 'Python',
        color='lawngreen',
        shape='box'
    ),    
)

def main():
    # Add edge types
    for item in EDGE_TYPES:
        et = EdgeType(name=item)
        et.save()
    
    # Add node looks
    for item in NODE_LOOKS:
        nl = NODE_LOOK(
            name=item['name'],
            color=item['color'],
            shape=item['shape']
            )
        

if __name__ == "__main__":
    main()