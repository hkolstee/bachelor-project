from django.db.models.query import QuerySet
from django.http.response import HttpResponse
from django.template import loader
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, Http404
from django.views import generic
from .models import *
from graphviz import Digraph, Graph
# from . import main

# Create your views here.
# def index(request):
#     # Make a list of models in the database sorted alphabetically
#     model_list = modelrepresentation.objects.order_by('name')
    
#     # Create an output format (here: list seperated with newlines (<br>))
#     output = 'Model name - Model ID<br>'
#     output = output + '<br>'.join([m.name + ' - ' + m.id for m in model_list])
    
#     # Load template from template folder
#     template = loader.get_template('webapp/index.html')

#     # Create context for render call
#     context = {
#         'model_list': model_list, 
#         }
    
#     return HttpResponse(template.render(context, request))

# def detail(request, model_id):
#     # there is also a get_list_or_404 function
#     model = get_object_or_404(modelrepresentation, pk = model_id)
#     return HttpResponse("You're are on model:[%s, %s] page." % (model.name, model_id))

# class DetailView(generic.DetailView):
#     model = modelrepresentation;
#     template_name = 'webapp/detail.html'


class IndexView(generic.ListView):
    # Make a list of models in the database sorted alphabetically
    context_object_name = 'model_list'

    # initiateUmlFile("test2.xmi")
    # initiateUmlFile("mapping.xmi")

    # Load template from template folder
    template_name = 'webapp/index.html'

    def get_queryset(self):
        return modelrepresentation.objects.order_by('name')


class DetailView(generic.DetailView):
    model = modelrepresentation;
    template_name = 'webapp/detail.html'


    def get_context_data(self, *args, **kwargs):
        # get primary key of the detailview
        pk = self.kwargs['pk']

        initiateUmlFile("webapp/static/webapp/test2.xmi")
        
        context = super(DetailView, self).get_context_data(*args, **kwargs)
        
        # create empty QuerySets
        attributeList = attribute.objects.none()
        operationList = operation.objects.none()
        parameterList = parameter.objects.none()
        relationList = relation.objects.none()

        # get list of components which have the current model as foreign key
        context['component_list'] = component.objects.filter(modelid=pk)
        
        # get list of attr/oper/rela that have any of the components in this
        #   model as foreign key. 
        # The union ("|") operator combines two querysets.
        # We first check if the QuerySet is not empty.
        if context['component_list']:
            for c in context['component_list']:
                # print(c)
                attributeList = attributeList | attribute.objects.filter(ownerid=c.id)
                operationList = operationList | operation.objects.filter(ownerid=c.id)
                relationList = relationList | relation.objects.filter(source=c.id)

        # add to context
        context['attribute_list'] = attributeList
        context['operation_list'] = operationList
        context['relation_list'] = relationList

        # get the list of parameters which have any of the operations in this 
        #   model as foreign key. We first make sure the QuerySet is not empty.
        if context['operation_list']:
            for o in context['operation_list']:
                parameterList = parameterList | parameter.objects.filter(ownerid=o.id)
        
        # add to context
        context['parameter_list'] = parameterList

        dot = Digraph(comment='Model Representation')
        for c in context['component_list']:
            dot.node(c.id, c.name + "\n" + c.type, shape='box', style='filled', color='lightgrey')

        for r in context['relation_list']:
            if (r.type == "none"):
                dot.edge(r.source.id, r.target.id, label=r.name)
            else:
                dot.edge(r.source.id, r.target.id, label=r.type)

        print(dot.source)
        dot.graph_attr['rankdir'] = 'LR'
        dot.render('graph', directory='webapp/static/webapp/images', format='png')

        # return context to display in the template
        return context