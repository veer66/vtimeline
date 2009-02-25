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

import cgi
import sys
from month import month_thai_short

DAY = 0
MONTH = 1
YEAR = 2
MONTH_NUM = 12
HEAD_ROW_NUM = 2

class Drawer(object):
    def __init__(self, out, specs, max_x = 1024, max_y = 800):
        self.max_x = max_x
        self.max_y = max_y
        self.out = out
        self.specs = specs
        if 'width' in self.specs:
            self.x_fac = self.specs['width']['value']
        else:
            self.x_fac = 100 
        self.y_fac = 30
        if '1st_col_width' in self.specs:
            self.desc_len = self.specs['1st_col_width']['value']
        else:
            self.desc_len = 300
        self.main_move_x = 30
        self.main_move_y = 30
        self.move_from_line_x = 5
        self.move_text_up_y = 10
        self.bar_space = 5

    def duration(self):
        diff_date = self.diff_date(self.specs['start']['date'], \
                                   self.specs['end']['date'])
        time_unit = self.time_unit(diff_date) 
        return time_unit
            
    def resolution(self):
        r_list = [1,2,3,4,6] # MONTH_NUM % r = 0
        r_list.reverse()
        ri = self.specs['resolution']['month']
        r = 1
        for r_ in r_list:
            if r_ <= ri:
                r = r_
                break
        return r

    def time_unit(self, date_tuple):
        r = self.resolution()
        u = date_tuple[YEAR] * MONTH_NUM + date_tuple[MONTH]
        u = (u + r - 1) / r
        return u
    
    def diff_date(self, start, end):
        start_year = start['year']
        start_month = self.adjusted_start_month()
        start_day = end['day']
        end_year = end['year']
        end_month = self.adjusted_end_month()
        end_day = end['day']
        if end_year is not None and start_year is not None:
            year_diff = end_year - start_year 
        else:
            year_diff = None
        if end_month is not None and start_month is not None:
            month_diff = end_month - start_month + 1
        else:
            month_diff = None
        if end_day is not None and start_day is not None:
            day_diff = end_day - start_day 
        else:
            day_diff = None
        return (day_diff, month_diff, year_diff)

    def g_move(self, x, y):
        print >>self.out, "<g transform=\"translate(%d,%d)\">" % (x, y)

    def g_close(self):
        print >>self.out, "</g>"

    def __call__(self):
        self.g_move(self.main_move_x, self.main_move_y)
        self.draw_header()
        self.draw_desc()
        self.draw_lines()
        self.draw_progress()
        self.g_close()
        return {'maxy': self.maxy + self.main_move_x * 2, 
                'maxx': self.maxx + self.main_move_y * 2}

    def draw_progress(self):
        for i, activity in enumerate(self.activities()):
            sm = activity['start']['month']
            sy = activity['start']['year']
            sd = self.month_year_to_duration_floor(sm, sy)
            em = activity['end']['month']
            ey = activity['end']['year']
            ed = self.month_year_to_duration_ceiling(em, ey) 
            x1 = sd * self.x_fac + self.desc_len
            x2 = ed  * self.x_fac + self.desc_len
            y1 = self.y_fac * (2 + i) + self.bar_space 
            y2 = self.y_fac * (2 + i + 1) - self.bar_space
            self.draw_rect(x1, y1, x2, y2, "#E0E0E0")
            if 'complete' in activity:
                c = activity['complete']
                x2_ = x1 + int((x2 - x1) * float(c) / 100.0)
                self.draw_rect(x1, y1+5, x2_, y2-5)
    
    def draw_rect(self, x1, y1, x2, y2, fill="black"):
        print >>self.out, "<rect x=\"%d\" y=\"%d\" width=\"%d\" height=\"%d\" fill=\"%s\"/>" % (x1, y1, x2 - x1, y2 - y1, fill)

    def adjusted_start_month(self):
        start_m = self.specs['start']['date']['month'] - 1
        if start_m % self.resolution() != 0:
            start_m = (start_m  / self.resolution()) * self.resolution()
        return start_m + 1

    def adjusted_end_month(self):
        end_m = self.specs['end']['date']['month'] 
        if end_m % self.resolution() != 0:
            end_m = ((end_m + self.resolution() - 1) / \
                      self.resolution()) * self.resolution()
            end_m += 1
        return end_m 

    def start_year(self):
        start_y = self.specs['start']['date']['year']
        return start_y

    def month_year_start(self, i):
        start_m = self.adjusted_start_month()
        start_y = self.start_year()
        m = i * self.resolution() + start_m - 1
        y = start_y + m / MONTH_NUM
        m = m % MONTH_NUM
        return (m + 1, y)

    def month_year_end(self, i):
        start_m = self.adjusted_start_month()
        start_y = self.specs['start']['date']['year']
        m = ((i + 1) * self.resolution()) + start_m - 1
        y = start_y + m / MONTH_NUM 
        m = m % MONTH_NUM
        return (m - 1, y)

    def month_year_to_duration_ceiling(self, m, y):
        start_m = self.adjusted_start_month()
        start_y = self.start_year()
        dy = y - start_y
        dm = m - start_m
        d = dm + dy * MONTH_NUM
        if self.resolution() > 1:
            d = (d + self.resolution() - 1)/ self.resolution()
        else:
            d += 1 
        return d

    def month_year_to_duration_floor(self, m, y):
        start_m = self.adjusted_start_month()
        start_y = self.start_year()
        dy = y - start_y
        dm = m - start_m
        d = dm + dy * MONTH_NUM
        return d / self.resolution()

    def month_str(self, d):
        if self.resolution() > 1:
            smonth = self.month_year_start(d)[0] # 0 - year
            emonth = self.month_year_end(d)[0] # 0 - year
            result = month_thai_short[smonth - 1] + "-" + month_thai_short[emonth]
        else:
            month = self.month_year_start(d)[0]
            result = month_thai_short[month - 1]
        return result

    def draw_header(self):
        duration = self.duration()
        mx = (duration) * self.x_fac
        self.g_move(self.desc_len, 0)
        self.draw_months()
        self.draw_years()
        self.g_close()

    def text(self, txt, x, y):
        print >>self.out, "<text x=\"%d\" y=\"%d\">%s</text>" % (x, y, txt) 

    def draw_years(self):
        duration = self.duration()
        self.g_move(0, self.y_fac - self.move_text_up_y)
        y_ = None
        for d in range(duration):
            y = self.month_year_start(d)[1] # 1 = year
            if y_ != y:
                y_ = y
                self.text(str(y) , self.move_from_line_x + d * self.x_fac, 0)
        self.g_close()

    def draw_months(self):
        duration = self.duration()
        x = 0
        self.g_move(0, self.y_fac * HEAD_ROW_NUM - self.move_text_up_y)
        for d in range(duration):
            self.text(self.month_str(d), self.move_from_line_x + d * self.x_fac, 0)
        self.g_close()

    def draw_lines(self):
        duration = self.duration()
        mx = (duration) * self.x_fac + self.desc_len
        my = self.y_fac * (HEAD_ROW_NUM + len(self.activities()))
        self.maxy = my
        self.maxx = mx
        self.draw_line(0, 0, mx, 0)
        self.draw_line(self.desc_len, self.y_fac, mx, self.y_fac)
        y = self.y_fac * HEAD_ROW_NUM
        self.draw_line(0, y, mx, y)
        self.draw_line(0, 0, 0, my)

        # year vertical line
        y_ = None
        for d in range(duration):
            y = self.month_year_start(d)[1]
            if y_ != y:
                y_ = y
                x = self.desc_len + d * self.x_fac
                self.draw_line(x, 0, x, my)
       
        x = self.desc_len + duration * self.x_fac
        self.draw_line(x, 0, x, my)

        # month veritcal line
        for d in range(duration):
            x = self.desc_len + d * self.x_fac
            self.draw_line(x, self.y_fac, x, my)

        # activity horizontal lines
        y = self.y_fac * HEAD_ROW_NUM
        for i, activity in enumerate(self.activities()):
            y += self.y_fac
            self.draw_line(0, y, self.desc_len + duration * self.x_fac, y)

    def activities(self):
        return self.specs['activities']

    def draw_line(self, x1, y1, x2, y2):
        print >>self.out, "<g stroke=\"black\"><line x1=\"%d\" y1=\"%d\" x2=\"%d\" y2=\"%d\" stroke-width=\"1\"/></g>" % (x1, y1, x2, y2)

    def draw_desc(self):
        y = self.y_fac
        self.g_move(self.move_from_line_x, self.y_fac * HEAD_ROW_NUM - 10)
        for i, activity in enumerate(self.activities()):
            desc = cgi.escape(activity['desc'])
            def onum():
                return str(i + 1) + ". "
            def complete():
                if 'complete' in activity:
                    return u" (%d%%)" % activity['complete']
                else:
                    return ''
            self.text(onum() + desc + complete(), i + 1, y)
            y += self.y_fac 
        self.g_close()
        
def draw(specs, out):
    return Drawer(out, specs)()
