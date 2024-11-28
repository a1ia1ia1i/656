import socket
from dnslib import DNSRecord, RR, QTYPE, A
import dns.resolver

def query_google_dns(domain):
    """
    Query Google Public DNS for a domain's A record.
    :param domain: The domain to query.
    :return: A list of IP addresses if found, None otherwise.
    """
    try:
        resolver = dns.resolver.Resolver()
        resolver.nameservers = ['8.8.8.8']  # Google DNS server
        answer = resolver.resolve(domain, 'A')
        return [ip.to_text() for ip in answer]
    except Exception as e:
        print(f"Google DNS query failed for {domain}: {e}")
        return None

def handle_dns_query(data, addr, sock):
    """
    Handle an incoming DNS query, using only public DNS resolution.
    :param data: The raw DNS query data.
    :param addr: The address of the client.
    :param sock: The server socket.
    """
    try:
        # Parse the incoming DNS query
        dns_record = DNSRecord.parse(data)
        query_name = str(dns_record.q.qname)
        query_type = QTYPE[dns_record.q.qtype]

        print(f"Received DNS query: {query_name} ({query_type}) from {addr}")

        # Query Google Public DNS
        google_ips = query_google_dns(query_name)
        query_ip = google_ips[0] if google_ips else None

        # Create the DNS response
        reply = dns_record.reply()
        if query_ip:
            reply.add_answer(RR(query_name, QTYPE.A, rdata=A(query_ip)))
            print(f"Replied with IP: {query_ip}")
        else:
            print(f"No record found for {query_name}")

        # Send the response
        sock.sendto(reply.pack(), addr)
    except Exception as e:
        print(f"Error handling query: {e}")

def start_dns_server():
    """
    Start the DNS server to handle incoming queries.
    """
    DNS_HOST = "0.0.0.0"  # Listen on all interfaces
    DNS_PORT = 53  # Standard DNS port

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((DNS_HOST, DNS_PORT))
    print(f"DNS server listening on {DNS_HOST}:{DNS_PORT}")

    while True:
        data, addr = sock.recvfrom(512)  # DNS packet size limit is 512 bytes
        handle_dns_query(data, addr, sock)

if __name__ == "__main__":
    start_dns_server()
