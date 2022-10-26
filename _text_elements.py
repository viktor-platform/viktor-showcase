""" This file contains all Text elements that are used in the app, in order to keep the `app.py` file clean. """

from viktor.parametrization import Text

introduction_text1 = Text("""
## Welcome to the VIKTOR showcase app!

You are currently in the editor of an object. The core functionality of an editor is to:

- provide input fields a user can alter, which we call the **parametrization**. The parametrization is always located 
  on the left side of the editor.
- show results to a user by means of a visualization, which we call a **view**. The views are always shown on the right
  side of the editor.

An example input text field is shown below:
""")

introduction_text2 = Text("""
A simple parametrization can be created using fields only. However, if the parametrization becomes large, a layered 
structure can be achieved by making use of [Tab(s)](https://docs.viktor.ai/docs/create-apps/layout-and-styling/tabs-and-sections),
[Page(s)](https://docs.viktor.ai/docs/create-apps/layout-and-styling/pages), or 
[Step(s)](https://docs.viktor.ai/docs/create-apps/layout-and-styling/steps) (used in this app). 

There are many different 
[fields](https://docs.viktor.ai/docs/create-apps/user-input/) and 
[views](https://docs.viktor.ai/docs/create-apps/results-and-visualizations/) available for the design of your editor.
Both can have an (i) symbol next to it. Hover over it to get additional info!

## Click 'Next step' in the bottom right corner to continue
""")

research_text1 = Text("""
Play around with the value of 'Measurement' and 'Location', and see the results in the 'Map' view.
""")

research_text2 = Text("""
The fields above can be created with the following Python code:

```python
from viktor.parametrization import ViktorParametrization, IntegerField, GeoPointField

class Parametrization(ViktorParametrization):
    measurement = IntegerField("Measurement", min=0, max=100, description="...")
    location = GeoPointField("Location", description="...")
```

A view is defined on the [controller](https://docs.viktor.ai/docs/create-apps/fundamentals/create-editor#the-controller-class)
by decorating the view method as shown below. The values of the input fields that are defined in the parametrization are 
provided in the `params` argument:

```python
from viktor import ViktorController
from viktor.views import MapView, MapResult, MapPoint

class Controller(ViktorController)
    ...

    @MapView("Map", duration_guess=1, description="...")
    def map_view(self, params, **kwargs):
        marker = MapPoint.from_geo_point(params.research.location)
        features = [marker]     # points, polylines, polygons
        labels = ...            # text annotations
        legend = ...            # description of the colors 
        return MapResult(features, labels, legend)
```
""")

design_text1 = Text("""
Many field settings can be dynamic. For example, it is possible to 
[set the visibility](https://docs.viktor.ai/docs/create-apps/user-input/hide-field#depending-on-other-fields) of a field based 
on the value of another field. Change the shape of the geometry to see how this works:
""")

design_text2 = Text("""
```python
from viktor.parametrization import ViktorParametrization, OptionField, NumberField, IsEqual, Lookup

class Parametrization(ViktorParametrization):
    shape = OptionField("Shape", options=['Circle', 'Rectangle', 'Triangle'], variant='radio-inline')
    diameter = NumberField("Diameter", visible=IsEqual(Lookup('shape'), 'Circle')
    width = NumberField("Width", visible=IsEqual(Lookup('shape'), 'Rectangle')
    length = NumberField("Length", visible=IsEqual(Lookup('shape'), 'Rectangle')
    side = NumberField("Side", visible=IsEqual(Lookup('shape'), 'Triangle')
```
""")

calculate_text1 = Text("""
Dynamically sized input can be realized using a
[Table or DynamicArray](https://docs.viktor.ai/docs/create-apps/user-input/tables-and-arrays).
""")

calculate_text2 = Text("""
Besides plain Python code, calculations within a VIKTOR app can also be performed by making use of **services** like
the [spreadsheet calculator](https://docs.viktor.ai/docs/create-apps/documents-and-spreadsheets/spreadsheet-calculator). 
Notice that there are 2 view tabs on the right hand side of the editor: 
- "Results (Python)": performs a calculation using plain Python code 
- "Results (SpreadsheetCalculation)": performs a calculation using the spreadsheet calculator

This way, you are not limited to a single view per step! In the Python code, simply add a reference to both view
methods by means of a sequence (list):

```python
calculate = Step("Calculate", views=['calculate_python', 'calculate_spreadsheet'])
```

The second view has been set to update only when the user clicks the 'Update' button. This is especially useful if
calculating the results takes a long time, for example when using a service or
[integration](https://docs.viktor.ai/docs/create-apps/software-integrations/) with
third-party software packages (note: integrations require a [worker](https://docs.viktor.ai/docs/worker), which is
available to premium users only).
""")

report_section_text = Text("""
A second level of layering of the parametrization can be achieved by using Section(s), which are collapsible as shown
here. In code, this looks like:

```python
from viktor.parametrization import ViktorParametrization, Section, DateField

class Parametrization(ViktorParametrization):
    download = Section("Download")
    download.date = DateField("Date")
    ...
```
""")

report_download_text1 = Text("""
There are various [action buttons](https://docs.viktor.ai/docs/create-apps/user-input/action-buttons) available to let 
the user perform some action. For example, a [DownloadButton](https://docs.viktor.ai/docs/create-apps/managing-files/downloading-files) 
lets the user download a file, such as a report, to his/her local hard drive.
""")

report_download_text2 = Text("""
In the code we have to define the method that should be called when the button is pressed on the field:

```python
DownloadButton("Download Report (.docx)", method="download_report")
```

And add the "download_report" method on the controller:

```python
from viktor import ViktorController
from viktor.result import DownloadResult

class Controller(ViktorController):
    ...

    def download_report(self, params **kwargs):
        report = ...
        return DownloadResult(report, "report.docx")
```    
""")

report_upload_text1 = Text("""
A [FileField](https://docs.viktor.ai/docs/create-apps/managing-files/uploading-files#upload-using-filefield) enables 
the user to upload a file directly to the app. Click on the upload cloud to upload "report_template.docx", located 
in the source code of this app.
""")

report_upload_text2 = Text("""
Notice that the `file_types` argument on the `FileField` has been set to only allow for the selection of .docx files:

```python
FileField("Custom Template (Optional)", file_types=['.docx'])
```

**Challenge**: copy \"report_template.docx\" from the app's source code, modify it to your liking,
and upload it using this file-field, to generate and download a report that differs from the default one.

""")

evaluate_text = Text("""
## We hope you enjoyed this showcase app!

Have a look at this app's source code by opening it in your favorite
[IDE](https://docs.viktor.ai/docs/create-apps/development-tools-and-tips/ide). The code includes
\\\n plenty of examples and comments to help you understand, and is a good starting point for
\\\n creating your own app.

If you run into any questions that are not covered by the [documentation](https://docs.viktor.ai/docs/welcome),
feel free to ask your
\\\n questions on our [Community](https://community.viktor.ai/) page.

### Happy coding!
""")
