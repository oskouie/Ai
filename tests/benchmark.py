import json
import time
import sys
from collections import Counter
from src.extractor import extract_financial_info

def run_benchmark():
    file_path = '/app/data/tickets.json'
    print(f"Loading benchmark dataset from {file_path}...")

    start_time = time.time()
    with open(file_path, 'r', encoding='utf-8') as f:
        tickets = json.load(f)
    load_time = time.time() - start_time
    print(f"Loaded {len(tickets)} tickets in {load_time:.2f} seconds.")

    extracted_stats = Counter()
    extracted_tickets = 0
    total_tickets = len(tickets)

    parse_start = time.time()

    for ticket in tickets:
        msgs = ticket.get('messages', [])
        posted_time = ticket.get('ticketPostedTime')

        info = extract_financial_info(msgs, ticket_posted_time=posted_time)

        has_any = False
        if info['amount_toman'] is not None:
            extracted_stats['amount'] += 1
            has_any = True
        if info['time'] is not None:
            extracted_stats['time'] += 1
            has_any = True
        if info['date'] is not None:
            extracted_stats['date'] += 1
            has_any = True
        if info['source_card'] is not None:
            extracted_stats['source_card'] += 1
            has_any = True
        if info['destination_holder_name'] is not None:
            extracted_stats['destination_holder_name'] += 1
            has_any = True
        if info['gateway'] != 'نامشخص':
            extracted_stats['gateway'] += 1
            has_any = True

        if has_any:
            extracted_tickets += 1

    total_parse_time = time.time() - parse_start
    avg_speed_ms = (total_parse_time / total_tickets) * 1000

    print("\n" + "="*50)
    print("      BENCHMARK RESULTS & EXTRACTION STATISTICS     ")
    print("="*50)
    print(f"Total Tickets Processed     : {total_tickets}")
    print(f"Total Tickets with Financial Data Found : {extracted_tickets} ({extracted_tickets/total_tickets*100:.2f}%)")
    print(f"Total Time Taken            : {total_parse_time:.2f} seconds")
    print(f"Average Speed per Ticket    : {avg_speed_ms:.2f} ms")
    print("-" * 50)
    print(f"Amounts Extracted           : {extracted_stats['amount']} ({extracted_stats['amount']/total_tickets*100:.2f}%)")
    print(f"Times Extracted             : {extracted_stats['time']} ({extracted_stats['time']/total_tickets*100:.2f}%)")
    print(f"Dates Extracted             : {extracted_stats['date']} ({extracted_stats['date']/total_tickets*100:.2f}%)")
    print(f"Source Cards Extracted      : {extracted_stats['source_card']} ({extracted_stats['source_card']/total_tickets*100:.2f}%)")
    print(f"Dest Names Extracted        : {extracted_stats['destination_holder_name']} ({extracted_stats['destination_holder_name']/total_tickets*100:.2f}%)")
    print(f"Gateways Classified        : {extracted_stats['gateway']} ({extracted_stats['gateway']/total_tickets*100:.2f}%)")
    print("="*50 + "\n")

if __name__ == "__main__":
    run_benchmark()
