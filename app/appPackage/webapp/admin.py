from webapp.models import *
from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(modelrepresentation)
admin.site.register(component)
admin.site.register(attribute)
admin.site.register(operation)
admin.site.register(parameter)
admin.site.register(relation)
