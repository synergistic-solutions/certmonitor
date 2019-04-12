import requests
import base64
import re

url = 'https://www.gstatic.com/ct/log_list/all_logs_list.json'

resp = requests.get(url=url)
data = resp.json()


operators = {}
for operator in data['operators']:
    operators[operator['id']] = operator['name']

logs = {}
for log in data['logs']:
    logs[log['url']] = log['description']  # [operators[log['operated_by'][0]]

print(logs)

working = {}

count = 0
certs = set()
for url, name in logs.items():
    count += 1
    print(count, '/', len(logs))
    print(url, name)

    if count in list(range(46, 59)):
        continue

    new_url = 'https://' + url + 'ct/v1/get-sth'
    try:
        resp = requests.get(url=new_url)
        data = resp.json()
        num = data['tree_size']
    except:
        continue

    new_url = 'https://' + url + 'ct/v1/get-entries?start=' + str(num-1024) + '&end=' + str(num)

    try:
        resp = requests.get(url=new_url)
    except:
        continue

    if resp.status_code != 200:
        continue
    print("parsing")
    working[url] = name
    data = resp.json()

    if not data or not data['entries']:
        continue

    for entry in data['entries']:

        leaf_input = base64.b64decode(entry['leaf_input'])

        for i in leaf_input.split(b'\x82'):

            if not i:
                continue

            length = i[0]
            i = i[1:length + 1]

            if b'.' not in i or b' ' in i:
                continue

            decoded = i.decode("ascii", 'ignore').strip()
            if len(decoded) != len(i) or len(decoded) < 4:
                continue

            new_decoded = re.sub("[^a-z0-9.*-]+", "", decoded, flags=re.IGNORECASE)

            new_decoded = new_decoded.replace('*.', '').strip()

            if new_decoded not in certs:
                certs.add(new_decoded)

    print(len(certs))


with open('domains.txt', 'a') as the_file:
    the_file.write('\n'.join(certs))
print(working)