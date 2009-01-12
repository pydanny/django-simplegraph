from django.conf.urls.defaults import *


urlpatterns = patterns('',
           

    url(r'^$', 'simplegraph.views.index', name="index"), 
    url(r'^dot/all$', 'simplegraph.views.dot_all'),                            # show dot on everything
    url(r'^dot/node/([A-Za-z\d\s\.\-]{1,30})$', 'simplegraph.views.dot_node'), # show dot on just one node
    url(r'^node/([A-Za-z\d\s\.\-]{1,30})$', 'simplegraph.views.node_detail'),         # node details
    url(r'^show_em_all$', 'simplegraph.views.show_em_all'),         # big pretty picture    
    url(r'^graph_all.gif$', 'simplegraph.views.simplegraph_all'),                    # simplegraph_all nodes   
    url(r'^graph/([A-Za-z\d\s\.\-]{1,30}).gif$', 'simplegraph.views.simplegraph_detail'),                
    url(r'^random_image.gif$', 'simplegraph.views.random_image'),                    
)
