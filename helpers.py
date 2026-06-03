from datetime import datetime, date
import re

def format_kbbi_date(val):
    if not val:
        return ""
    tgl = None
    if isinstance(val, (datetime, date)):
        tgl = val
    else:
        val_str = str(val).strip()
        if not val_str or val_str == '-':
            return val_str
        
        formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M',
            '%d-%m-%Y %H:%M',
            '%d-%m-%Y %H:%M:%S',
            '%d/%m/%Y %H:%M',
            '%d/%m/%Y %H:%M:%S',
            '%Y-%m-%d',
            '%d-%m-%Y',
            '%d/%m/%Y'
        ]
        for fmt in formats:
            try:
                tgl = datetime.strptime(val_str, fmt)
                break
            except ValueError:
                continue
                
        if not tgl:
            month_map = {
                'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'mei': 5, 'may': 5, 'jun': 6, 'jul': 7,
                'agu': 8, 'aug': 8, 'agt': 8, 'sep': 9, 'okt': 10, 'oct': 10, 'nov': 11, 'des': 12, 'dec': 12,
                'januari': 1, 'februari': 2, 'maret': 3, 'april': 4, 'juni': 6, 'juli': 7, 'agustus': 8,
                'september': 9, 'oktober': 10, 'november': 11, 'desember': 12, 'january': 1, 'february': 2,
                'march': 3, 'june': 6, 'july': 7, 'august': 8, 'october': 10, 'december': 12
            }
            m = re.search(r'(\d{1,2})\s+([a-zA-Z]+)\s+(\d{4})(?:\s+(\d{1,2})[:\.](\d{1,2}))?', val_str)
            if m:
                day = int(m.group(1))
                mon_str = m.group(2).lower()
                year = int(m.group(3))
                hour = m.group(4)
                minute = m.group(5)
                if mon_str in month_map:
                    mon = month_map[mon_str]
                    if hour and minute:
                        tgl = datetime(year, mon, day, int(hour), int(minute))
                    else:
                        tgl = datetime(year, mon, day)
            
            if not tgl:
                return val_str

    has_time = False
    if isinstance(val, datetime):
        if val.hour != 0 or val.minute != 0 or val.second != 0:
            has_time = True
    elif isinstance(val, str):
        val_str = str(val).strip()
        if ' ' in val_str and (':' in val_str or '.' in val_str):
            has_time = True
            
    if has_time and hasattr(tgl, 'hour'):
        return tgl.strftime('%d-%m-%Y %H:%M')
    else:
        return tgl.strftime('%d-%m-%Y')

def formatRp(rupiah):
    try:
        rupiah = float(rupiah)
    except (ValueError, TypeError):
        return rupiah
    return "Rp {:,.0f}".format(rupiah).replace(",", ".") + ",00"
