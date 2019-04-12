import requests

from synergistic import poller, broker, certmonitor, resolver

broker_client = broker.Client("127.0.0.1", 8891, broker.Type.WEBAPP)

parser = certmonitor.Parser()

def get():
    url = 'https://www.gstatic.com/ct/log_list/all_logs_list.json'

    resp = requests.get(url=url)
    data = resp.json()
    print(data)
    operators = {}
    for operator in data['operators']:
        operators[operator['id']] = operator['name']

    logs = {}
    for log in data['logs']:
        logs[log['url']] = log['description']  # [operators[log['operated_by'][0]]

    for log, name in logs.items():
        print("trying:", log)

        for i in range(10):
            domains = parser.get_entries(log, 10000 + i * 1000, 1000)
            print(domains)
            print(len(domains))
            domains = list(domains)
            for domain in domains:
                broker_client.publish('resolve', {'hostname': domain, 'type': resolver.dns.Type.A})


def trigger(channel, msg_id, payload):
    get()


if __name__ == "__main__":
    poller = poller.Poll(catch_errors=False)

    poller.add_client(broker_client)
    broker_client.subscribe('trigger.certmonitor', trigger)
    get()
    poller.serve_forever()
