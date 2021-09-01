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
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.models import User, auth
from django.contrib import messages
# import pydot
# import re
# from . import main

from .forms import FileForm, ModelRepresentationForm, AnnotationForm

class IndexView(generic.ListView):
    # Make a list of models in the database sorted alphabetically
    context_object_name = 'model_list'

    # Load template from template folder
    template_name = 'webapp/index.html'

    def get_queryset(self):
        return modelrepresentation.objects.order_by('name')

###### detail view functions
# Gets all elements that are associated with the current detailViews model primary key
def getElements(context, modelPrimaryKey):
    # create empty QuerySets
    attributeList = attribute.objects.none()
    operationList = operation.objects.none()
    parameterList = parameter.objects.none()
    relationList = relation.objects.none()
    annotationList= annotation.objects.none()

    # get list of components which have the current model as foreign key
    context['component_list'] = component.objects.filter(modelid=modelPrimaryKey)
    
    # get list of attr/oper/rela that have any of the components in this
    #   model as foreign key. 
    # The union ("|") operator combines two querysets.
    # We first check if the QuerySet is not empty.
    if context['component_list']:
        for c in context['component_list']:
            # print(c)
            attributeList = attributeList | attribute.objects.filter(ownerid=c)
            operationList = operationList | operation.objects.filter(ownerid=c)
            relationList = relationList | relation.objects.filter(source=c)
            annotationList = annotationList | annotation.objects.filter(ownerid=c)

    # add to context
    context['attribute_list'] = attributeList
    context['operation_list'] = operationList
    context['relation_list'] = relationList
    context['annotation_list'] = annotationList

    # get the list of parameters which have any of the operations in this 
    #   model as foreign key. We first make sure the QuerySet is not empty.
    if context['operation_list']:
        for o in context['operation_list']:
            parameterList = parameterList | parameter.objects.filter(ownerid=o.id)
    
    # add to context
    context['parameter_list'] = parameterList

# Creates the graph
def createGraph():
    # shape = record means we can add the attribute box / operations box beneath the name in the graph
    graph = Digraph('graph', node_attr={'shape': 'record', 'height': '.01'})

    return graph

# Function to create a string of the operations with their parameters
#   in the format: method(type1 param1, type2 param2, ...): type3 param3, type4 param4, ... 
def formatOperationString(context, operations):
    # Create empty string
    operationString = ""

    for o in operations:
        operationString = operationString + o.name
        # find all related parameters and format them into the string of the operation
        parameters = findAllRelated(context['parameter_list'], lambda x: x.ownerid == o)

        count = 0
        for p in parameters:
                
            if p.direction == "in":
                # For multiple parameters that go into the operation 
                # first parameter in -> add "(", else add ", "
                if count == 0:
                    operationString = operationString + "("
                else:
                    operationString = operationString + ", "

                # add type if available
                if p.type != "" or None:
                    operationString = operationString + p.name + " : " + p.type
                else:
                    operationString = operationString + p.name
                count = 1
            operationString = operationString + ")"

        # For out parameters, multiple parameters is also allowed
        count = 0
        for p in parameters:
            if p.direction == "out":
                # first parameter out -> add ":", else add ", "
                if count == 0:
                    operationString = operationString + ": "
                else:
                    operationString = operationString + ", "

                # add type if available
                if p.type != "" or None:
                    operationString = operationString + p.type + " " + p.name
                else:
                    operationString = operationString + p.name
            # increment count
            count = 1

        # Create newline for next operation
        operationString = operationString + "\l"

    return operationString

# Adds components to the graph, this included associated operations + paramters, and attributes
def addComponentsToGraph(context, graph):
    # Add a node for each component
    for c in context['component_list']:
        # Find all attributes/operations that this object owns using a function defined in models.py
        attributes = findAllRelated(context['attribute_list'], lambda x: x.ownerid == c)
        operations = findAllRelated(context['operation_list'], lambda x: x.ownerid == c)

        # Create an empty string
        attributeString = ""
        
        # For each attribute/operation that this component owns, add information to the string (+ newline)
        for a in attributes:
            # Add type if available
            if a.type != "":
                attributeString = attributeString + a.type + " " + a.name + "\l"
            else:
                attributeString = attributeString + a.name + "\l"
                
        # seperate function for formatting the operations string with parameters
        operationString = formatOperationString(context, operations)

        # replace <,> by \<,\> to prevent bad label error in the nohtml() call
        attributeString = attributeString.replace("<", "\<")
        attributeString = attributeString.replace(">", "\>")
        operationString = operationString.replace("<", "\<")
        operationString = operationString.replace(">", "\>")

        # Create the node with its attributes and operations in seperate sections
        if attributeString == "" and operationString == "":
            graph.node(c.name, nohtml(c.name), style="filled", fillcolor="lightgrey", color="black", fontname="Helvetica", fontsize="11")
        elif operationString == "":
            graph.node(c.name, nohtml('{' + c.type + ": " + c.name + '}|' + attributeString), style="filled", fillcolor="lightgrey", color="black", fontname="Helvetica", fontsize="11")
        elif attributeString == "":
            graph.node(c.name, nohtml('{' + c.type + ": " + c.name + '}|' + operationString), style="filled", fillcolor="lightgrey", color="black", fontname="Helvetica", fontsize="11")
        else:
            graph.node(c.name, nohtml('{' + c.type + ": " + c.name + '}|' + attributeString + '|' + operationString), style="filled", fillcolor="lightgrey", color="black", fontname="Helvetica", fontsize="11")

    return graph

# Adds relations to the graph
def addRelationsToGraph(context, graph):
    # Draw edges for each relation
    # Depending on the type of the relation the name of the specific relation is saved in either the type or the name
    # If the name is empty, it is saved in the type
    for r in context['relation_list']:
        if (r.name == None or r.name == ""):
            if (r.type == "association"):
                graph.edge(r.source.name, r.target.name, label=r.type, fontsize="9", fontcolor = "grey", arrowhead="none")
            else:
                graph.edge(r.source.name, r.target.name, label=r.type, fontsize="9", fontcolor = "grey")
        else:
            # NOT SURE HOW THESE ARROWSHEADS SHOULD BE IMPLEMENTED
            # if (r.type == "association"):
                # graph.edge(r.source.name, r.target.name, label=r.name, fontsize="9", fontcolor = "grey", arrowhead="none")
            # else:
            graph.edge(r.source.name, r.target.name, label=r.name, fontsize="9", fontcolor = "grey")

    return graph

# Adds annotations to the graph
def addAnnotationsToGraph(context, graph):
    # To keep track which components have an annotation allready and which don't
    # Important because there is no other way to know which button to create in 
    #   the template.
    #   -> update/delete or create annotation buttons
    annotatedComponents = []

    # Draw edges for each annotation
    for a in context['annotation_list']:
        # print(repr(a.content))
        # safe a list of component ids who allready have an annotation, used in template for update/delete button instead of create button
        annotatedComponents.append(a.ownerid.id)

        # Some function to insert a newline every 64 characters, does not work as nice as I would like it to
        # a.content = re.sub("(.{64})", "\\1\n", a.content, 0, re.DOTALL)

        # make the content string be left alligned in the annotation
        content = a.content.replace("\n", "\l")
        content += "\l"
        
        # Create node and edge for annotation
        graph.node(str(a.id), content, shape="note", style="filled", fillcolor="khaki1", color="khaki4", fontcolor="khaki4", fontname="Helvetica", fontsize="11")
        graph.edge(str(a.id), a.ownerid.name, style="dotted", arrowhead = "none", color="grey")
        
    # add list of annotated component ids to context
    context['annotated_components'] = annotatedComponents

    # test annotation
    # graph.node("testnode", "This is a test annotation without any relations\l\l\l\l\l\l\l\l\l\l\l\l\lend of test annotation", 
    #             pos="0,0" ,shape="note", style="filled", fillcolor="cadetblue1", color="cyan4", fontcolor="cyan4", fontname="Helvetica", fontsize="11")

    return graph

# Renders the graph to a SVG file in webapp/static/webapp/images/graph.svg
def renderGraph(graph):
    # Print the graph source dot code if desired
    # print(graph.source)
    # Ranks the components from left to right
    graph.graph_attr['rankdir'] = 'LR'
    # Render the svg file to display in the detail view
    graph.render('graph', directory='webapp/static/webapp/images', format='svg')

# Detailed view of a model, includes graph image, description, list of elements. 
# Users can edit description/annotations in this view aswell
class DetailView(generic.DetailView):
    model = modelrepresentation;
    template_name = 'webapp/detail.html'

    # All graph logic done here
    def get_context_data(self, *args, **kwargs):
        # get primary key of the detailview
        modelPrimaryKey = self.kwargs['pk']
        
        # Get context so we can add more data to it
        context = super(DetailView, self).get_context_data(*args, **kwargs)
        
        # Get all elements in the current model, put them into context to display in the template
        getElements(context, modelPrimaryKey)

        # Create the graph image
        graph = createGraph()

        # Add components to the graph
        graph = addComponentsToGraph(context, graph)

        # Add edges(relations) to the graph
        graph = addRelationsToGraph(context, graph)

        # Check which components have annotations, and add them to the graph
        graph = addAnnotationsToGraph(context, graph)

        # render the graph to a SVG file
        renderGraph(graph)

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

class UpdateDescView(generic.UpdateView):
    template_name = 'updatedesc.html'
    form_class = ModelRepresentationForm
    queryset = modelrepresentation.objects.all()

    def get_success_url(self):
        return reverse_lazy('webapp:detail', kwargs={'pk' : self.object.pk}) 

class CreateAnnoView(generic.CreateView):
    template_name = 'createanno.html'
    form_class = AnnotationForm
    queryset = annotation.objects.all()
    # context['owner'] = component.objects.get(id=self.kwargs.get('pk'))

    # Save owner in kwargs to display on the page
    def get_context_data(self, **kwargs):
        self.ownerid = get_object_or_404(component, id=self.kwargs['pk'])
        kwargs['owner'] = self.ownerid
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        # Create form with a foreign key requires setting of the foreign key with this code
        annotation = form.save(commit=False)
        annotation.ownerid = component.objects.get(id=self.kwargs.get('pk'))
        return super(CreateAnnoView, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('webapp:detail', kwargs={'pk' : self.object.ownerid.modelid.pk})

class UpdateAnnoView(generic.UpdateView):
    template_name = 'updateanno.html'
    form_class = AnnotationForm
    queryset = annotation.objects.all()

    def get_success_url(self):
        return reverse_lazy('webapp:detail', kwargs={'pk' : self.object.ownerid.modelid.pk})

class FileListView(generic.ListView):
    model = modelfile
    template_name = 'file_list.html'
    context_object_name = 'file_list'

def delete_file(request, pk):
    if request.method == 'POST':
        file = modelfile.objects.get(id=pk)
        file.delete()
    return redirect('webapp:file_list')

def delete_anno(request, pk):
    if request.method == 'POST':

        anno = annotation.objects.get(id=pk)
        redirectModelId = anno.ownerid.modelid.id
        anno.delete()
    return redirect('webapp:detail',  pk=redirectModelId)

# Here are the functions for the views for creating accounts, logging in, and logging out

def register(request):
    # When submitted
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        # Confirm password is different
        if password1 != password2:     
            messages.info(request, 'Passwords don\'t match')           
            return redirect('webapp:register')
            
        # Username taken
        elif User.objects.filter(username=username).exists():    
            messages.info(request, 'Username already taken')           
            return redirect('webapp:register')

        # Email taken
        elif User.objects.filter(email=email).exists():
            messages.info(request, 'Email already taken')           
            return redirect('webapp:register')

        # Save new user
        else:
            user = User.objects.create_user(username=username, password=password1, 
                                email=email, first_name=first_name, last_name=last_name)
            return redirect('webapp:login')

    # Register page
    else:
        return render(request, 'register.html')

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        print("username: " + username + ", password: " + password)

        user = authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('webapp:index')
        else:
            messages.info(request, "Invalid credentials")
            return redirect('webapp:login')
    else:
        return render(request, 'login.html')

def logout(request):
    auth.logout(request)
    return redirect('webapp:index')