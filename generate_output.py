import json
import time
from src.extractor import extract_financial_info

def generate_all_outputs():
    input_file = '/app/data/tickets.json'
    output_file = '/app/parsed_tickets_output.json'

    print(f"Loading dataset from {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        tickets = json.load(f)

    print(f"Processing {len(tickets)} tickets...")
    start_time = time.time()
    results = []

    for idx, ticket in enumerate(tickets, 1):
        t_id = ticket.get('id')
        user_id = ticket.get('userId')
        posted_time = ticket.get('ticketPostedTime')
        msgs = ticket.get('messages', [])

        # Extract financial info
        extracted = extract_financial_info(msgs, ticket_posted_time=posted_time)

        # Build output structure
        results.append({
            "ticket_id": t_id,
            "user_id": user_id,
            "ticket_posted_time": posted_time,
            "parsed_financial_data": extracted,
            "raw_customer_messages": [m.get('text') for m in msgs if m.get('sender') == 'customer']
        })

    total_time = time.time() - start_time
    print(f"Extraction completed in {total_time:.2f} seconds.")

    print(f"Saving output to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"Done! Saved {len(results)} parsed tickets to {output_file}.")

if __name__ == "__main__":
    generate_all_outputs()
