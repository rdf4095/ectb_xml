"""
program: main.py

purpose: Main routine for project ectb_xml.
         Read data from an XML file and construct a glossary of tagname meanings,
         in the context of Emory Cardiac Toolbox (ECTb) software.

         Possible output formats
         --------
         1. WSV: Whitespace-Separated Values (see: WhitespaceSV.com)
         2. JSON
         3. OML (like JSON, with whitespace instead of commas, and quotes used only
            for values that contain spaces)
         4. TBL (like SML with heirarchical rows; 1 value=level, 2 values = attribute & value)
         5. plain text

author: Russell Folks

history:
-------
11-18-2024  creation
11-22-2024  Test algorithm to segment terms by case, using sev scores.
12-05-2024  Move alternate xml-reading methods to alternate_xml.txt.
12-07-2024  Add more tag lists: segments, summed scores, gated results,
12-08-2024  Change some inline comments, simplify get_tag_values(), add tag
            definitions for segmental scores.
12-11-2024  Combine extract_parts() and match_parts_to_defs() into
            handle_tags()
"""
from pathlib import Path
import xml.etree.ElementTree as ET

def get_tag_values(xmlroot):
    record = {'ptname' : xmlroot.find('PatientName').text,
              'age' : int(xmlroot.find('PatientAge').text),
              'tid' : float(xmlroot.find('TIDindex').text),
              'stress_ef' : int(xmlroot.find('StressLVEjectionFraction').text),
              'rest_ef' : int(xmlroot.find('RestLVEjectionFraction').text)
             }

    return record


def find_vessel(tag):
    # method 1
    # found_lad = False
    # found_lcx = False
    # found_rca = False
    #
    # if tag.rfind("LAD") != -1: found_lad = True
    # if tag.rfind("LCX") != -1: found_lad = True
    # if tag.rfind("RCA") != -1: found_lad = True

    # return (found_lad, found_lcx, found_rca)

    # method 2
    vessels = ['LAD', 'LCX', 'RCA']
    for v in vessels:
        if tag.rfind(v) != -1:
            return v


def find_lv(tag):
    found_lv = False
    if tag.rfind("LV") != -1: found_lv = True

    return found_lv


def find_edes(tag):
    found_edes = False
    if tag.rfind("ED") != -1 or tag.rfind("ES") != -1: found_edes = True

    return found_edes


def handle_tags(tag_group, tag_defs, prepend=None):
    output_set = []
    for tagnum, tag in enumerate(tag_group):
        tag_parts = extract_parts(tag)
        output = match_parts_to_defs(tag_parts, tag_defs, prepend)
        output_set.append(output)

    return output_set


def extract_parts(tag):
    # for tagnum, tag in enumerate(tag_group):
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

    return parts


def match_parts_to_defs(parts, defs, prepend=None):
    output = ''
    if len(parts) > len(defs):
        output += parts[0]
    else:
        if prepend is not None:
            output += prepend

    for n, item in enumerate(parts):
        if item in defs.keys():
            output += ' '
            output += defs[item]

    return output


# tag translation definitions
# ===========================
severity_defs = {'Tot': 'Total',
                 'Sev': 'defect severity',
                 'Score': 'in standard deviation units'}
defect_defs = {'Extent': 'defect extent,',
               'Total': 'in pixels',
               'Reversed': 'defect reversed,'}
# defect_defs.keys()
segmental_defs = {'Bas': 'Basal',
                  'Mid': 'Mid',
                  'Ap': 'Apical',
                  'Ant': 'anterior',
                  'Inf': 'inferior',
                  'Lat': 'lateral',
                  'Sep': 'septal'
                  }
# gated_defs = {}

# Read the XML file
# =================
mypath = Path('data')

filepath = mypath / 'CroDa_no_arrays.xml'

tree = ET.parse(filepath)
xmlroot = tree.getroot()

ectb_tags = [elem.tag for elem in xmlroot.iter()]

# tag groups
# ==========
severity_scores = [tag for tag in ectb_tags if tag.endswith('SevScore')]
defect_values = [tag for tag in ectb_tags if
                 tag.find('Extent') != -1 or
                 tag.find('Reversed') != -1]
segment_scores = [tag for tag in ectb_tags if
                  tag.endswith('ScoreStr') or
                  tag.endswith('ScoreRst')]

# from gated, find items: LV, ES, ED
# ?? need to find PFR...
study1_gated_tags = [tag for tag in ectb_tags if tag.startswith('Study1')]
study2_gated_tags = [tag for tag in ectb_tags if tag.startswith('Study2')]


# print(f'defect tags: {defect_values}')
# print(f'sev tags: {sev_scores}')

# parse tag name based on 'sections' as determined by letter case
s1 = 'TotScore'
s1.isalpha()

# for tagnum, tag in enumerate(severity_scores):
#     markers = []
#     parts = []
#
#     # check for vessel name, prepend
#     vessel = find_vessel(tag)
#     if vessel:
#         vessel_part = tag[0:3]
#
#     for n, c in enumerate(tag):
#         if c.isupper():
#             markers.append(n)
#     for n, elem in enumerate(markers):
#         if n < len(markers) - 1:
#             next_part = tag[markers[n]:markers[n + 1]]
#         else:
#             next_part = tag[markers[n]:]
#         parts.append(next_part)
#
#     severity_output = match_parts_to_defs(parts, severity_defs, 'Stress')
#     print(f'parts: {parts}')
#     print(f'output: {severity_output}')

# severity_parts = extract_parts(severity_scores)
severity_output = handle_tags(severity_scores, severity_defs, "Stress")

print('severity:')
for item in severity_output:
    print(f'    {item}')

defect_output = handle_tags(defect_values, defect_defs)

print('defect:')
for item in defect_output:
    print(f'    {item}')

# print(f'    {defect_output}')

