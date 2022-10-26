"""
This file is the entry point for your application and is used to:

    - Define all entity-types that are part of the app, and
    - Create 1 or more initial entities (of above type(s)), which are generated upon starting the app

For more information about this file, see: https://docs.viktor.ai/docs/create-apps/fundamentals/#apppy
"""
# Import required classes and functions
from pathlib import Path

from viktor import File, Color, ViktorController, UserException, InitialEntity
from viktor.external.word import WordFileTag, WordFileImage, render_word_file
from viktor.external.spreadsheet import SpreadsheetCalculation, SpreadsheetCalculationInput
from viktor.geometry import CircularExtrusion, SquareBeam, Extrusion, Material, Line, Point
from viktor.result import DownloadResult
from viktor.parametrization import ViktorParametrization, Step, GeoPointField, NumberField, DownloadButton, DateField, \
    IntegerField, OptionField, Table, TextField, TextAreaField, FileField, DynamicArray, OptionListElement, Section, \
    BooleanField, IsEqual, Lookup, MultiSelectField, LineBreak
from viktor.utils import convert_word_to_pdf
from viktor.views import MapView, MapPoint, MapLegend, MapLabel, MapResult, PDFView, PDFResult, GeometryView, \
    GeometryResult, DataGroup, DataItem, DataStatus, PNGView, PNGResult, PlotlyAndDataView, PlotlyAndDataResult, Label

from _text_elements import *


# Define some constants to be used in multiple parts of the code
NORM_A_MAX = 500
NORM_B_MAX = 750
NORM_C_MAX = 1000


# Define some stand-alone functions
def get_color(value: int) -> Color:
    """ Generate a color based on a single integer value (0 <= value <= 100)

    See "tests/test_get_color.py" for an example test written for this method.
    """
    if not 0 <= value <= 100:  # check for invalid value
        raise ValueError(f"value ({value}) must be between 0 - 100")

    return Color(255 - int(value / 100 * 255), 20, int(value / 100 * 255))


def calculate_mass_from_spreadsheet(volume: float, density: float) -> float:
    """ Calculates the mass from the volume and density by means of a spreadsheet (calculate_mass.xlsx).

    For more information, see: https://docs.viktor.ai/docs/create-apps/documents-and-spreadsheets/spreadsheet-calculator
    """
    inputs = [
        SpreadsheetCalculationInput('volume', volume),  # 'volume' equals the name in viktor-input-sheet
        SpreadsheetCalculationInput('density', density),  # 'density' equals the name in viktor-input-sheet
    ]

    sheet_path = Path(__file__).parent / 'calculate_mass.xlsx'
    sheet = SpreadsheetCalculation.from_path(sheet_path, inputs=inputs)
    spreadsheet_result = sheet.evaluate(include_filled_file=False)  # calculation is triggered here
    return spreadsheet_result.get_value('mass')  # 'mass' equals the name in viktor-output-sheet


class Parametrization(ViktorParametrization):
    """ A Parametrization defines the fields and views visible in an entity type's editor.

    For more information on the Parametrization-class, see:
    https://docs.viktor.ai/docs/create-apps/fundamentals/create-editor#defining-a-parametrization

    Available fields are:

        - Text
        - TextField
        - TextAreaField
        - NumberField
        - IntegerField
        - DateField
        - BooleanField
        - OutputField
        - HiddenField
        - LineBreak
        - OptionField
        - MultiSelectField
        - AutocompleteField
        - ActionButton
        - DownloadButton
        - OptimizationButton
        - SetParamsButton
        - Table
        - DynamicArray
        - EntityOptionField
        - ChildEntityOptionField
        - SiblingEntityOptionField
        - EntityMultiSelectField
        - ChildEntityMultiSelectField
        - SiblingEntityMultiSelectField
        - GeoPointField
        - GeoPolylineField
        - GeoPolygonField
        - FileField
        - MultiFileField

    Structuring of fields can be achieved by means of Tab(s), Page(s) or Step(s) to create top level, and Section(s) to
    create a second level of layering.

    For tree-type apps (or if the Parametrization-class becomes large), it might be cleaner to move the class to a 
    separate file ("parametrization.py") next to "controller.py" and import the class in the usual way:

    from .parametrization import Parametrization

    For more information on a tree-type app's recommended folder structure, see:
    https://docs.viktor.ai/docs/create-apps/tree-apps/#recommended-structure
    """
    intro = Step("Introduction", views='png_view')
    intro.text1 = introduction_text1
    intro.text = TextField("TextField", description="This is a TextField!")
    intro.text2 = introduction_text2

    research = Step("Research", views='map_view')
    research.text1 = research_text1
    research.measurement = IntegerField(
        "Measurement", min=0, max=100,
        description="When removing the value with backspace, the value returned in the params is None."
    )
    research.location = GeoPointField(
        "Location",
        description="Remove the pre-selected point by clicking the bin icon. Define a new point by clicking the "
                    "+marker icon and selecting a location on the Map view."
    )
    research.text2 = research_text2

    design = Step("Design", views='geometry_view')
    design.text1 = design_text1
    design.shape = OptionField(
        "Shape", options=['Circle', 'Rectangle', 'Triangle'], default='Circle', flex=40, variant='radio-inline'
    )
    design.lb1 = LineBreak()
    design.height = NumberField(
        "Height", suffix='m', min=1, max=10, description="Remove the value to see a custom user-error raised."
    )
    design.diameter = NumberField("Diameter", suffix='m', min=0.1, visible=IsEqual(Lookup('design.shape'), 'Circle'))
    design.width = NumberField("Width", suffix='m', min=0.1, visible=IsEqual(Lookup('design.shape'), 'Rectangle'))
    design.length = NumberField("Length", suffix='m', min=0.1, visible=IsEqual(Lookup('design.shape'), 'Rectangle'))
    design.side = NumberField("Side", suffix='m', min=0.1, visible=IsEqual(Lookup('design.shape'), 'Triangle'))
    design.red = NumberField("Red", min=0, max=255, step=1, default=100, variant='slider', flex=100)
    design.green = NumberField("Green", min=0, max=255, step=1, default=100, variant='slider', flex=100)
    design.blue = NumberField("Blue", min=0, max=255, step=1, default=100, variant='slider', flex=100)
    design.text2 = design_text2

    calculate = Step("Calculate", views=['calculate_python', 'calculate_spreadsheet'])
    calculate.text1 = calculate_text1
    calculate.cases = DynamicArray(
        "Cases", min=1, row_label="Case", description="This array should have at least 1 row. Click on the bin icon to "
                                                      "remove a row, and see what happens if all rows are deleted."
    )
    calculate.cases.volume = NumberField("Volume", suffix='m³', min=0.1, max=1, step=0.1, default=0.3)
    calculate.cases.density = IntegerField("Density", suffix='kg/m³', min=0, max=3000, default=1000)
    calculate.cases.norm = OptionField(
        "Norm", default='A', options=[OptionListElement(value='A', label=f'A (max. {NORM_A_MAX} kg)'),
                                      OptionListElement(value='B', label=f'B (max. {NORM_B_MAX} kg)'),
                                      OptionListElement(value='C', label=f'C (max. {NORM_C_MAX} kg)')]
    )
    calculate.text2 = calculate_text2

    report = Step("Report", views='pdf_view')
    report.section = Section("This is a section (click to expand/collapse)")
    report.section.text = report_section_text

    report.download = Section("Download")
    report.download.text1 = report_download_text1
    report.download.date = DateField("Date", description="Type or select a date by clicking on the calendar icon.")
    report.download.authors = Table("Authors", description="Right-click on a cell in the table to add or remove a row.")
    report.download.authors.first_name = TextField("First Name")
    report.download.authors.last_name = TextField("Last Name")
    report.download.authors.organization = TextField("Organization")
    report.download.authors.email = TextField("Email")
    report.download.remarks = TextAreaField("Additional Remarks", default="No remarks.")
    report.download.button = DownloadButton("Download Report (.docx)", method="download_report")
    report.download.text2 = report_download_text2
    report.upload = Section("Upload")
    report.upload.text1 = report_upload_text1
    report.upload.template = FileField("Custom Template (Optional)", file_types=['.docx'], flex=50,
                                       description="Don't forget to select the file after uploading it.")
    report.upload.text2 = report_upload_text2

    evaluate = Step("Evaluate")
    evaluate.text = evaluate_text

    ########
    # Uncomment the lines below to add a step that includes a text-field (and has no views)
    ########
    # my_step = Step("My Step")
    # my_step.text = Text("From the moment you uncommented the 'Text' field, it became visible in the editor!")


# Creates an entity-type 'MyEntityType'
class MyEntityType(ViktorController):
    """
    For more information on the controller class, see:
    https://docs.viktor.ai/docs/create-apps/fundamentals/create-editor#the-controller-class

    Views are defined by means of "@***View" decorated methods on the controller.

    Available views are:

        - GeometryView (2D/3D)
        - DataView
        - SVGView
        - PNGView
        - JPGView
        - MapView
        - GeoJSONView
        - WebView
        - PlotlyView
        - PDFView
        - GeometryAndDataView
        - SVGAndDataView
        - PNGAndDataView
        - JPGAndDataView
        - MapAndDataView
        - GeoJSONAndDataView
        - WebAndDataView
        - PlotlyAndDataView

    For more information on views, see: https://docs.viktor.ai/docs/create-apps/results-and-visualizations/
    """
    label = 'My Entity Type'  # label of the entity type as seen by the user in the app's interface
    parametrization = Parametrization  # parametrization associated with the editor of the MyEntityType entity type

    @PNGView("View", duration_guess=1, description="This is a View!")
    def png_view(self, params, **kwargs):
        """ https://docs.viktor.ai/docs/create-apps/results-and-visualizations/images#pngview """
        png_path = Path(__file__).parent / 'viktor-logo.png'
        return PNGResult.from_path(png_path)

    @MapView("Map", duration_guess=1, description="Click on the map marker to see its description.")
    def map_view(self, params, **kwargs):
        """ https://docs.viktor.ai/docs/create-apps/results-and-visualizations/map#mapview """
        location = params.research.location  # type GeoPoint (or None if unfilled)
        features, labels = [], []
        if location:
            measurement = params.research.measurement  # type float (or None if unfilled)
            if measurement is not None:  # colored pin-add icon if measurement exists
                color = get_color(measurement)
                icon = "pin-add"

                label = MapLabel(location.lat, location.lon, f"{measurement}", scale=5, fixed_size=True)
                labels.append(label)
            else:  # black cross icon if no measurement
                color = Color.black()  # black map marker if no measurement
                icon = "cross"  # cross icon if no measurement

            description = f"Measurement: {measurement}"
            map_point = MapPoint.from_geo_point(location, description=description, color=color, icon=icon)
            features.append(map_point)

        legend_entries = [(get_color(i), f"{i}") for i in [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]]
        legend = MapLegend(legend_entries)

        return MapResult(features, labels, legend)

    @GeometryView("Geometry", duration_guess=1, description="Move around and zoom in and out using your mouse.")
    def geometry_view(self, params, **kwargs):
        """ https://docs.viktor.ai/docs/create-apps/results-and-visualizations/threed-model """
        design_params = params.design

        # Create material with the user-defined color
        red = design_params.red
        green = design_params.green
        blue = design_params.blue
        material = Material("my_material", color=Color(red, green, blue))

        height = design_params.height
        if height is None:  # raise an exception to the user if height is not filled in
            raise UserException("Please fill in a value for 'height'")

        shape = design_params.shape
        if shape == 'Circle':
            diameter = design_params.diameter
            if diameter is None:
                raise UserException("Please fill in a value for 'diameter'")
            extrusion_line = Line(Point(0, 0, -height / 2), Point(0, 0, height / 2))
            geometry = CircularExtrusion(diameter=diameter, line=extrusion_line, material=material)
        elif shape == 'Rectangle':
            width = design_params.width
            length = design_params.length
            if width is None:
                raise UserException("Please fill in a value for 'width'")
            if length is None:
                raise UserException("Please fill in a value for 'length'")
            geometry = SquareBeam(width, length, height, material=material)
        elif shape == 'Triangle':
            side = design_params.side
            if side is None:
                raise UserException("Please fill in a value for 'side'")
            profile = [Point(side / 2, 0), Point(-side / 2, 0), Point(0, side), Point(side / 2, 0)]
            extrusion_line = Line(Point(0, 0, -height / 2), Point(0, 0, height / 2))
            geometry = Extrusion(profile, extrusion_line, material=material)
        else:
            raise NotImplementedError  # should not occur

        labels = []
        # optionally, text annotation can be added
        # labels.append(Label(Point(0, 0, -height), *LABEL*, size_factor=2))

        return GeometryResult(geometry, labels=labels)

    @staticmethod
    def create_plotly_and_data_result(params, calculation_method: str):
        graph_data, data_items = [], []
        for i, case in enumerate(params.calculate.cases, 1):
            if case.norm == 'A':  # 'value' will be present in the params, while 'label' is shown in the interface!
                max_mass = NORM_A_MAX
            elif case.norm == 'B':
                max_mass = NORM_B_MAX
            elif case.norm == 'C':
                max_mass = NORM_C_MAX
            else:
                raise NotImplementedError  # should not occur

            if calculation_method == 'spreadsheet':
                # calculate the mass using a spreadsheet
                mass = calculate_mass_from_spreadsheet(case.volume, case.density)
            elif calculation_method == 'python_function':
                # calculate the mass using a simple Python function (very fast)
                mass = case.volume * case.density
            else:
                raise NotImplementedError  # should not occur

            unity_check = mass / max_mass * 100
            if unity_check > 100:
                status = DataStatus.ERROR
                color = "red"
            elif unity_check > 80:
                status = DataStatus.WARNING
                color = "orange"
            else:
                status = DataStatus.SUCCESS
                color = "green"

            graph_data.append((unity_check, color))

            item = DataItem(
                f"Case {i}", unity_check, suffix='%', number_of_decimals=0, status=status,
                subgroup=DataGroup(
                    DataItem("Volume", case.volume, suffix='m³'),
                    DataItem("Density", case.density, suffix='kg/m³'),
                    DataItem("Mass", mass, suffix='kg'),
                    DataItem("Norm", case.norm),
                    DataItem("Unity Check", unity_check, suffix='%', number_of_decimals=0, status=status)
                )
            )

            data_items.append(item)

        # Create the Plotly graph
        x = [f"Case {i}" for i in range(1, len(graph_data) + 1)]  # x = Case 1, Case 2, Case 3, ...
        if graph_data:
            y, color = zip(*graph_data)  # y = unity checks
        else:
            raise UserException("Add at least 1 case.")
        # For more information on how to create a Plotly visualization, see:
        # https://plotly.com/chart-studio-help/json-chart-schema/
        fig = {
            'data': [{'type': "bar", 'x': x, 'y': y, 'marker': {'color': color}}],
            'layout': {'title': {'text': "Unity Check [%]"}}
        }

        return PlotlyAndDataResult(fig, data=DataGroup(*data_items))

    @PlotlyAndDataView("Results (Python function)", duration_guess=1,
                       description="Most of the views can be combined with a dataview (e.g. PlotlyView + DataView = "
                                   "PlotlyAndDataView), to have a more compact overview of the results.")
    def calculate_python(self, params, **kwargs):
        """ Combined PlotlyView + DataView.

        More information on PlotlyView: https://docs.viktor.ai/docs/create-apps/results-and-visualizations/plots-charts-graphs#using-plotly
        More information on DataView: https://docs.viktor.ai/docs/create-apps/results-and-visualizations/data-and-tables
        """
        return self.create_plotly_and_data_result(params, calculation_method='python_function')

    @PlotlyAndDataView("Results (SpreadsheetCalculation)", duration_guess=4,  # adds 'Update' button if duration_guess > 3
                       description="Views that require more calculation time can be configured to be triggered "
                                   "manually using an 'Update' button, by setting `duration_guess` larger than 3. ")
    def calculate_spreadsheet(self, params, **kwargs):
        return self.create_plotly_and_data_result(params, calculation_method='spreadsheet')

    @staticmethod
    def create_report(params, entity_name: str) -> File:
        """ Create a report using a Word-file template (report_template.docx).

        For more information, see: https://docs.viktor.ai/docs/create-apps/documents-and-spreadsheets/word-file-templater
        """
        content = params.report.download

        # DateField returns a Python datetime object
        date = content.date.strftime("%Y-%m-%d") if content.date is not None else '-'

        components = [
            WordFileTag('title', entity_name),
            WordFileTag('date', date),
            WordFileTag('authors', content.authors),
            WordFileTag('remarks', content.remarks)
        ]

        with open(Path(__file__).parent / 'viktor-logo.png', 'rb') as image:
            components.append(WordFileImage(image, 'image', width=30))

        template = params.report.upload.template
        if template is not None:  # user has selected custom report template
            with template.file.open_binary() as r:
                report = render_word_file(r, components)
        else:  # user has not selected custom report template, use default template
            with open(Path(__file__).parent / 'report_template.docx', 'rb') as r:
                report = render_word_file(r, components)

        return report

    def download_report(self, params, entity_name: str, **kwargs):
        """ Enables the user to download a report.

        For more information on downloading files, see: https://docs.viktor.ai/docs/create-apps/managing-files/downloading-files
        """
        report = self.create_report(params, entity_name)
        return DownloadResult(report, "report.docx")

    @PDFView("PDF", duration_guess=10, update_label="Generate Report",
             description="The PDFView makes it possible to show a static or dynamically generated report directly in "
                         "your VIKTOR app.")
    def pdf_view(self, params, entity_name: str, **kwargs):
        """ https://docs.viktor.ai/docs/create-apps/results-and-visualizations/report """
        docx_report = self.create_report(params, entity_name)

        with docx_report.open_binary() as r:
            pdf_report = convert_word_to_pdf(r)

        return PDFResult(file=pdf_report)


# Create the initial entity of type 'MyEntityType' with the name "Showcase" as a starting point for the user.
initial_entities = [
    InitialEntity('MyEntityType', name='Showcase', params='my_entity.json')  # predefined entity properties from a .json file.
]
