from django import forms
from simplegraph.models import Node, Edge, NodeLook, EdgeType

class NodeForm(forms.ModelForm):
    
    class Meta:
        model = Node