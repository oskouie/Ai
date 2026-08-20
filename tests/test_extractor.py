import pytest
from src.extractor import extract_financial_info, parse_amount, parse_time, parse_date, parse_card_number, parse_gateway_and_names

def test_parse_amount():
    assert parse_amount("مبلغ یکمیلیون تومان") == 1000000
    assert parse_amount("مبلغ ۵۰۰ هزار تومان") == 500000
    assert parse_amount("واریزی 500000هزارتومان") == 500000
    assert parse_amount("۵۰۰۰000 ریال") == 500000
    assert parse_amount("شارژ 1.5 میلیون تومان") == 1500000
    assert parse_amount("500بهحساب") == 500000

def test_parse_time():
    assert parse_time("ساعت 16:08") == "16:08"
    assert parse_time("ساعت 9:15 شب") == "21:15"
    assert parse_time("ساعت 21.57.24") == "21:57"
    assert parse_time("10.5 عصر") == "22:05"

def test_parse_date():
    assert parse_date("تاریخ 1405/05/28") == "2026/08/19"
    assert parse_date("الان شارژ کردم", ticket_posted_time="20.08.26 - 01:53") == "2026/08/20"

def test_parse_card_number():
    res = parse_card_number("از کارت 6063731265272212 به کارت 5894631252177365")
    assert res['source_card'] == "6063731265272212"
    assert res['destination_card'] == "5894631252177365"

def test_parse_gateway():
    res1 = parse_gateway_and_names("از طریق شاپرک واریز کردم")
    assert res1['gateway'] == "شاپرک"

    res2 = parse_gateway_and_names("به نام آقای محمد سهرابی واریز شد")
    assert res2['gateway'] == "کارت‌به‌کارت"
    assert "محمد" in res2['destination_holder_name']

def test_full_extraction():
    ticket_msgs = [
        {"sender": "customer", "text": "سلام مبلغ 500 هزار تومان ساعت 14:20 به نام محمد سهرابی واریز کردم از کارت 6037991786315824"}
    ]
    extracted = extract_financial_info(ticket_msgs, ticket_posted_time="20.08.26 - 01:53")
    assert extracted['amount_toman'] == 500000
    assert extracted['time'] == "14:20"
    assert extracted['source_card'] == "6037991786315824"
    assert extracted['destination_holder_name'] is not None
    assert extracted['gateway'] == "کارت‌به‌کارت"
