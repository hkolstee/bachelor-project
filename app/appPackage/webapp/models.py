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

    def __str__(self):
        return self.name

class modelrepresentation(models.Model):
    # Used as PK in database
    # id = models.AutoField(primary_key=True)
    # Used to find associated components
    modelid = models.CharField(max_length = 45)
    name = models.CharField(max_length = 45)
    file = models.OneToOneField(modelfile, on_delete=models.CASCADE)

class component(models.Model):
    componentid = models.CharField(max_length=20)
    # id = models.CharField(max_length = 45)
    name = models.CharField(max_length = 45)
    type = models.CharField(max_length = 45)
    modelid = models.ForeignKey(modelrepresentation, on_delete=models.CASCADE)

class attribute(models.Model):
    attributeid = models.CharField(max_length=20)
    # id = models.CharField(max_length = 45)
    name = models.CharField(max_length = 45)
    type = models.CharField(max_length = 45)
    datatype = models.CharField(max_length = 45, null=True, blank=True)
    visibilty = models.CharField(max_length = 45)
    ownerid = models.ForeignKey(component, on_delete=models.CASCADE)   

class operation(models.Model):
    operationid = models.CharField(max_length=20)
    # id = models.CharField(max_length = 45)
    name = models.CharField(max_length = 45)
    type = models.CharField(max_length = 45)
    visiblity = models.CharField(max_length = 45)
    ownerid = models.ForeignKey(component, on_delete=models.CASCADE)

class parameter(models.Model):
    parameterid = models.CharField(max_length=20)
    # id = models.CharField(max_length = 45)
    name = models.CharField(max_length = 45, null = True, blank = True)
    type = models.CharField(max_length = 45)
    direction = models.CharField(max_length = 45)
    ownerid = models.ForeignKey(operation, on_delete=models.CASCADE)        

class relation(models.Model):
    relationid = models.CharField(max_length=20)
    # id = models.CharField(max_length = 45)
    name = models.CharField(max_length = 45, null = True, blank = True)
    type = models.CharField(max_length = 45)
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
    for packagedElement in root.findall(".//*[@{http://schema.omg.org/spec/XMI/2.1}type='uml:Class']"):
        
        componentId = packagedElement.get('{http://schema.omg.org/spec/XMI/2.1}id')    
        componentName = packagedElement.get('name')
        componentType = packagedElement.get('{http://schema.omg.org/spec/XMI/2.1}type')
        
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
    for model in root.findall(".//packagedElement/[@{http://schema.omg.org/spec/XMI/2.1}type='uml:Model']"):
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
def find(list, filter):
    for x in list:
        if filter(x):
            return x
    print("no foreign key found\n")
    return False

# Methods to parse and save from PlantUML staruml-xmi export
def findRelation(root, modelId):
    # Generalizations
    for ownedRelation in root.findall(".//UML:Generalization/[@namespace='" + modelId + "']", namespaces):

        relationId = ownedRelation.get('xmi.id')
        relationName = ownedRelation.get('name')
        relationType = 'generalization'
        relationSource = find(components, lambda x: x.componentid == ownedRelation.get('child'))
        relationTarget = find(components, lambda x: x.componentid == ownedRelation.get('parent'))
        
        r = relation(relationid = relationId, name = relationName, type = relationType, source = relationSource, target = relationTarget)    
        relations.append(r)

    # Associations
    for ownedRelation in root.findall(".//UML:Association/[@namespace='" + modelId + "']", namespaces):
        
        relationId = ownedRelation.get('xmi.id')
        relationType = 'association'
        relationName = ownedRelation.get('name')
        
        # Two ends of the relation
        count = 0
        for relationEnd in ownedRelation.findall(".//UML:AssociationEnd", namespaces):
            if (count == 0):
                if (relationName == ""):
                    relationName = relationEnd.get('aggregation')
                relationTarget = find(components, lambda x: x.componentid == relationEnd.get('type'))
            else:
                relationSource = find(components, lambda x: x.componentid == relationEnd.get('type'))
            count = 1

        r = relation(relationid = relationId, name = relationName, type = relationType, source = relationSource, target = relationTarget)
        relations.append(r)


def findComponents(root, modelId, foreignKey):
    for packagedElement in root.findall(".//UML:Class/[@namespace='" + modelId + "']", namespaces):

        componentId = packagedElement.get('xmi.id')    
        componentName = packagedElement.get('name')
        componentType = 'class'
        
        c = component(componentid = componentId, name =  componentName, type = componentType, modelid = foreignKey)
        components.append(c)


def findModel(root, modelfile):
    for model in root.findall(".//UML:Model", namespaces):

        modelId = model.get('xmi.id')
        modelName = model.get('name')

        m = modelrepresentation.objects.create(modelid=modelId, name=modelName, file=modelfile)
        modelrepresentations.append(m)

        # find associated components
        findComponents(root, modelId, m)
        # findComponents(root, modelId, m.id)
        findRelation(root, modelId)


# add the objects to the db in the correct order to avoid any foreign key constraint fails
def saveToDatabase():
    print("saving to database..\n")
    # for m in modelrepresentations:
        # print(m)
        # m.save()
        
    for c in components:
        # print(c)
        c.save()

    for a in attributes:
        # print(a)
        a.save()
    
    for o in operations:
        # print(o)
        o.save()
    
    for p in parameters:
        # print(p)
        p.save()
    
    for r in relations:
        # print(r)
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
    modelrepresentations.clear()
    components.clear()
    attributes.clear()
    operations.clear()
    parameters.clear()
    relations.clear()


    root = etree.parse("webapp/media/" + modelfile.file.name)

    findModel(root, modelfile)
    # findModelStar(root)
    saveToDatabase()

    
    