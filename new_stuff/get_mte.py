from lxml import html

def file_to_tree(filename):
    '''
    Opens a file and returns an lxml tree
    '''
    file = open(filename, 'r')
    source_string = file.read()
    file.close()
    return html.fromstring(source_string)

def get_mte_marks(sub_tr):
    na = 'NA'
    '''
    Subjects and then marks are found in <tr> elements
    MTE marks need to extracted from those

    sub_tr is the <tr> element in the tree where the subject string is found
    na is the string to return for subjects for which there was no mte

    - Theory MTE marks are found in the 1st following sibling of this <tr> element
    - Objective MTE marks are found in the 3rd following sibling of this <tr> element
    '''

    # storing all the following siblings in a list:
    following_siblings = sub_tr.xpath('./following-sibling::*')
    n_siblings = len(following_siblings)

    # checking for theory MTE:
    if n_siblings>=1:
        theory_title = following_siblings[0].xpath('./child::*[3]/text()')[0].strip()
        if theory_title == 'Theory Mid Term':   # checking if this is the actual <tr> required
            return following_siblings[0].xpath('./child::*[5]/text()')[0]
    else: return na

    # checking for objective MTE:
    if n_siblings>=3:
        obj_title = following_siblings[2].xpath('./child::*[3]/text()')[0].strip()
        if obj_title == 'Objective Type Mid Term':
            return following_siblings[2].xpath('./child::*[5]/text()')[0]
        else: return na
    else: return na

def extract_all(tree):
    '''
    Stores the subject and MTE marks as pairs in a dictionary and returns that dictionary
    '''
    marks_dict = {}
    sub_trs=tree.xpath('//tr[@class="rgRow" and .//span/text()]|//tr[@class="rgAltRow" and .//span/text()]')
    # ^ tr elements with subjects and CA marks in them
    for sub_tr in sub_trs:
        subject_name = sub_tr.xpath(".//span/text()")[0]
        marks_dict[subject_name] = get_mte_marks(sub_tr)
    return marks_dict
    pass


# main program:
tree = file_to_tree('marks.html')
marks_dict = extract_all(tree)
for subject in marks_dict:
    print(subject+': '+marks_dict[subject])