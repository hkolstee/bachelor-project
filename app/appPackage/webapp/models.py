from django.db import models
from django.db.models.deletion import CASCADE
import xml.etree.ElementTree as ET

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


# Create your models here.
class modelrepresentation(models.Model):
    id = models.CharField(primary_key = True, max_length = 20)
    name = models.CharField(max_length = 45)

class component(models.Model):
    id = models.CharField(primary_key = True, max_length=20)
    name = models.CharField(max_length = 45)
    type = models.CharField(max_length = 45)
    modelid = models.ForeignKey(modelrepresentation, on_delete=models.CASCADE)

class attribute(models.Model):
    id = models.CharField(primary_key = True, max_length=20)
    name = models.CharField(max_length = 45)
    type = models.CharField(max_length = 45)
    datatype = models.CharField(max_length = 45, null=True, blank=True)
    visibilty = models.CharField(max_length = 45)
    ownerid = models.ForeignKey(component, on_delete=models.CASCADE)   

class operation(models.Model):
    id = models.CharField(primary_key = True, max_length=20)
    name = models.CharField(max_length = 45)
    type = models.CharField(max_length = 45)
    visiblity = models.CharField(max_length = 45)
    ownerid = models.ForeignKey(component, on_delete=models.CASCADE)

class parameter(models.Model):
    id = models.CharField(primary_key = True, max_length=20)
    name = models.CharField(max_length = 45, null = True, blank = True)
    type = models.CharField(max_length = 45)
    direction = models.CharField(max_length = 45)
    ownerid = models.ForeignKey(operation, on_delete=models.CASCADE)        

class relation(models.Model):
    id = models.CharField(primary_key = True, max_length=20)
    name = models.CharField(max_length = 45, null = True, blank = True)
    type = models.CharField(max_length = 45)
    source = models.ForeignKey(component, on_delete=models.CASCADE, related_name='source')
    target = models.ForeignKey(component, on_delete=models.CASCADE, related_name='target')

# METHODS For saving XMLfile

def findAttributes(root, componentId):
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

        
def findParameters(root, operationId):
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
    

def findRelation(root, componentId):
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
    

def findOwnedMembers(root, componentId):
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


def findOperations(root, componentId):
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

        findParameters(root, operationId)


def findComponents(root, modelId):
    for packagedElement in root.findall(".//*[@{http://schema.omg.org/spec/XMI/2.1}type='uml:Class']"):
        
        componentId = packagedElement.get('{http://schema.omg.org/spec/XMI/2.1}id')    
        componentName = packagedElement.get('name')
        componentType = packagedElement.get('{http://schema.omg.org/spec/XMI/2.1}type')
        
        # add to database
        c = component(componentId, componentName, componentType, modelId)
        # c.save()
        components.append(c)

        # find associated attributes/operations/relations
        findAttributes(root, componentId)
        findOperations(root, componentId)
        findRelation(root, componentId)
        findOwnedMembers(root, componentId)

def findModel(root):
    for model in root.findall(".//packagedElement/[@{http://schema.omg.org/spec/XMI/2.1}type='uml:Model']"):
        modelId = model.get('{http://schema.omg.org/spec/XMI/2.1}id')
        modelName = model.get('name')

        # add to database
        m = modelrepresentation(modelId, modelName)
        # m.save()
        modelrepresentations.append(m)

        # find associated components
        findComponents(root, modelId)

# add the objects to the db in the correct order to avoid any foreign key constraint fails
def saveToDatabase():
    for m in modelrepresentations:
        m.save()
        
    for c in components:
        c.save()

    for a in attributes:
        a.save()
    
    for o in operations:
        o.save()
    
    for p in parameters:
        p.save()
    
    for r in relations:
        r.save()

    # clear arrays
    modelrepresentations.clear()
    components.clear()
    attributes.clear()
    operations.clear()
    parameters.clear()
    relations.clear()

def initiateUmlFile(filename):
    tree = ET.parse(filename)
    root = tree.getroot()

    findModel(root)
    saveToDatabase()

    
    