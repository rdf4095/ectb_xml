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
            handle_tags().
12-13-2024  Add tag set for gated and ungated mass values.
12-24-2024  Add tags for 17 segments. Make 'ignore' parameter a list. Remove
            'gmass' parameter.

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


# def handle_tags(tag_group, tag_defs, prepend=None, gmass=False, ignore=None):
def handle_tags(tag_group, tag_defs, prepend=None, ignore=None):
    output_set = []
    for tagnum, tag in enumerate(tag_group):
        # tag_parts = extract_parts(tag, gmass)
        tag_parts = extract_parts(tag)
        output = match_parts_to_defs(tag_parts, tag_defs, prepend, ignore)
        output_set.append(output)

    return output_set


# def extract_parts(tag, gmass=False):
def extract_parts(tag):
    # for tagnum, tag in enumerate(tag_group):
    markers = []
    parts = []

    # check for vessel name, prepend
    vessel = find_vessel(tag)
    if vessel:
        vessel_part = tag[0:3]
    else:
        vessel_part = ''

    # if gmass:
    #     markers.append(0)

    for n, c in enumerate(tag):
        if c.isupper():
            markers.append(n)
    for n, elem in enumerate(markers):
        if n < len(markers) - 1:
            next_part = tag[markers[n]:markers[n + 1]]
        else:
            next_part = tag[markers[n]:]
        if vessel_part:
            parts.append(vessel_part)
            vessel_part = ''
        else:
            parts.append(next_part)

    return parts


def match_parts_to_defs(parts, defs, prepend=None, ignore=None):
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
        else:
            if isinstance(ignore, list):
                if item in ignore:
                    pass
                else:
                    output += ' '
                    output += item
    return output


# tag translation definitions
# ===========================
severity_defs = {'Tot': 'Total',
                 'Sev': 'defect severity',
                 'Score': 'in standard deviation units'
                 }
defect_defs = {'Extent': 'defect extent,',
               'Total': 'in pixels',
               'Reversed': 'defect reversed,'
               }
mass_defs = {'Ung': 'Ungated Mass,',
             'g': 'Gated Mass,',
             'Myo': 'Myocardium',
             'Def': 'Defect',
             'Defect': 'Defect',
             'Pct': 'Percent of',
             'Rev': 'Reversible',
             'Total': 'Total'
             }
segment_defs = {'Bas': 'basal',
                'Mid': 'mid',
                'Ap': 'apical',
                'Ant': 'anterior',
                'Inf': 'inferior',
                'Lat': 'lateral',
                'Sep': 'septal',
                'Score': 'score'
                }

# Read the XML file
# =================
mypath = Path('data')

filepath = mypath / 'CroDa_no_arrays.xml'

tree = ET.parse(filepath)
xmlroot = tree.getroot()

ectb_tags = [elem.tag for elem in xmlroot.iter()]

# define tag groups
# -----------------
severity_scores = [tag for tag in ectb_tags if tag.endswith('SevScore')]
defect_values = [tag for tag in ectb_tags if
                 tag.find('Extent') != -1 or
                 tag.find('Reversed') != -1]
segment_scores = [tag for tag in ectb_tags if
                  tag.endswith('ScoreStr') or
                  tag.endswith('ScoreRst')]
mass_values = [tag for tag in ectb_tags if
               tag.startswith('Ung') or
               tag.startswith('g')]
str_segment_values = [tag for tag in ectb_tags if
               tag.endswith('Str')]
rst_segment_values = [tag for tag in ectb_tags if
               tag.endswith('Rst')]
summed_scores = []

# from gated, find items: LV, ES, ED
# ?? need to find PFR...
study1_gated_tags = [tag for tag in ectb_tags if tag.startswith('Study1')]
study2_gated_tags = [tag for tag in ectb_tags if tag.startswith('Study2')]

# parse tag name based on 'sections' as determined by character case
s1 = 'TotScore'
s1.isalpha()

severity_output = handle_tags(severity_scores, severity_defs, 'Stress')

defect_output = handle_tags(defect_values, defect_defs, 'Total')

# mass_output = handle_tags(mass_values, mass_defs, gmass=True, ignore=['Mass'])
mass_output = handle_tags(mass_values, mass_defs, ignore=['Mass'])

str_segment_output = handle_tags(str_segment_values,
                                 segment_defs,
                                 prepend='Stress',
                                 ignore=['Str'])

rst_segment_output = handle_tags(rst_segment_values,
                                 segment_defs,
                                 prepend='Rest',
                                 ignore=['Rst'])

# print('defect:')
# for item in defect_output:
#     print(f'    {item}')

# print('severity:')
# for item in severity_output:
#     print(f'    {item}')

print('mass:')
for item in mass_output:
    print(f'    {item}')

# print('segment scores:')
# for item in str_segment_output:
#     print(f'    {item}')
# print()
# for item in rst_segment_output:
#     print(f'    {item}')
