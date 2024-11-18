"""
program: main.py

project: ectb_xml

purpose: Main routine for the project.
         Read data from an XML file and construct a glossary of tagname meanings,
         within the context of Emory Cardiac Toolbox (ECTb) software.

         Alternative formats
         -------------------
         1. WSV: Whitespace-Separated Values (see: WhitespaceSV.com)
         2. JSON
         3. OML (like JSON, with whitespace instead of commas, and quotes used only
            for values that contain spaces)
         4. TBL (like SML with heirarchical rows; 1 value=level, 2 values = attribute & value)

author: Russell Folks

history:
-------
11-18-2024  creation
"""
from pathlib import Path
import xml.etree.ElementTree as ET

def get_tag_values(xmlroot):
    record = {}

    record['ptname'] = xmlroot.find('PatientName').text
    record['age'] = int(xmlroot.find('PatientAge').text)
    record['tid'] = float(xmlroot.find('TIDindex').text)
    record['stress_ef'] = int(xmlroot.find('StressLVEjectionFraction').text)
    record['rest_ef'] = int(xmlroot.find('RestLVEjectionFraction').text)

    return record    


# Read the XML file
# =================
# method 1:
# --------
mypath = Path('data')

filepath = mypath / 'CroDa_no_arrays.xml'
# print(f'mypath: {mypath}, {type(mypath)}')
# print(f'filepath: {filepath}, {type(filepath)}')

tree = ET.parse(filepath)
xmlroot = tree.getroot()
# rec = get_tag_values(xmlroot)
# print(f'...root: {xmlroot}')
# print(f'values found:\n\t{rec}')
# print()

ectb_tags = [elem.tag for elem in xmlroot.iter()]

# get tag subsets
sev_scores = [tag for tag in ectb_tags if tag.endswith('SevScore')]
extent_scores = [tag for tag in ectb_tags if tag.endswith('ExtentTotal')]

# print(f'extent tags: {extent_scores}')
# print(f'sev tags: {sev_scores}')


# parse tag name based on 'sections' as determined by letter case
s1 = 'TotScore'
s1.isalpha()
# s1[3].isupper()

parts = []
for n, c in enumerate(sev_scores[0]):
    p = ''
    if c.isupper():
        if len(p) == 0:
            parts.append(p)
            print(f'parts: {parts}')
        else:
            p.append(c)
    else:
        p.append(c)
    
    


# method 2:
# --------
# import fnmatch
# mypath2 = Path('data')
# for file in mypath2.iterdir():
#     if fnmatch.fnmatch(file, '*.xml'):
#         print(f'found: {file}')
#     tree = ET.parse(file)
#     xmlroot = tree.getroot()
#     # print(f'...root: {xmlroot}')
#     rec = get_results(xmlroot)
#     print(f'...for root: {xmlroot}, values found:\n{rec}')
#     print()


# method 3:
# --------
# import os
# import fnmatch
# mypath = Path('data')
# mypath3 = os.listdir('data')
# for file in mypath3:
#     if fnmatch.fnmatch(file, '*.xml'):
#         print(f'found: {file}')
#         with open(os.path.join(mypath, file), 'r') as f:
#             tree = ET.parse(f)
#             xmlroot = tree.getroot()
#             # print(f'...root: {xmlroot}')
#             rec = get_results(xmlroot)
#             print(f'...for root: {xmlroot}, values found:\n{rec}')
#             print()


# extract XML elements for the output file
# (you would do this for .csv output)
# 1. the column headers
# klist = [str(k) for k in rec.keys()]
# separator = ','
# line3_h = separator.join(klist)
# print(f'output row: {line3_h}')

# 2. example: row values for row 3
# vlist = [str(k) for k in rec.values()]
# line3_v = separator.join(vlist)
# print(f'output row: {line3_v}')

