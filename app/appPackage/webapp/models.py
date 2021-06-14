from os import name
from django.db import models
from django.db.models.deletion import CASCADE
import xml.etree.ElementTree as ET
from lxml import etree

from django.utils import tree

# Before saving objects to the database, we put them in an array
# Because of the structure of the XML files we cant directly add
#   To the database, because of foreign key constraint failure on
#   certain relations/components. 
modelrepresentations = []
components = []
attributes = []
operations = []
parameters = []
relations = []

# Namespaces used in XML files
namespaces = {
    'uml': 'http://schema.omg.org/spec/UML/2.0',
    'UML': 'href://org.omg/UML/1.3',
    'xmi': 'http://schema.omg.org/spec/XMI/2.1',
    }


# Create your models here.
class modelfile(models.Model):
    name = models.CharField(max_length = 100)
    file = models.FileField(upload_to='')
    # description = models.TextField(null=True, blank=True)
    
    def delete(self, *args, **kwargs):
        self.file.delete()
        super().delete(*args, **kwargs)

class modelrepresentation(models.Model):
    # Used as PK in database
    # id = models.AutoField(primary_key=True)
    # Used to find associated components
    modelid = models.CharField(max_length = 45)
    name = models.CharField(max_length = 100)
    file = models.OneToOneField(modelfile, on_delete=models.CASCADE)
    description = models.TextField(null=True, blank=True)

class component(models.Model):
    componentid = models.CharField(max_length=20)
    # id = models.CharField(max_length = 45)
    name = models.CharField(max_length = 100)
    type = models.CharField(max_length = 100)
    modelid = models.ForeignKey(modelrepresentation, on_delete=models.CASCADE)

class annotation(models.Model):
    # xposition = models.IntegerField()
    # yposition = models.IntegerField()
    content = models.TextField()
    ownerid = models.OneToOneField(component, on_delete=models.CASCADE)

class attribute(models.Model):
    attributeid = models.CharField(max_length=20)
    # id = models.CharField(max_length = 45)
    name = models.CharField(max_length = 100)
    type = models.CharField(max_length = 100)
    datatype = models.CharField(max_length = 45, null=True, blank=True)
    visibility = models.CharField(max_length = 100)
    ownerid = models.ForeignKey(component, on_delete=models.CASCADE)   

class operation(models.Model):
    operationid = models.CharField(max_length=20)
    # id = models.CharField(max_length = 45)
    name = models.CharField(max_length = 100)
    type = models.CharField(max_length = 100)
    visibility = models.CharField(max_length = 45)
    ownerid = models.ForeignKey(component, on_delete=models.CASCADE)

class parameter(models.Model):
    parameterid = models.CharField(max_length=20)
    # id = models.CharField(max_length = 45)
    name = models.CharField(max_length = 100, null = True, blank = True)
    type = models.CharField(max_length = 100)
    direction = models.CharField(max_length = 100)
    ownerid = models.ForeignKey(operation, on_delete=models.CASCADE)        

class relation(models.Model):
    relationid = models.CharField(max_length=20)
    # id = models.CharField(max_length = 45)
    name = models.CharField(max_length = 100, null = True, blank = True)
    type = models.CharField(max_length = 100)
    source = models.ForeignKey(component, on_delete=models.CASCADE, related_name='source')
    target = models.ForeignKey(component, on_delete=models.CASCADE, related_name='target')

# METHODS For saving XMLfile
# Methods to parse and save from starUML 3 export
def findAttributesStar(root, componentId):
    for ownedAttribute in root.findall(".//*[@{http://schema.omg.org/spec/XMI/2.1}id='" + componentId + "']/ownedAttribute"):
        
        attrId = ownedAttribute.get('{http://schema.omg.org/spec/XMI/2.1}id')
        attrName = ownedAttribute.get('name')
        attrType = ownedAttribute.get('{http://schema.omg.org/spec/XMI/2.1}type')
        attrDataType = ownedAttribute.get('type')
        attrVisibility = ownedAttribute.get('visibility')

        # 
        if (attrDataType != None):
            item = root.find(".//*[@{http://schema.omg.org/spec/XMI/2.1}id='" + attrDataType + "']")
            attrDataType = item.get('name') 


        # Some attribuets are defined with a custom DataType, and stored elsewhere in the XML file with id = type
        a = attribute(attrId, attrName, attrType, attrDataType, attrVisibility, componentId)
        # a.save()
        attributes.append(a)
      
def findParametersStar(root, operationId):
    for ownedParameter in root.findall(".//*[@{http://schema.omg.org/spec/XMI/2.1}id='" + operationId + "']/ownedParameter"):
            
        parameterId = ownedParameter.get('{http://schema.omg.org/spec/XMI/2.1}id')
        parameterName = ownedParameter.get('name')
        parameterType = ownedParameter.get('{http://schema.omg.org/spec/XMI/2.1}type')
        parameterDirection = ownedParameter.get('direction')

        # Some parameters are defined with a custom DataType, and stored elsewhere in the XML file with id = type
        if (parameterName == None):
            customType = ownedParameter.get('type')
            item = root.find(".//*[@{http://schema.omg.org/spec/XMI/2.1}id='" + customType + "']")
            parameterName = item.get('name') 

        # add to database
        p = parameter(parameterId, parameterName, parameterType, parameterDirection, operationId)
        parameters.append(p)
    
def findRelationStar(root, componentId):
    for ownedRelation in root.findall(".//*[@{http://schema.omg.org/spec/XMI/2.1}id='" + componentId + "']/generalization"):
    
        relationId = ownedRelation.get('{http://schema.omg.org/spec/XMI/2.1}id')
        relationName = ownedRelation.get('name')
        relationType = ownedRelation.get('{http://schema.omg.org/spec/XMI/2.1}type')
        relationSource = ownedRelation.get('specific')
        relationTarget = ownedRelation.get('general')

        # add to database
        r = relation(relationId, relationName, relationType, relationSource, relationTarget)
        # r.save()
        relations.append(r)
    
def findOwnedMembersStar(root, componentId):
    for ownedMember in root.findall(".//*[@{http://schema.omg.org/spec/XMI/2.1}id='" + componentId + "']/ownedMember"):
            
        relationId = ownedMember.get('{http://schema.omg.org/spec/XMI/2.1}id')
        relationName = ownedMember.get('name')

        #end 1 aggregation = none           ->source or target
        #end 2 aggregation = none           ->target or source

        #end 1 aggregation = composite      ->source
        #end 2 aggregation = none           ->target

        #end 1 aggregation = none           ->target
        #end 2 aggregation = composite      ->source
        i = 0
        for ownedEnd in root.findall(".//*[@{http://schema.omg.org/spec/XMI/2.1}id='" + relationId + "']/ownedEnd"):
            currentEndType = ownedEnd.get('aggregation')
            if (currentEndType == "none"):
                if (i == 0):
                    relationTarget = ownedEnd.get('type')
                else:
                    relationSource = ownedEnd.get('type')
                    relationType = currentEndType
                i = i + 1
            else: 
                relationSource = ownedEnd.get('type')
                relationType = ownedEnd.get('aggregation')

        # add to database
        r = relation(relationId, relationName, relationType, relationSource, relationTarget)
        # r.save()
        relations.append(r)

def findOperationsStar(root, componentId):
    for ownedOperation in root.findall(".//*[@{http://schema.omg.org/spec/XMI/2.1}id='" + componentId + "']/ownedOperation"):
        
        operationId = ownedOperation.get('{http://schema.omg.org/spec/XMI/2.1}id')
        operationName = ownedOperation.get('name')
        operationType = ownedOperation.get('{http://schema.omg.org/spec/XMI/2.1}type')
        operationVisibility = ownedOperation.get('visibility')
        # print(operationVisibility)

        # TODO: add to database
        # self.operations.append({operationId, operationName, operationType, operationVisibility})
        # print("Operation: [id: %s] [name: %s] [type: %s] [visibility: %s]" % 
        #     (operationId, operationName, operationType, operationVisibility))

        # add to database
        o = operation(operationId, operationName, operationType, operationVisibility, componentId)
        # o.save()
        operations.append(o)

        findParametersStar(root, operationId)

def findComponentsStar(root, modelId):
    for ownedComponent in root.findall(".//*[@{http://schema.omg.org/spec/XMI/2.1}type='uml:Class']"):
        
        componentId = ownedComponent.get('{http://schema.omg.org/spec/XMI/2.1}id')    
        componentName = ownedComponent.get('name')
        componentType = ownedComponent.get('{http://schema.omg.org/spec/XMI/2.1}type')
        
        # add to database
        c = component(componentId, componentName, componentType, modelId)
        # c.save()
        components.append(c)

        # find associated attributes/operations/relations
        findAttributesStar(root, componentId)
        findOperationsStar(root, componentId)
        findRelationStar(root, componentId)
        findOwnedMembersStar(root, componentId)

def findModelStar(root):
    for model in root.findall(".//ownedComponent/[@{http://schema.omg.org/spec/XMI/2.1}type='uml:Model']"):
    # for model in root.findall('UML:Model')
        modelId = model.get('{http://schema.omg.org/spec/XMI/2.1}id')
        modelName = model.get('name')

        # add to database
        m = modelrepresentation(modelId, modelName)
        # m.save()
        modelrepresentations.append(m)

        # find associated components
        findComponentsStar(root, modelId)

# function to find foreign key based on found id in model
def findRelated(list, filter):
    for x in list:
        if filter(x):
            return x
    # print("no foreign key found\n")
    return False

def findAllRelated(list, filter):
    related = []
    for x in list:
        if filter(x):
            related.append(x)
    return related

def findOperation(componentRoot, component, modelId):
    for ownedOperation in componentRoot.findall(".//UML:Operation", namespaces):

        operationId = ownedOperation.get('xmi.id')
        operationName = ownedOperation.get('name')
        operationVisibility = ownedOperation.get('visibility')
        if not operationVisibility:
            operationVisibility = "N/A"

        o = operation(operationid = operationId, name = operationName, type = "N/A", 
                        visibility = operationVisibility, ownerid = component)
        
        operations.append(o)

def findAttribute(componentRoot, component, modelId):
    for ownedAttribute in componentRoot.findall(".//UML:Attribute", namespaces):

        attributeId = ownedAttribute.get('xmi.id')
        attributeName = ownedAttribute.get('name')
        attributeVisibility = ownedAttribute.get('visibility')
        if not attributeVisibility:
            attributeVisibility = "N/A"

        a = attribute(attributeid = attributeId, name = attributeName, type = "N/A", 
                        datatype = "N/A", visibility = attributeVisibility, ownerid= component)
        
        attributes.append(a)


# Methods to parse and save from PlantUML staruml-xmi export
def findRelation(root, modelId):
    # Generalizations
    for ownedRelation in root.findall(".//UML:Generalization/[@namespace='" + modelId + "']", namespaces):

        relationId = ownedRelation.get('xmi.id')
        relationName = ownedRelation.get('name')
        relationType = 'generalization'

        relationSource = findRelated(components, lambda x: x.componentid == ownedRelation.get('child'))
        relationTarget = findRelated(components, lambda x: x.componentid == ownedRelation.get('parent'))
        
        r = relation(relationid = relationId, name = relationName, type = relationType, source = relationSource, target = relationTarget)    
        relations.append(r)

    # Associations
    for ownedRelation in root.findall(".//UML:Association/[@namespace='" + modelId + "']", namespaces):
        
        relationId = ownedRelation.get('xmi.id')
        relationName = ownedRelation.get('name')
        relationType = "association"
        
        # Two ends of the relation
        count = 0
        for relationEnd in ownedRelation.findall(".//UML:AssociationEnd", namespaces):
            if (count == 0):
                if (relationName == "" or relationName == None):
                    relationName = relationEnd.get('aggregation')
                    relationType = relationName
                relationTarget = findRelated(components, lambda x: x.componentid == relationEnd.get('type'))
            else:
                relationSource = findRelated(components, lambda x: x.componentid == relationEnd.get('type'))
            count = 1
        
        # Some cases where the association has no label(name) or type
        if relationType == None:
            relationType = ""

        r = relation(relationid = relationId, name = relationName, type = relationType, source = relationSource, target = relationTarget)
        relations.append(r)

    


def findComponents(root, modelId, foreignKey):
    # for ownedComponent in root.findall(".//UML:Class/[@namespace='" + modelId + "']", namespaces):
    for ownedComponent in root.findall(".//UML:Class", namespaces):
        
        componentId = ownedComponent.get('xmi.id')    
        componentName = ownedComponent.get('name')
        componentType = 'class'

        c = component(componentid = componentId, name =  componentName, type = componentType, modelid = foreignKey)
        components.append(c)

        # find associated attributes/operations
        findAttribute(ownedComponent, c, modelId)
        findOperation(ownedComponent, c, modelId)


def findModel(root, modelfile):
    for model in root.findall(".//UML:Model", namespaces):

        modelId = model.get('xmi.id')
        modelName = model.get('name')

        m = modelrepresentation.objects.create(modelid=modelId, name=modelName, file=modelfile)
        modelrepresentations.append(m)

        # find associated components
        findComponents(model, modelId, m)
        # findComponents(root, modelId, m.id)
        findRelation(model, modelId)


# add the objects to the db in the correct order to avoid any foreign key constraint fails
def saveToDatabase():
    print("saving to database..\n")
    for m in modelrepresentations:
        print(m)
        m.save()
        
    for c in components:
        print(c)
        c.save()

    for a in attributes:
        print(a)
        a.save()
    
    for o in operations:
        print(o)
        o.save()
    
    for p in parameters:
        print(p)
        p.save()
    
    for r in relations:
        print(r)
        r.save()

    # clear arrays
    modelrepresentations.clear()
    components.clear()
    attributes.clear()
    operations.clear()
    parameters.clear()
    relations.clear()

def initiateUmlFile(modelfile):
    # tree = ET.parse(filename)
    # root = tree.getroot()

    root = etree.parse("webapp/media/" + modelfile.file.name)
    # root = etree.parse("webapp/media/" + modelfile.file.name)

    findModel(root, modelfile)
    # findModelStar(root)
    saveToDatabase()

    
    