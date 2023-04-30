import panel as pn
import pandas as pd
import numpy as np
import analyze_report
import io

pn.extension('tabulator')

# initial app creation
vanilla = pn.template.VanillaTemplate(title='Enrollment Permissions Dashboard', header_background='#F28C28', logo='new_RIT_logo1_w.png')

# logo (str): URI of logo to add to the header (if local file, logo is base64 encoded as URI).

# site (str): Name of the site. Will be shown in the header. Default is ‘’, i.e. not shown.

# site_url (str): Url of the site and logo. Default is “/”.
page = pn.Column(sizing_mode='stretch_width')

# getting perms db data
perms_db = pd.read_excel('PermissionsDB.xlsx') # how do we grab this from web?

# initial helper creation
filters = {
    'Title': {'type': 'input', 'func': 'like', 'placeholder': 'Enter title'},
    'Subtitle': {'type': 'input', 'func': 'like', 'placeholder': 'Enter subtitle'},
    'Roles Assigned': {'type': 'input', 'func': 'like', 'placeholder': 'Enter title'},
    'Permissions Explictly Granted': {'type': 'input', 'func': 'like', 'placeholder': 'Enter explicitly granted'},
    'Inherited Perms': {'type': 'input', 'func': 'like', 'placeholder': 'Enter inherited'},
    'Permissions': {'type': 'input', 'func': 'like', 'placeholder': 'Enter permissions'},
}

# initial widget creation
file_input = pn.widgets.FileInput()
filter_table = pn.widgets.Tabulator(
    perms_db, pagination='remote', layout='fit_columns', page_size=15, sizing_mode='stretch_width', show_index=False, disabled=True, theme='materialize',
    header_filters=filters
)

user_report_filters = {
    'Cleaned Roles': {'type': 'input', 'func': 'like', 'placeholder': 'Enter role'},
    'Correct Roles': {'type': 'input', 'func': 'like', 'placeholder': 'Enter role'},
    'Missing Roles': {'type': 'input', 'func': 'like', 'placeholder': 'Enter role'},
    'Excess Roles': {'type': 'input', 'func': 'like', 'placeholder': 'Enter role'},
    'fullTitle': {'type': 'input', 'func': 'like', 'placeholder': 'Enter Title'},
    'Department': {'type': 'input', 'func': 'like', 'placeholder': 'Enter Department'},
    'Title': {'type': 'input', 'func': 'like', 'placeholder': 'Enter Title'},
    'Updated': {'type': 'input', 'func': 'like', 'placeholder': 'Enter Date'},
    'Username': {'type': 'input', 'func': 'like', 'placeholder': 'Enter Username'},
    'Roles': {'type': 'input', 'func': 'like', 'placeholder': 'Enter Roles'},
}

user_report_table = pn.widgets.Tabulator(pagination='remote', layout='fit_columns', page_size=15, sizing_mode='stretch_width', show_index=False, disabled=True, theme='materialize',
    header_filters=user_report_filters
)


    
# pn.depends functions
@pn.depends(file_input=file_input)
def file_upload(file_input):
    print('entered func')
    if file_input is not None:
        df = pd.read_excel(io.BytesIO(file_input))
        report = analyze_report.preprocess(df)
        data = report.astype(str)
        user_report_table.value = data


# content boxing
permissions_db_content = [
    pn.Row('Permissions Database'),
    pn.Row(filter_table)
]

file_upload_content = [
    pn.Row('Upload User Report'),
    pn.Row(file_input),
    pn.Row(file_upload),
    pn.Row(user_report_table)
]

# linkage and theme building
link1 = pn.widgets.Button(name='Permissions Database')
link2 = pn.widgets.Button(name='Analyze User Report')

vanilla.sidebar.append(link1)
vanilla.sidebar.append(link2)
vanilla.main.append(page)

# content controllers
def load_content1(event):
    vanilla.main[0].objects = permissions_db_content

def load_content2(event):
    vanilla.main[0].objects = file_upload_content
    
link1.on_click(load_content1)
link2.on_click(load_content2)

vanilla.show()
