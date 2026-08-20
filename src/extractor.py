import re
import jdatetime
from datetime import datetime

FA_TO_EN_MAP = str.maketrans('۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩', '01234567890123456789')

MONTHS_FA = {
    'فروردین': 1, 'اردیبهشت': 2, 'خرداد': 3, 'تیر': 4,
    'مرداد': 5, 'شهریور': 6, 'مهر': 7, 'آبان': 8,
    'آذر': 9, 'دی': 10, 'بهمن': 11, 'اسفند': 12
}

WORD_MILLIONS = {
    'یکمیلیون': 1000000, 'یک میلیون': 1000000, 'دومیلیون': 2000000, 'دو میلیون': 2000000,
    'سه میلیون': 3000000, 'چهار میلیون': 4000000, 'پنجمیلیون': 5000000, 'پنج میلیون': 5000000,
    'دهمیلیون': 10000000, 'ده میلیون': 10000000, 'نیم میلیون': 500000
}

def normalize_text(text: str) -> str:
    if not text:
        return ""
    text = text.translate(FA_TO_EN_MAP)
    text = text.replace('\u200c', ' ').replace('\xa0', ' ')
    return text

def parse_amount(text: str) -> int | None:
    if not text:
        return None

    norm_text = normalize_text(text).lower()

    for word_m, val in WORD_MILLIONS.items():
        if word_m in norm_text:
            return val

    m_million_thousand = re.search(
        r'(\d+(?:\.\d+)?)\s*(?:میلیون|ملیون|م)\s*(?:و|-|\+)?\s*(\d+(?:\.\d+)?)\s*(?:هزار)?\s*(تومان|تومن|ریال|ريال)?',
        norm_text
    )
    if m_million_thousand:
        m_val = float(m_million_thousand.group(1)) * 1_000_000
        k_val_str = m_million_thousand.group(2)
        k_val = float(k_val_str) if k_val_str else 0
        if 0 < k_val < 1000:
            k_val *= 1000
        res = int(m_val + k_val)
        unit = m_million_thousand.group(3)
        if unit in ['ریال', 'ريال'] or ('ریال' in norm_text and 'تومان' not in norm_text):
            res //= 10
        return res

    m_million = re.search(r'(\d+(?:\.\d+)?)\s*(?:میلیون|ملیون)\s*(تومان|تومن|ریال|ريال)?', norm_text)
    if m_million:
        res = int(float(m_million.group(1)) * 1_000_000)
        unit = m_million.group(2)
        if unit in ['ریال', 'ريال'] or ('ریال' in norm_text and 'تومان' not in norm_text):
            res //= 10
        return res

    m_thousand = re.search(r'(\d+(?:[,\./]\d{3})*|\d+)\s*هزار\s*(تومان|تومن|ریال|ريال)?', norm_text)
    if m_thousand:
        num_str = re.sub(r'[,\./]', '', m_thousand.group(1))
        val = int(num_str)
        if val >= 10000:
            res = val
        else:
            res = val * 1000
        unit = m_thousand.group(2)
        if unit in ['ریال', 'ريال'] or ('ریال' in norm_text and 'تومان' not in norm_text):
            res //= 10
        return res

    m_kw = re.search(r'(?:مبلغ|واریزی|شارژ|بابت)\s*[:\-]?\s*(\d{1,3}(?:[,\./]\d{3})+|\d+)\s*(تومان|تومن|ریال|ريال)?', norm_text)
    if m_kw:
        num_str = re.sub(r'[,\./]', '', m_kw.group(1))
        val = int(num_str)
        unit = m_kw.group(2)
        if val < 10000 and val > 0:
            val *= 1000
        if unit in ['ریال', 'ريال'] or ('ریال' in norm_text and 'تومان' not in norm_text):
            val //= 10
        return val

    m_unit = re.search(r'(\d{1,3}(?:[,\./]\d{3})+|\d+)\s*(تومان|تومن|ریال|ريال)', norm_text)
    if m_unit:
        num_str = re.sub(r'[,\./]', '', m_unit.group(1))
        val = int(num_str)
        unit = m_unit.group(2)
        if val < 10000 and val > 0:
            val *= 1000
        if unit in ['ریال', 'ريال']:
            val //= 10
        return val

    raw_nums = re.findall(r'\b(\d{1,3}(?:[,\./]\d{3})+|\d+)\b', norm_text)
    for num_s in raw_nums:
        clean = re.sub(r'[,\./]', '', num_s)
        if len(clean) in (16, 11) or (len(clean) == 8 and clean.startswith(('13', '14', '20'))):
            continue
        val = int(clean)
        if val >= 10000 and val <= 500000000:
            if 'ریال' in norm_text and 'تومان' not in norm_text:
                val //= 10
            return val
        elif 50 <= val < 10000:
            val *= 1000
            if 'ریال' in norm_text and 'تومان' not in norm_text:
                val //= 10
            return val

    return None

def parse_time(text: str) -> str | None:
    if not text:
        return None

    norm_text = normalize_text(text)

    # First look for time explicitly prefixed with keyword 'ساعت'
    kw_time_match = re.search(r'ساعت\s*[:\-]?\s*(\b[0-2]?\d)[:\./](\d{1,2})(?:[:\./]\d{1,2})?', norm_text)
    if kw_time_match:
        hh = int(kw_time_match.group(1))
        mm = int(kw_time_match.group(2))
        if 0 <= hh <= 23 and 0 <= mm <= 59:
            ctx = norm_text[max(0, kw_time_match.start()-20):min(len(norm_text), kw_time_match.end()+20)]
            if any(pm in ctx for pm in ['عصر', 'بعدازظهر', 'شب', 'بعد از ظهر', 'pm', 'PM']):
                if 1 <= hh <= 11:
                    hh += 12
            return f"{hh:02d}:{mm:02d}"

    # General HH:MM or HH.MM or HH/MM
    time_match = re.search(r'(\b[0-2]?\d)[:\./](\d{1,2})(?:[:\./]\d{1,2})?', norm_text)
    if time_match:
        hh = int(time_match.group(1))
        mm = int(time_match.group(2))

        # Ignore if it looks like date month/day or year digits
        if 0 <= hh <= 23 and 0 <= mm <= 59:
            ctx = norm_text[max(0, time_match.start()-20):min(len(norm_text), time_match.end()+20)]
            if any(pm in ctx for pm in ['عصر', 'بعدازظهر', 'شب', 'بعد از ظهر', 'pm', 'PM']):
                if 1 <= hh <= 11:
                    hh += 12
            return f"{hh:02d}:{mm:02d}"

    return None

def parse_date(text: str, ticket_posted_time: str | None = None) -> str | None:
    if not text:
        text = ""

    norm_text = normalize_text(text)

    full_date_match = re.search(r'\b(13\d{2}|14\d{2})[./;-](\d{1,2})[./;-](\d{1,2})\b', norm_text)
    if full_date_match:
        y, m, d = full_date_match.group(1), int(full_date_match.group(2)), int(full_date_match.group(3))
        return f"{y}/{m:02d}/{d:02d}"

    reverse_full_match = re.search(r'\b(\d{1,2})[./;-](\d{1,2})[./;-](13\d{2}|14\d{2})\b', norm_text)
    if reverse_full_match:
        d, m, y = int(reverse_full_match.group(1)), int(reverse_full_match.group(2)), reverse_full_match.group(3)
        return f"{y}/{m:02d}/{d:02d}"

    yy_date_match = re.search(r'\b(\d{2})[./;-](\d{1,2})[./;-](\d{1,2})\b', norm_text)
    if yy_date_match:
        yy, m, d = yy_date_match.group(1), int(yy_date_match.group(2)), int(yy_date_match.group(3))
        if 1 <= m <= 12 and 1 <= d <= 31:
            y = f"14{yy}" if len(yy) == 2 else yy
            return f"{y}/{m:02d}/{d:02d}"

    for m_name, m_num in MONTHS_FA.items():
        m_day_match = re.search(r'\b(\d{1,2})\s*' + m_name, norm_text)
        if m_day_match:
            d = int(m_day_match.group(1))
            y = "1405"
            if ticket_posted_time:
                p_parts = re.split(r'[./-]', ticket_posted_time.split('-')[0].strip())
                if len(p_parts) == 3 and len(p_parts[0]) == 2:
                    y = '14' + p_parts[0]
                elif len(p_parts) == 3 and len(p_parts[0]) == 4:
                    y = p_parts[0]
            return f"{y}/{m_num:02d}/{d:02d}"

    if ticket_posted_time:
        posted_date = ticket_posted_time.split('-')[0].strip()
        parts = re.split(r'[./-]', posted_date)
        if len(parts) == 3:
            y, m, d = parts[0], parts[1], parts[2]
            if len(y) == 2:
                y = '14' + y
            return f"{y}/{int(m):02d}/{int(d):02d}"

    return None

def parse_card_number(text: str) -> dict:
    result = {
        'source_card': None,
        'destination_card': None,
        'ambiguous_cards': []
    }
    if not text:
        return result

    norm_text = normalize_text(text)

    card_pattern = r'\b(\d{4}[- \n]?\d{4}[- \n]?\d{4}[- \n]?\d{4})\b'
    matches = list(re.finditer(card_pattern, norm_text))

    for match in matches:
        raw_card = match.group(1).replace('-', '').replace(' ', '').replace('\n', '')
        if len(raw_card) == 16 and raw_card.isdigit():
            start_pos = max(0, match.start() - 50)
            end_pos = min(len(norm_text), match.end() + 50)
            ctx = norm_text[start_pos:end_pos]

            is_src = any(kw in ctx for kw in ['از کارت', 'کارت خودم', 'کارت من', 'مبدا', 'مبدأ', 'از حساب', 'کارت مبدا'])
            is_dst = any(kw in ctx for kw in ['به کارت', 'به حساب', 'مقصد', 'کارت مقصد'])

            if is_src and not is_dst:
                if not result['source_card']:
                    result['source_card'] = raw_card
            elif is_dst and not is_src:
                if not result['destination_card']:
                    result['destination_card'] = raw_card
            else:
                result['ambiguous_cards'].append(raw_card)

    if not result['source_card'] and result['ambiguous_cards']:
        result['source_card'] = result['ambiguous_cards'].pop(0)
    if not result['destination_card'] and result['ambiguous_cards']:
        result['destination_card'] = result['ambiguous_cards'].pop(0)

    return result

def parse_gateway_and_names(text: str) -> dict:
    norm_text = normalize_text(text)

    gateway = "نامشخص"
    dest_name = None

    if any(kw in norm_text for kw in ['شاپرک', 'shaparak', 'درگاه مستقیم', 'درگاه اولی', 'درگاه اول']):
        gateway = "شاپرک"
    elif any(kw in norm_text for kw in ['کاسپین', 'caspian', 'درگاه پرسرعت']):
        gateway = "کاسپین"
    elif any(kw in norm_text for kw in ['کارت‌به‌کارت', 'کارت به کارت', 'kart be kart', 'کارت به کارت کردم', 'پل']):
        gateway = "کارت‌به‌کارت"

    name_match = re.search(r'(?:به\s*نام|بنام|به\s*اسم|صاحب\s*کارت\s*مقصد|به\s*حساب)\s*[:\-]?\s*(?:آقای|اقای|آقا|خانم)?\s*([\u0600-\u06FF\s]+)', norm_text)
    if name_match:
        raw_name = name_match.group(1).strip()
        clean_name = re.split(r'(?:واریز|انتقال|انجام|ممنون|ساعت|تاریخ|شماره|تیکت|خسته|سلام|نیامده|کردم|\d)', raw_name)[0].strip()
        if len(clean_name) >= 3:
            dest_name = clean_name

    if dest_name and gateway == "نامشخص":
        gateway = "کارت‌به‌کارت"

    return {
        'gateway': gateway,
        'destination_holder_name': dest_name
    }

def extract_financial_info(ticket_messages: list[dict], ticket_posted_time: str | None = None) -> dict:
    customer_texts = [
        msg.get('text', '') for msg in ticket_messages
        if msg.get('sender') == 'customer' and msg.get('text')
    ]
    full_text = "\n".join(customer_texts)

    amount = parse_amount(full_text)
    time_str = parse_time(full_text)
    date_str = parse_date(full_text, ticket_posted_time=ticket_posted_time)
    cards = parse_card_number(full_text)
    gw_info = parse_gateway_and_names(full_text)

    return {
        'amount_toman': amount,
        'time': time_str,
        'date': date_str,
        'source_card': cards['source_card'],
        'destination_card': cards['destination_card'],
        'destination_holder_name': gw_info['destination_holder_name'],
        'gateway': gw_info['gateway'],
        'deposit_type': 'شارژ حساب'
    }
