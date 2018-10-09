from requests import get
from scapy.all import IP, sr1
import json

def get_API_token():
    with open('settings.json', 'r') as infile:
        token = json.load(infile)
        return token['APItoken']

def get_ip_data(ip_addr):
    token = get_API_token()
    resp = get('https://ipinfo.io/{}?token={}'.format(ip_addr, token))
    if resp.status_code == 200:
        return resp.content
    else:
        print('An error occured. Status code: {}'.format(resp.status_code))

def trace_route():
    hostname = 'dnb.no'
    for i in range(1, 10):
        pkt = IP(dst=hostname, ttl=i)

        # # UPD port necessary?
        resp = sr1(pkt, verbose=0, timeout=1) # verbose makes the function silent
        # print(resp.summary)
        # print(resp.show())

        if resp is None:
            print('resp is None: {}'.format(resp))
            break
        elif resp.type == 3:
            # Dst reached
            print('Dst reached: {}'.format(resp.src))
            
            ip_data = get_ip_data(resp.src)
            print(ip_data)
        else:
            # Keep going
            print('{} hops away. IP addr: {}'.format(i, resp.src))

            ip_data = get_ip_data(resp.src)
            print(ip_data)


if __name__ == '__main__':  
    trace_route()

