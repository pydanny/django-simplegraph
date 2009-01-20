from django import forms
from simplegraph.models import Node, Edge, NodeLook, EdgeType

class NodeForm(forms.ModelForm):
    
    def clean(self):
        return self.cleaned_data    
    
    class Meta:
        model = Node
        
class BaseEdgeForm(forms.ModelForm):

    class Meta:
        model = Edge
        
class EdgeForm(BaseEdgeForm):
    
    id = forms.IntegerField(widget=forms.HiddenInput())
    
    
class ParentForm(EdgeForm):
    
    child = forms.IntegerField(widget=forms.HiddenInput())
      
    
class ChildForm(EdgeForm):

    parent = forms.IntegerField(widget=forms.HiddenInput())    
    
