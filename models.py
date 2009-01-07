from django.db import models

COLOR_CHOICES = (
    ('grey93', 'grey93'),
    ('lawngreen', 'lawngreen'),
    ('lightblue', 'lightblue'),
    ('yellow', 'yellow'),
    ('white', 'white'),    
)

SHAPE_CHOICES = (
    ('box','box'),
    ('circle','circle'),
    ('component','component'),     
    ('diamond','diamond'),
    ('folder','folder'),    
    ('hexagon','hexagon'),
    ('note','note'),    
    ('octagon','octagon'),
    ('plaintext','plaintext'),
    ('point','point'),
    ('tab','tab'),
)
        
class NodeLook(models.Model):
    name = models.CharField(max_length=30)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=40,choices=COLOR_CHOICES)
    shape = models.CharField(max_length=40,choices=SHAPE_CHOICES)    
    
    def __unicode__(self):
        return self.name


class Node(models.Model):
    name = models.CharField(max_length=30)     
    responsible_party = models.CharField(max_length=30,blank=True)
    responsible_party_email = models.EmailField(blank=True)  
    description = models.TextField(blank=True)      
    node_look = models.ForeignKey(NodeLook,blank=True,null=True)

    def __unicode__(self):
        return self.name
        
class EdgeType(models.Model):
    name = models.CharField(max_length=30)

    def __unicode__(self):
        return self.name    
        
class Edge(models.Model):
    parent = models.ForeignKey(Node,related_name='parent')
    child = models.ForeignKey(Node,related_name='child')
    edge_type = models.ForeignKey(EdgeType,blank=True,null=True)
    
    def __unicode__(self):
        if self.edge_type:
            return '%s -> %s (%s)' % (self.parent, self.child, self.edge_type)            
        return '%s -> %s' % (self.parent, self.child)
        
        