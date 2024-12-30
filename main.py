"""
program: main.py

purpose: Main routine for project ectb_xml.
         Read data from an XML file and construct a glossary of tagname meanings,
         in the context of Emory Cardiac Toolbox (ECTb) software.

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
12-26-2024  Add tags for summed perfusion score. Add find_uc_prefix() to detect
            a sequence of uppercase characters at the start of the tag name.
12-28-2024  Refactor handling of number of tag parts (fixes defect severity
            output.) Detect initial lowercase letter in a tagname (fixes defect
            mass output.) Edit mass definitions.
12-30-2024  Refactor handling of a string to prepend to the tag output (see
            match_parts_to_defs().
"""
from pathlib import Path
import xml.etree.ElementTree as ET

# def get_tag_values(xmlroot):
#     record = {'ptname' : xmlroot.find('PatientName').text,
#               'age' : int(xmlroot.find('PatientAge').text),
#               'tid' : float(xmlroot.find('TIDindex').text),
#               'stress_ef' : int(xmlroot.find('StressLVEjectionFraction').text),
#               'rest_ef' : int(xmlroot.find('RestLVEjectionFraction').text)
#               }
#     return record


# def find_vessel(tag):
#     vessels = ['LAD', 'LCX', 'RCA']
#     for v in vessels:
#         if tag.rfind(v) != -1:
#             return v


# def find_lv(tag):
#     found_lv = False
#     if tag.rfind("LV") != -1: found_lv = True
#
#     return found_lv


# def find_edes(tag):
#     found_edes = False
#     if tag.rfind("ED") != -1 or tag.rfind("ES") != -1: found_edes = True
#
#     return found_edes


def find_uc_prefix(tag, truncate=True):
    seq = ''
    for n, c in enumerate(tag):
        if c.isupper():
            seq = seq + c
        else:
            break

    if truncate is True:
        return seq[:-1]
    else:
        return seq


# def handle_tags(tag_group, tag_defs, prepend=None, gmass=False, ignore=None):
def handle_tags(tag_group,
                tag_defs,
                prepend=None,
                append=None,
                ignore=None,
                truncate=True):
    output_set = []
    for tagnum, tag in enumerate(tag_group):
        # tag_parts = extract_parts(tag, gmass)
        tag_parts = extract_parts(tag, truncate)
        output = match_parts_to_defs(tag_parts, tag_defs, prepend, append, ignore)
        output_set.append(output)

    return output_set


def extract_parts(tag, truncate=True):
    markers = []
    parts = []

    upperc_prefix = find_uc_prefix(tag, truncate)
    # print(f'found uppercase seq: {uc_sequence}')
    if upperc_prefix != '':
        tag = tag.removeprefix(upperc_prefix)
        parts.append(upperc_prefix)

    # handle initial lowercase letter in the tag
    if tag[0].islower():
        markers.append(0)

    for n, c in enumerate(tag):
        if c.isupper():
            markers.append(n)
    for n, elem in enumerate(markers):
        if n < len(markers) - 1:
            next_part = tag[markers[n]:markers[n + 1]]
        else:
            next_part = tag[markers[n]:]
        # if vessel_part:
        #     parts.append(vessel_part)
        #     vessel_part = ''
        # else:
        parts.append(next_part)
    # print(parts)
    return parts


def match_parts_to_defs(parts, defs, prepend=None, append=None, ignore=None):
    output = ''
    # if len(parts) > len(defs):
    #     output += parts[0]
    # else:
    #     if prepend is not None:
    #         output += prepend

    # if len(parts) < len(defs):
    #     if prepend is not None:
    #         output += prepend
    # print(f'parts: {parts}')
    for n, item in enumerate(parts):
        if item in defs.keys():
            # if prepend is not None:
            #     if prepend[0] == '':
            #         output += prepend[1] + ' ' + defs[item]
            # else:
            output += ' ' + defs[item]
        else:
            if ignore is None:
                output += ' ' + item
            else:
                 if isinstance(ignore, list) and not item in ignore:
                     output += ' ' + item

    if append is not None:
        output += ' ' + append

    output_prep = output.strip()
    output_final = output_prep
    if prepend is not None:
        if prepend[0] == '' or output_prep.startswith(prepend[0]):
            output_final = prepend[1] + ' ' + output_prep
        # else:
        #     output_final = output_prep
    return output_final.capitalize()
    # return output.strip()


# def sentence_case(input_str: str):
#     str_list = input_str.strip().split(' ')
#     str_list_lc = [s.lower() for s in str_list]
#     str_sentence = ' '.join(str_list_lc)
#
#     return str_sentence

# tag translation definitions
# ===========================
severity_defs = {'Tot': 'total',
                 'Rev': 'reversible',
                 'Sev': 'defect severity'
                 # 'Score': 'score'
                 }

defect_defs = {'Extent': 'defect extent,',
               'Total': 'in pixels',
               'Reversed': 'defect reversed,'
               }
mass_defs = {'Ung': 'ungated mass in g,',
             'g': 'gated mass in g,',
             # 'Restg': 'Rest mass in g,',
             # 'Stressg': 'Stress mass in g,',
             'Myo': 'myocardium',
             'Def': 'defect',
             'Defect': 'defect',
             'Pct': 'as percent of',
             'Rev': 'reversible',
             'Total': 'total'
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
summed_score_defs = {'SS': 'summed stress',
                     'SR': 'summed rest',
                     'SD': 'summed difference'
                     }

volume_defs = {
    'L': 'left',
    'V': 'ventricle',
    'Volume': 'volume in ml'
}

# Read the XML file
# -----------------
mypath = Path('data')

filepath = mypath / 'CroDa_no_arrays.xml'

tree = ET.parse(filepath)
xmlroot = tree.getroot()

ectb_tags = [elem.tag for elem in xmlroot.iter()]

# define tag groups
# -----------------
# TODO: use tuple of values for methods like endswith
severity_scores = [tag for tag in ectb_tags if tag.endswith('SevScore')]

defect_values = [tag for tag in ectb_tags if
                 # tag.find('Extent') != -1 or
                 # tag.find('Reversed') != -1]
                 'Extent' in tag or
                 'Reversed' in tag]
segment_scores = [tag for tag in ectb_tags if
                  tag.endswith('ScoreStr') or
                  tag.endswith('ScoreRst')]
mass_values = [tag for tag in ectb_tags if
               tag.startswith('g') or
               tag.startswith('Ung')]
str_segment_values = [tag for tag in ectb_tags if
               tag.endswith('Str')]
rst_segment_values = [tag for tag in ectb_tags if
               tag.endswith('Rst')]
summed_scores = [tag for tag in ectb_tags if tag.endswith('score')]
volume_values = [tag for tag in ectb_tags if
                 (tag.endswith('EjectionFraction') or
                 tag.endswith('Volume')) and
                 tag.startswith(('Stress', 'Rest'))]
phase_values = [tag for tag in ectb_tags if 'Phase' in tag]

# from gated, find items: LV, ES, ED
# ?? need to find PFR...
# study1_gated_tags = [tag for tag in ectb_tags if tag.startswith('Study1')]
# study2_gated_tags = [tag for tag in ectb_tags if tag.startswith('Study2')]

# parse tag name based on 'sections' as determined by character case
# s1 = 'TotScore'
# s1.isalpha()

defect_output = handle_tags(defect_values, defect_defs, 'Total')

severity_output = handle_tags(severity_scores,
                              severity_defs,
                              prepend=('Tot', 'Stress'),
                              append='in standard deviation units')

summed_output = handle_tags(summed_scores,
                            summed_score_defs,
                            append='score',
                            truncate=False)

# mass_output = handle_tags(mass_values, mass_defs, gmass=True, ignore=['Mass'])
# TODO: refactor mass tags to include stress and rest MyoMass
mass_output = handle_tags(mass_values, mass_defs, ignore=['Mass'])

str_segment_output = handle_tags(str_segment_values,
                                 segment_defs,
                                 prepend=('', 'Stress'),
                                 ignore=['Str'])

rst_segment_output = handle_tags(rst_segment_values,
                                 segment_defs,
                                 prepend=('', 'Rest'),
                                 ignore=['Rst'])

volume_output = handle_tags(volume_values,
                            volume_defs)

# phase_output = handle_tags()

# print('defect:')
# for item in defect_output:
#     print(f'    {item}')

print('severity:')
for item in severity_output:
    print(f'    {item}')

# print('mass:')
# for item in mass_output:
#     print(f'    {item}')

# print('summed scores:')
# for item in summed_output:
#     print(f'    {item}')

# print('segment scores:')
# for item in str_segment_output:
#     print(f'    {item}')
# print()
# for item in rst_segment_output:
#     print(f'    {item}')

print('volumes and EF:')
for item in volume_output:
    print(f'    {item}')

# print('phase:')
# for item in phase_output:
#     print(f'    {item}')

