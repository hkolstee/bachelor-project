from django.db.models.query import QuerySet
from django.http.response import HttpResponse
from django.template import loader
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, Http404
from django.views import generic
from .models import *
from graphviz import Digraph, Graph
from django.core.files.storage import FileSystemStorage
# from . import main


class IndexView(generic.ListView):
    # Make a list of models in the database sorted alphabetically
    context_object_name = 'model_list'

    # initiateUmlFile("webapp/media/components.xmi")

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

        # initiateUmlFile("webapp/static/webapp/components.xmi")
        
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

        # Create the graph image
        dot = Digraph(comment='Model Representation')
        for c in context['component_list']:
            # dot.node(c.id, c.name + "\n" + c.type, shape='box', style='filled', color='lightgrey')
            dot.node(c.id, c.name, shape='box', style='filled', color='lightgrey')

        for r in context['relation_list']:
            if (r.name == None or r.name == ""):
                dot.edge(r.source.id, r.target.id, label=r.type)
            else:
                dot.edge(r.source.id, r.target.id, label=r.name)

        # print(dot.source)
        dot.graph_attr['rankdir'] = 'LR'
        dot.render('graph', directory='webapp/static/webapp/images', format='svg')

        # return context to display in the template
        return context

def upload(request):
    context = {}
    if (request.method == 'POST'):
        # get uploaded file
        uploaded_file = request.FILES['document']
        
        
        # save the uploaded file
        fs = FileSystemStorage()
        name = fs.save(uploaded_file.name, uploaded_file)
        context['url'] = fs.url(name)
    return render(request, 'upload.html', context)