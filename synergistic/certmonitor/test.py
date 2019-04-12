import requests
import base64
import re


def cert(leaf):
    certs = []
    for i in leaf.split(b'\x82'):

        if not i:
            continue

        length = i[0]
        i = i[1:length+1]

        if b'.' not in i or b' ' in i:
            continue

        decoded = i.decode("ascii", 'ignore').strip()
        if len(decoded) != len(i) or len(decoded) < 4:
            continue

        new_decoded = re.sub("[^a-z0-9.*-]+", "", decoded, flags=re.IGNORECASE)

        if new_decoded not in certs:
            certs.append(new_decoded)

    return certs


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


count = 0
for url, name in logs.items():
    count += 1
    print(count, '/', len(logs))
    print(url, name)

    new_url = 'https://' + url + 'ct/v1/get-sth'
    try:
        resp = requests.get(url=new_url, timeout=1)
    except:
        continue

    if True:
        data = resp.json()
        num = data['tree_size']
        #print(num)
        new_url = 'https://' + url + 'ct/v1/get-entries?start=' + str(num-1024) + '&end=' + str(num)

        try:
            resp = requests.get(url=new_url, timeout=1)
        except:
            continue

        if resp.status_code != 200:
            continue

        data = resp.json()

        if not data or not data['entries']:
            continue

        certs = []
        for entry in data['entries']:

            leaf_input = base64.b64decode(entry['leaf_input'])
            #extra_data = base64.b64decode(entry["extra_data"])
            certs += cert(leaf_input)

        print(len(certs))
        with open('domains.txt', 'a') as the_file:
            the_file.write('\n'.join(certs))


