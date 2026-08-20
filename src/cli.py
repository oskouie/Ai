import argparse
import json
import sys
from src.extractor import extract_financial_info

def main():
    parser = argparse.ArgumentParser(description="Financial Ticket Parsing AI CLI")
    parser.add_argument("--text", type=str, help="Single text prompt to analyze")
    parser.add_argument("--file", type=str, help="JSON file containing tickets")
    parser.add_argument("--ticket-id", type=str, help="Specific ticket ID in JSON file")

    args = parser.parse_args()

    if args.text:
        msgs = [{"sender": "customer", "text": args.text}]
        res = extract_financial_info(msgs)
        print(json.dumps(res, ensure_ascii=False, indent=2))
    elif args.file:
        with open(args.file, 'r', encoding='utf-8') as f:
            tickets = json.load(f)

        if args.ticket_id:
            ticket = next((t for t in tickets if str(t.get('id')) == str(args.ticket_id)), None)
            if not ticket:
                print(f"Ticket ID {args.ticket_id} not found.")
                sys.exit(1)
            res = extract_financial_info(ticket.get('messages', []), ticket_posted_time=ticket.get('ticketPostedTime'))
            print(json.dumps(res, ensure_ascii=False, indent=2))
        else:
            print(f"Loaded {len(tickets)} tickets.")
            sample = tickets[0]
            res = extract_financial_info(sample.get('messages', []), ticket_posted_time=sample.get('ticketPostedTime'))
            print(f"Sample extraction for ticket {sample.get('id')}:")
            print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
