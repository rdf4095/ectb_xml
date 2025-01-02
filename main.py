"""
program: main.py

purpose: Main routine for project ectb_xml.
         Read data from an XML file and construct a glossary of tagname meanings,
         in the context of Emory Cardiac Toolbox (ECTb) software.

author: Russell Folks

history:
-------
11-18-2024  creation
... (see history.txt)
01-02-2025  Minor refactoring of functions for length. Calculate tag length
            for output spacing.
"""
from pathlib import Path
import xml.etree.ElementTree as ET

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


def handle_tags(tag_group,
                tag_defs,
                prepend=None,
                append=None,
                ignore=None,
                truncate=True,
                keep_prefix=False):
    output_list = []
    for tagnum, tag in enumerate(tag_group):
        tag_parts = extract_parts(tag, truncate)
        output = match_parts_to_defs(tag_parts, tag_defs, prepend, append, ignore, keep_prefix)

        output_list.append(output)
        values_explanations.append((tag, output))

    return output_list


def extract_parts(tag, truncate=True):
    markers = []
    parts = []

    upperc_prefix = find_uc_prefix(tag, truncate)
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
        parts.append(next_part)

    return parts


def match_parts_to_defs(parts,
                        defs,
                        prepend=None,
                        append=None,
                        ignore=None,
                        keep_prefix=False):
    output = ''
    for n, item in enumerate(parts):
        if item in defs.keys():
            output += ' ' + defs[item]
        else:
            if isinstance(ignore, list) and not item in ignore:
                output += ' ' + item

    if append is not None:
        output += append

    output_prep = output.strip()
    output_final = output_prep
    if prepend is not None:
        if prepend[0] == '' or output_prep.startswith(prepend[0]):
            output_final = prepend[1] + ' ' + output_prep
    if keep_prefix:
        return output_final
    else:
        return output_final.capitalize()


# tag translation definitions
# ===========================
severity_defs = {
    'Tot': 'total',
    'Rev': 'reversible',
    'Sev': 'defect severity'
}
defect_defs = {
    'Extent': 'defect extent,',
    'Total': 'in pixels',
     'Reversed': 'defect reversed,'
}
mass_defs = {
    'Ung': 'ungated mass,',
    'g': 'gated mass,',
    'Myo': 'myocardium',
    'Def': 'defect',
    'Defect': 'defect',
    'Pct': 'as percent of',
    'Rev': 'reversible',
    'Total': 'total'
}
segment_defs = {
    'Bas': 'basal',
    'Mid': 'mid',
    'Ap': 'apical',
    'Ant': 'anterior',
    'Inf': 'inferior',
    'Lat': 'lateral',
    'Sep': 'septal',
    'Score': 'score'
}
summed_score_defs = {
    'SS': 'summed stress',
    'SR': 'summed rest',
    'SD': 'summed difference'
}
volume_defs = {
    'L': 'left',
    'V': 'ventricular',
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
defect_values = [tag for tag in ectb_tags if
                 'Extent' in tag or
                 'Reversed' in tag]

severity_values = [tag for tag in ectb_tags if tag.endswith('SevScore')]

segment_values = [tag for tag in ectb_tags if
                  tag.endswith('ScoreStr') or
                  tag.endswith('ScoreRst')]

mass_values = [tag for tag in ectb_tags if
               tag.startswith('g') or
               tag.startswith('Ung')]

str_segment_values = [tag for tag in ectb_tags if
               tag.endswith('Str')]

rst_segment_values = [tag for tag in ectb_tags if
                      tag.endswith('Rst')]

summed_values = [tag for tag in ectb_tags if tag.endswith('score')]

volume_values = [tag for tag in ectb_tags if
                 (tag.endswith('EjectionFraction') or
                 tag.endswith('Volume')) and
                 tag.startswith(('Stress', 'Rest'))]

phase_values = [tag for tag in ectb_tags if 'Phase' in tag]

values_explanations = []

defect_output = handle_tags(defect_values, defect_defs, keep_prefix=True)

severity_output = handle_tags(severity_values,
                              severity_defs,
                              prepend=('Tot', 'Stress'),
                              append=', in standard deviation units')

summed_output = handle_tags(summed_values,
                            summed_score_defs,
                            truncate=False)

mass_output = handle_tags(mass_values, mass_defs, ignore=['Mass'],
                          append=', in grams')

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

"""
print('defect:')
for item in defect_output:
    print(f'    {item}')

print('severity:')
for item in severity_output:
    print(f'    {item}')

print('mass:')
for item in mass_output:
    print(f'    {item}')

print('summed scores:')
for item in summed_output:
    print(f'    {item}')

print('segment scores:')
for item in str_segment_output:
    print(f'    {item}')
print()
for item in rst_segment_output:
    print(f'    {item}')

print('volumes and EF:')
for item in volume_output:
    print(f'    {item}')

# print('phase:')
# for item in phase_output:
#     print(f'    {item}')
"""

# setup for output text file
# --------------------------
spacing = max([len(item[0]) for item in values_explanations])
separator = ':'

with open('output.txt', 'w') as outputfile:
    for n, item in enumerate(values_explanations):
        outputfile.write(f'{item[0] :>{spacing}} {separator} {item[1]}\n')
