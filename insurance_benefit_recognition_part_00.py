# -*- coding: utf-8 -*-

from sys import argv
import os
import re
import shutil

output_file_name = 'integrated_term_line.txt'
print '***请先重新下载最新版本的sentence_splitting文本***\n本程序提取原始文档所有句子，并整合至一个TXT文档下，格式如“PID|SENTENCE|IS_TITLE”'
print '参数一：目标文件夹路径；'
print '参数二（可选）：PID白名单，跳过只做白名单下的PID'
print '输出文件为：%s'%output_file_name
print '注：请保证本目录包含文档结构表./document_structure_tab'

if len(argv) == 3:
    src_folder = argv[1]
    whitelist_file = argv[2]
elif len(argv) == 2:
    src_folder = argv[1]
    whitelist_file = ''
else:
    print 'not enough parameter.'
    exit()

document_structure_tab_path = './document_structure_tab'

# initialize the document structure info
doc_structure_tab = {}
with open(document_structure_tab_path) as f:
    for line in f.readlines():
        line = line.strip()
        line_info = line.split('|')
        if len(line_info) != 7:
            continue
        doc_structure_tab[line_info[0]] = (line_info[1], line_info[2], line_info[3], line_info[4], line_info[5], line_info[6])

def get_next_title_sn(cur_title_sn):
    chs_sn_order = {
        u'十': u'十一',
        u'一': u'二',
        u'二': u'三',
        u'三': u'四',
        u'四': u'五',
        u'五': u'六',
        u'六': u'七',
        u'七': u'八',
        u'八': u'九',
        u'九': u'十',
    }
    match = re.match(ur'第([一二三四五六七八九十]+)条', cur_title_sn)
    if match:
        if len(match.group(1)) == 1:
            return [match.group(0).replace(match.group(1), chs_sn_order[match.group(1)])]
        elif match.group(1) == u'十九':
            return [match.group(0).replace(match.group(1), u'二十')]
        elif match.group(1)[-1] == u'九':
            title_sn_part_1 = match.group(1)[0]
            title_sn_part_2 = match.group(1)[1:-1]
            title_sn_part_3 = match.group(1)[-1]
            next_title_sn = chs_sn_order[title_sn_part_1] + u'十'
            return [match.group(0).replace(match.group(1), next_title_sn)]
        else:
            title_sn_part_1 = match.group(1)[:-1]
            title_sn_part_2 = match.group(1)[-1]
            next_title_sn = title_sn_part_1 + chs_sn_order[title_sn_part_2]
            return [match.group(0).replace(match.group(1), next_title_sn)]

    match = re.match(ur'(\d+)\.(\d+)', cur_title_sn)
    if match:
        return ['%s.%s'%(match.group(1), int(match.group(2))+1), '%s.%s'%(int(match.group(1))+1, 1)]

    match = re.match(ur'(\d+)\.[^0-9]', cur_title_sn)
    if match:
        return ['%s.'%(int(match.group(1)) + 1)]

    match = re.match(ur'(\d+)[^0-9]', cur_title_sn)
    if match:
        return ['%s.'%(int(match.group(1)) + 1)]

    return []

whitelist_pid_arr = []
if whitelist_file != '':
    with open(whitelist_file) as wl:
        for line in wl.readlines():
            line = line.strip()
            if line.isdigit() == True:
                whitelist_pid_arr.append(int(line))
if len(whitelist_pid_arr) > 0:
    print 'white list detected, there are %d pid in white list' % len(whitelist_pid_arr)

output_file = open(output_file_name, 'w')
integrated_file_count = 0
for roots, dirs, files in os.walk(src_folder):
    for name in files:
        match = re.match(ur'(\d+)_sentence_splitting.txt', name)
        if not match:
            continue

        pid = int(match.group(1))
        # if pid != 1516:
        #     continue

        if doc_structure_tab.has_key(str(pid)) != True:
            print 'ERR: no structure info of this document %s' % name

        if int(doc_structure_tab[str(pid)][5]) == 0:
            print 'ERR: this document is not processable:', name
            continue

        if len(whitelist_pid_arr) > 0 and pid not in whitelist_pid_arr:
            ingnore_file_count += 1
            continue

        title_sn_pattern = ''
        if int(doc_structure_tab[str(pid)][2]) == 1:
            title_sn_pattern = u'^\d+\.\d+'
        elif int(doc_structure_tab[str(pid)][2]) == 2:
            title_sn_pattern = u'^第[一二三四五六七八九十]+条'
        elif int(doc_structure_tab[str(pid)][2]) == 3:
            title_sn_pattern = u'^\d+'
        elif int(doc_structure_tab[str(pid)][2]) == 4:
            title_sn_pattern = u'^\d+\.'
        else:
            print 'ERR: no title serial number pattern matches this document:', name
            continue

        file_path = os.path.join(src_folder, name)
        file_tmp = open(file_path)
        output_line_arr = []
        for line in file_tmp.readlines():
            line = line.strip().decode('utf-8')
            match = re.match(ur'%s'%title_sn_pattern, line)
            if match:
                is_title = 1
            else:
                is_title = 0
            str_tmp = '%s|%s|%s\n' % (pid, line, is_title)
            output_file.write(str_tmp.encode('utf-8'))
        file_tmp.close()
        integrated_file_count += 1

output_file.close()

print '%d files processed' % integrated_file_count
