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
11-22-2024  Test algorithm to segment terms by case, using sev scores.
12-05-2024  Move alternate xml-reading methods to alternate_xml.txt.
12-07-2024  Add more tag lists: segments, summed scores, gated results,
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


def find_vessel(tag):
    found_lad = False
    found_lcx = False
    found_rca = False

    if tag.rfind("LAD") != -1: found_lad = True
    if tag.rfind("LCX") != -1: found_lad = True
    if tag.rfind("RCA") != -1: found_lad = True

    return (found_lad, found_lcx, found_rca)


def find_lv(tag):
    found_lv = False
    if tag.rfind("LV") != -1: found_lv = True

    return found_lv


def find_edes(tag):
    found_edes = False
    if tag.rfind("ED") != -1 or tag.rfind("ES") != -1: found_edes = True

    return found_edes


def match_part_to_def(parts, defs, prepend):
    print(f'    parts: {parts}')
    output = ''
    if len(defs) < len(parts):
        output += parts[0]
    for n, item in enumerate(parts):
        if item in defs.keys():
            output += ' '
            output += defs[item]

    return output




# module variables
# ================
# definitions
severity_defs = {'Tot': 'Total',
                 'Sev': 'defect severity',
                 'Score': 'in standard deviation units'}
defect_defs = {'Extent': 'defect extent,',
               'Total': 'in pixels',
               'Reversed': 'defect reversed,'}
defect_defs.keys()
summed_defs = {}
segmental_defs = {}
gated_defs = {}

# Read the XML file
# =================
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

# define tag subsets
sev_scores = [tag for tag in ectb_tags if tag.endswith('SevScore')]
# extent_scores = [tag for tag in ectb_tags if tag.endswith('ExtentTotal')]
defect_values = [tag for tag in ectb_tags if
                 tag.find('Extent') != -1 or
                 tag.find('Reversed') != -1]
segment_scores = []
summed_scores = []

# from gated, find items: LV, ES, ED
# ?? need to find PFR...
study1_gated_tags = [tag for tag in ectb_tags if tag.startswith('Study1')]
study2_gated_tags = [tag for tag in ectb_tags if tag.startswith('Study2')]


# print(f'defect tags: {defect_values}')
print(f'sev tags: {sev_scores}')

# parse tag name based on 'sections' as determined by letter case
s1 = 'TotScore'
s1.isalpha()

for tagnum, tag in enumerate(sev_scores):
    markers = []
    parts = []

    # check for vessel name, prepend
    vessel = find_vessel(tag)
    if vessel:
        vessel_part = tag[0:3]


    for n, c in enumerate(tag):
        if c.isupper():
            markers.append(n)
    for n, elem in enumerate(markers):
        if n < len(markers) - 1:
            next_part = tag[markers[n]:markers[n + 1]]
        else:
            next_part = tag[markers[n]:]
        parts.append(next_part)
    # print(parts)
    # print()

    strin = match_part_to_def(parts, severity_defs, 'Stress')
    print(f'output: {strin}')

