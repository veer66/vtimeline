#-*- coding: UTF-8 -*-
import cgi
import sys
from month import month_thai_short

DAY = 0
MONTH = 1
YEAR = 2

class Drawer(object):
    def __init__(self, out, specs, max_x = 1024, max_y = 800):
        self.max_x = max_x
        self.max_y = max_y
        self.out = out
        self.specs = specs
        self.x_fac = 100 
        self.y_fac = 30
        self.desc_len = 200

    def duration(self):
        return self.time_unit( \
            self.diff_date(self.specs['start']['date'], \
                           self.specs['end']['date']))
       
    def resolution(self):
        r_list = [1,2,3,4,6]
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
        print >>sys.stderr, r, date_tuple
        u = date_tuple[YEAR] * 12 + date_tuple[MONTH]
        u = (u + r - 1) / r
        return u
    
    def diff_date(self, start, end):
        start_year = start['year']
        start_month = start['month']
        start_day = end['day']
        end_year = end['year']
        end_month = end['month']
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

    def time_col_num(self):
        pass

    def __call__(self):
        print >>self.out, "<g transform=\"translate(30,30)\">"
        self.draw_header()
        self.draw_desc()
        self.draw_lines()
        self.draw_progress()
        print >>self.out, "</g>"


    def draw_progress(self):
        for i, activity in enumerate(self.activities()):
            sm = activity['start']['month']
            sy = activity['start']['year']
            sd = self.month_year_to_duration_floor(sm, sy)
            em = activity['end']['month']
            ey = activity['end']['year']
            ed = self.month_year_to_duration_ceiling(em, ey)
            
            x1 = sd * self.x_fac + self.desc_len
            x2 = (ed) * self.x_fac + self.desc_len
            y1 = self.y_fac * (2 + i) + 5 
            y2 = self.y_fac * (2 + i + 1) - 5 
            self.draw_rect(x1, y1, x2, y2)

    def draw_rect(self, x1, y1, x2, y2):
        print >>self.out, "<rect x=\"%d\" y=\"%d\" width=\"%d\" height=\"%d\"/>" % (x1, y1, x2 - x1, y2 - y1)

    def adjusted_start_month(self):
        start_m = self.specs['start']['date']['month']
        start_m = ((start_m - 1) / self.resolution()) * self.resolution()
        return start_m

    def start_year(self):
        start_y = self.specs['start']['date']['year']
        return start_y

    def month_year_start(self, i):
        start_m = self.adjusted_start_month()
        start_y = self.start_year()
        m = i * self.resolution() + start_m
        y = start_y + m / 12
        m = m % 12
        return (m, y)

    def month_year_end(self, i):
        start_m = self.adjusted_start_month()
        start_y = self.specs['start']['date']['year']
        m = ((i + 1) * self.resolution()) + start_m - 1
        y = start_y + m / 12
        m = m % 12
        return (m, y)

    def month_year_to_duration_ceiling(self, m, y):
        start_m = self.adjusted_start_month()
        start_y = self.start_year()
        dy = y - start_y
        dm = m - start_m
        d = dm + dy * 12
        return (d + self.resolution() - 1)/ self.resolution()

    def month_year_to_duration_floor(self, m, y):
        start_m = self.adjusted_start_month()
        start_y = self.start_year()
        dy = y - start_y
        dm = m - start_m
        d = dm + dy * 12
        return d / self.resolution()


    def month_str(self, d):
        if self.resolution() > 1:
            smonth = self.month_year_start(d)[0]
            emonth = self.month_year_end(d)[0]
            result = month_thai_short[smonth] + "-" + month_thai_short[emonth]
        else:
            month = self.month_year_start(d)[0]
            result = month_thai_short[month]
        return result

    def draw_header(self):
        duration = self.duration()
        mx = (duration) * self.x_fac
        print >>self.out, "<g transform=\"translate(%d,0)\">" % self.desc_len


        self.draw_months()
        self.draw_years()
        print >>self.out, "</g>"

    def draw_years(self):
        duration = self.duration()
        print >>self.out, "<g transform=\"translate(0,20)\">"
        y_ = None
        for d in range(duration):
            y = self.month_year_start(d)[1]
            if y_ != y:
                y_ = y
                print >>self.out, "<text x=\"%d\" y=\"0\">%d</text>" % (2 + d * self.x_fac, y)
        print >>self.out, "</g>"

    def draw_months(self):
        duration = self.duration()
        x = 0
        print >>self.out, "<g transform=\"translate(0,50)\">"
        for d in range(duration):
            print >>self.out, "<text x=\"%d\" y=\"0\">%s</text>" % (2 + d * self.x_fac, self.month_str(d))
        print >>self.out, "</g>"


    def draw_lines(self):
        duration = self.duration()
        mx = (duration) * self.x_fac + self.desc_len
        my = self.y_fac * (2 + len(self.activities()))
        print >>self.out, '<g stroke="black"><line x1="0" y1="' + '0' + '" x2="' + str(mx) + '" y2="' + '0' + '" stroke-width="1"/></g>'

        self.draw_line(self.desc_len,
                       self.y_fac,
                       self.desc_len + duration * self.x_fac,
                       self.y_fac)
        print >>self.out, '<g stroke="black"><line x1="0" y1="' + str(self.y_fac * 2) + '" x2="' + str(mx) + '" y2="' + str(self.y_fac * 2) + '" stroke-width="1"/></g>'

        self.draw_line(0, 0, 0, my)

        # year vertical line
        y_ = None
        for d in range(duration):
            y = self.month_year_start(d)[1]
            if y_ != y:
                y_ = y
                self.draw_line(self.desc_len + d * self.x_fac,
                               0,
                               self.desc_len + d * self.x_fac,
                               my)

        self.draw_line(self.desc_len + duration * self.x_fac,
                       0,
                       self.desc_len + duration * self.x_fac,
                       my)
                      

        ############ month veritcal line
        for d in range(duration):
            x = self.desc_len + d * self.x_fac
            self.draw_line(x, self.y_fac, x, my)
 


        #activity horizontal lines
        y = self.y_fac * 2
        for i, activity in enumerate(self.activities()):
            y += self.y_fac
            self.draw_line(0,
                       y,
                       self.desc_len + duration * self.x_fac,
                       y)

    def activities(self):
        return self.specs['activities']

    def draw_line(self, x1, y1, x2, y2):
        print >>self.out, "<g stroke=\"black\"><line x1=\"%d\" y1=\"%d\" x2=\"%d\" y2=\"%d\" stroke-width=\"1\"/></g>" % (x1, y1, x2, y2)

    def draw_desc(self):
        y = 30 
        print >>self.out, "<g transform=\"translate(5,%d)\">" % (self.y_fac * 2 - 10,)
        for i, activity in enumerate(self.activities()):
            desc = cgi.escape(activity['desc'])
            print >>self.out, "<text x=\"0\" y=\"%d\">%d. %s</text>" % (y, i+1, desc)
            y += self.y_fac 
        print >>self.out, "</g>"
        
def draw(specs, out):
    Drawer(out, specs)()
