from django.db.models.query import QuerySet
from django.http.response import HttpResponse
from django.template import loader
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, Http404
from django.views import generic
from django.views.generic.list import ListView
from .models import *
from graphviz import Digraph, Graph, nohtml
from django.urls import reverse_lazy
from django.core.files.storage import FileSystemStorage
import pydot
# from . import main

from .forms import FileForm, ModelRepresentationForm

class IndexView(generic.ListView):
    # Make a list of models in the database sorted alphabetically
    context_object_name = 'model_list'

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
        # shape = record means we can add the attribute box / operations box beneath the name in the graph
        dot = Digraph('dot', node_attr={'shape': 'record', 'height': '.01'})
        dot.attr(style="filled", fillcolor=".7 .3 1.0", color=".5 .15 1.0")

        # Add a node for each component
        for c in context['component_list']:
            # Find all attributes/operations that this object owns using a function defined in models.py
            attributes = findAllRelated(context['attribute_list'], lambda x: x.ownerid == c)
            operations = findAllRelated(context['operation_list'], lambda x: x.ownerid == c)
            # Create an empty string
            attributeString = ""
            operationString = ""
            # For each attribute/operation that this component owns, add information to the string (+ newline)
            for a in attributes:
                attributeString = attributeString + a.name + "\l"
            for o in operations:
                operationString = operationString + o.name + "\l"

            # replace <,> by \<,\> to prevent bad label error in the nohtml() call
            attributeString = attributeString.replace("<", "\<")
            attributeString = attributeString.replace(">", "\>")
            operationString = operationString.replace("<", "\<")
            operationString = operationString.replace(">", "\>")

            # Create the node with its attributes and operations in seperate sections
            if attributeString == "" and operationString == "":
                dot.node(c.name, nohtml(c.name), style="filled", fillcolor="lightgrey", color="black", fontname="Helvetica", fontsize="11")
            elif operationString == "":
                dot.node(c.name, nohtml('{' + c.name + '}|' + attributeString), style="filled", fillcolor="lightgrey", color="black", fontname="Helvetica", fontsize="11")
            elif attributeString == "":
                dot.node(c.name, nohtml('{' + c.name + '}|' + operationString), style="filled", fillcolor="lightgrey", color="black", fontname="Helvetica", fontsize="11")
            else:
                dot.node(c.name, nohtml('{' + c.name + '}|' + attributeString + '|' + operationString), style="filled", fillcolor="lightgrey", color="black", fontname="Helvetica", fontsize="11")
                             

        # Draw edges for each relation
        # Depending on the type of the relation the name of the specific relation is saved in either the type or the name
        # If the name is empty, it is saved in the type
        for r in context['relation_list']:
            if (r.name == None or r.name == ""):
                dot.edge(r.source.name, r.target.name, label=r.type, fontsize="9", fontcolor = "grey")
            else:
                dot.edge(r.source.name, r.target.name, label=r.name, fontsize="9", fontcolor = "grey")

        # Print the dot source code if desired
        # print(dot.source)
        # Ranks the components from left to right
        dot.graph_attr['rankdir'] = 'LR'
        # Render the svg file to display in the detail view
        dot.render('graph', directory='webapp/static/webapp/images', format='svg')

        # return context to display in the template
        return context

class UploadView(generic.CreateView):
    model = modelfile
    form_class = FileForm
    success_url = reverse_lazy('webapp:file_list')
    template_name = 'upload.html'

    # parse the file and save to database when upload is success
    def form_valid(self, form):
        file = form.save()
        # parse file and save mapped representation to database
        initiateUmlFile(file)

        return super(UploadView,self).form_valid(form)

class UpdateView(generic.UpdateView):
    template_name = 'update.html'
    form_class = ModelRepresentationForm
    queryset = modelrepresentation.objects.all()

    def get_success_url(self):
        return reverse_lazy('webapp:detail', kwargs={'pk' : self.object.pk})
    


class FileListView(generic.ListView):
    model = modelfile
    template_name = 'file_list.html'
    context_object_name = 'file_list'

def delete_file(request, pk):
    if request.method == 'POST':
        file = modelfile.objects.get(id=pk)
        file.delete()
    return redirect('webapp:file_list')

