# bachelor-project

# Introduction
This is the bachelor project of Hugo Kolstee for the Rijksuniversiteit Groningen.

The web application offers functionality to import XML-type files generated from PlantUML and StarUML class-diagram models. 
These XML files are parsed using the Python ElementTree XML API.
These models are then visualized in a general representation. 
This general representation reduces the supported Architectural Language models to a graph of components with relations.
Descriptions to models can be added, as well as annotations to specific components. 
The annotationsare added to the graph similarly to components, but with an easy to differentiate appearance.

The models are stored in a MySQL database and devided in components, relations, attributes, operations, and parameters.
This datamodel is chosen to be universally mappable to from other architectural language diagrams.

The graph is visualized using GraphViz.

# Structure of the code
The application is made using the Django framework, and also follows this structure.
Django requires a main application with the main settings, then different parts of the web application are added using
  a module like structure.
for example:

    bachelor project-
                    |-app-
                         |-appPackage-
                                     |-application
                                     |-webapp

Here appPackage is the main directory of the entire project.
The application directory contains the project along with its settings.
The webapp directory contains everything else for the application.

To elaborate:

    webapp-
          |-media-\
          |-templates-\
          |-migrations-\
          |-models.py
          |-views.py
          |-urls.py

The templates directory, models python file, and views python file are standard and required for every module in a django project.

In the models.py file, the classes with objects that are to be added to the database are specified. Here should also be the functions are related to using logic with these objects. In our application, the parsing of the
XML file is done to create the objects that are then saved to the database.

In the views.py file, it is specified what should be displayed on the different web pages. This can be functions that specify what should be in the context of this web page, or classed that can be called on different data to create a general view for this type of object. Here we differentiate between lists, which will be an indexView, and a simple object, which will be detailView. In our applications this is the list of all models and a model itself, respectively. Other web pages like the registration web page also require an own class.

The template directory contains HTML files which are templates to what a webpage should look like. Different views have different templates. The template gets all the information it can use through the context provided in the views.py file

In the media directory, the uploaded XML (or XMI, which is based on XML) files are stored. The migrations directory contains files that keep track of database migrations. The urls.py file contain how the urls should be specified for the different views. Then, in the template file for a view, the home page can for example be called by its specified url.

# How to add to your own django project
Quick start

Before we start, install the dependencies:

  > pip install -r requirements.txt

Then, add the webapp:

1. Add "webapp" to your INSTALLED_APPS setting like this::

    > INSTALLED_APPS = [
    >     ...
    >     'webapp',
    > ]

2. Include the webapp URLconf in your project urls.py like this::

    > path('webapp/', include('webapp.urls', namespace='webapp')),

3. To install the package, use pip:

    > python -m pip install --user gen_representation-0.1.tar.gz

With luck, your Django project should now work correctly again. Run the server again to confirm this.

4. Run ''**python manage.py migrate**'' in the appPackage directory to create the webapp models.

5. Visit **http://127.0.0.1:8000/webapp/** to use the application.

To uninstall the package, use pip:

    > python -m pip uninstall django-polls
