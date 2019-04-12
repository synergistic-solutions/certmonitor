import requests
import base64
import re

class Parser:

    def get_entries(self, ct, start, amount):
        url = 'https://' + ct + 'ct/v1/get-entries?start=' + str(start) + '&end=' + str(start + amount)

        domains = set()

        try:
            resp = requests.get(url=url, timeout=3)
        except requests.exceptions.ConnectTimeout or requests.exceptions.ReadTimeout:
            return domains

        if resp.status_code != 200:
            return domains

        data = resp.json()

        if not data or not data['entries']:
            return domains

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

                if new_decoded not in domains:
                    domains.add(new_decoded)

        return domains
