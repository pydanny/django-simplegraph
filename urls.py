from django.conf.urls.defaults import *


urlpatterns = patterns('',
           
    # all the handy displays
    url(r'^$', 'simplegraph.views.index', name="index"), 
    url(r'^dot/all$', 'simplegraph.views.dot_all', name="dot_all"),                            # show dot on everything
    url(r'^dot/node/([A-Za-z\d\s\.\-]{1,30})$', 'simplegraph.views.dot_node', name="dot_node"), # show dot on just one node
    url(r'^node/([A-Za-z\d\s\.\-]{1,30})$', 'simplegraph.views.node_detail', name="node_detail"),         # node details    
    url(r'^list_nodes/$', 'simplegraph.views.list_nodes', name="list_nodes"),      
    url(r'^show_em_all$', 'simplegraph.views.show_em_all',  name="show_em_all"),         # big pretty picture    
    url(r'^graph_all.([a-z]{3})$', 'simplegraph.views.graph_all',name="graph_all"),                    # simplegraph_all nodes   
    url(r'^graph/([A-Za-z\d\s\.\-]{1,30}).([a-z]{3})$', 'simplegraph.views.graph_detail', name="graph_detail"), 
    url(r'^random_image$', 'simplegraph.views.random_image', name="random_image"),
    
    # modification features
    url(r'^edit/node/([A-Za-z\d\s\.\-]{1,30})$', 'simplegraph.views.edit_node', name="edit_node"),
    url(r'^edit/node/edges/([A-Za-z\d\s\.\-]{1,30})$', 'simplegraph.views.edit_node_edges', name="edit_node_edges"),    
    url(r'^add/node$', 'simplegraph.views.add_node', name="add_node"),
    url(r'^add/edge$', 'simplegraph.views.add_edge', name="add_edge"),    
    
)


