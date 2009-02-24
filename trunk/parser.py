#-*- coding: UTF-8 -*-
#
# Copyright 2009 Vee Satayamas
# 
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.


import re

def parse_date(txt):
    pat = re.compile('^(?P<day>\d+)/(?P<month>\d+)/(?P<year>\d+)$')
    m = pat.match(txt)
    if m:
        d = m.groupdict()
        d_ = {}
        for k, v in d.items():
            d_[k] = int(v)
        d = d_
    else:
        pat2 = re.compile('^(?P<month>\d+)/(?P<year>\d+)$')
        m2 = pat2.match(txt)
        if m2:  
            d = m2.groupdict()
            d_ = {}
            for k, v in d.items():
                d_[k] = int(v)
            d = d_
            d['day'] = None
        else:
            raise RuntimeError, "cannot parse date" + " :" + txt + ":"
    return d
            
def parse_activity(m, statements):
    desc = m.group(2).strip()
    statements.append({'type': 'activity', 'desc': desc})
    
def parse_act_start(m):
    date = parse_date(m.groupdict()['date'].strip())
    return ('start', date)
    
def parse_act_end(m):
    date = parse_date(m.groupdict()['date'].strip())
    return ('end', date)
 
def parse_act_complete(m):
    percent = int(m.groupdict()['percent'].strip())
    return ('complete', percent)

def parse_activity_detail(m, statements):
    pats = [(u"^ตั้งแต่(?P<date>.+)", parse_act_start), 
                (u"^ถึง(?P<date>.+)", parse_act_end),
                (u"^สำเร็จร้อยละ\s*(?P<percent>\d+)", parse_act_complete)]
    pats = map(lambda pat: (re.compile(pat[0]), pat[1]), pats)
    result = None
    for pat in pats:
        m_ = pat[0].match(m.group(2).strip())
        if m_:
            result = pat[1](m_)
            break
    if result is None:
        raise RuntimeError, "Cannot parse activity detail"
    if len(statements) == 0 or statements[-1]['type'] != 'activity':
        raise RuntimeError, "There is no activity before activity detail"
    statements[-1][result[0]] = result[1]
        
def parse_start(m, statements):
    statements.append({'type': 'start', 'date': parse_date(m.group(2).strip())})
    
def parse_end(m, statements):
    statements.append({'type': 'end', 'date': parse_date(m.group(2).strip())})

def parse_resolution(m, statements):
    m_ = re.match(u"^(\d+)\s+เดือน$", m.group(2).strip())
    if m_:
        statements.append({'type': 'resolution', 
                           'day': 0, 
                           'year': 0, 
                           'month': int(m_.group(1))})
    else:
        raise RuntimeError, "Cannot parse resolution"

def parse_width(m, statements):
    m_ = re.match(u"^(\d+)$", m.group(2).strip())
    if m_:
        statements.append({'type': 'width', 'value': int(m_.group(1))})
    else:
        raise RuntimeError, "Cannot parse width"
        
def parse_first_column_width(m, statements):
    m_ = re.match(u"^(\d+)$", m.group(2).strip())
    if m_:
        statements.append({'type': '1st_col_width', 
                           'value': int(m_.group(1))})
    else:
        raise RuntimeError, "Cannot parse first column width"
                
def parse(txt):
    start_pats = [(u"(^กิจกรรม)(.+)", parse_activity) , 
                         (u"(^\*)(.+)", parse_activity_detail), 
                         (u"(^เริ่ม)(.+)", parse_start),
                         ( u"(^สิ้นสุด)(.+)", parse_end ), 
                         (u"(^ความละเอียด)(.+)", parse_resolution),
                         (u"(^ช่องกว้าง)(.+)", parse_width),
                         (u"(^ช่องแรกกว้าง)(.+)", parse_first_column_width)]
    start_pats = map(lambda pat: (re.compile(pat[0]), pat[1]), start_pats)
   
    statements = []
    for line in txt.replace("\r", "").split("\n"):
        line = line.strip()
        if line != '':
            for pat in start_pats:
                m = pat[0].match(line)
                if m:
                    pat[1](m, statements)
                    break            
    return statements
