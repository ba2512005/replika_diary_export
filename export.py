import os
import json
import requests
from urllib.parse import urljoin
import asyncio


class ReplikaDiaryExport:
    def __init__(self, headers=None, out_dir='./export'):
        headers = {
            'X-AUTH-TOKEN': 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
            'X-USER-ID': 'XXXXXXXXXXXXXXXXXXXXXXXX',
            'X-DEVICE-ID': 'XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX',
            'X-TIMESTAMP-HASH': 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
        }
        self.headers = headers
        self.out_dir = out_dir
        self.init_out_dir()

    def init_out_dir(self):
        print('Initializing output directory...')
        if not os.path.exists(self.out_dir):
            os.makedirs(self.out_dir)
        if not os.path.exists(os.path.join(self.out_dir, 'images')):
            os.makedirs(os.path.join(self.out_dir, 'images'))
        print('Output directory initialized.')

    async def get_diary_entries(self, offset, limit):
        print(f'Fetching diary entries with offset {offset} and limit {limit}...')
        url = f'https://my.replika.com/api/mobile/1.4/saved_chat_items/previews?t=diary&offset={offset}&limit={limit}'
        response = requests.get(url, headers=self.headers)
        data = response.json()
        print(f'Fetched {len(data)} diary entries.')
        return data

    async def get_all_diary_entries(self):
        print('Fetching all diary entries...')
        offset = 0
        limit = 100
        entries = []
        while True:
            data = await self.get_diary_entries(offset, limit)
            if not data:
                break
            entries.extend(data)
            offset += limit
        print(f'Fetched a total of {len(entries)} diary entries.')
        return entries

    async def get_diary_entries_details(self, entries):
        print('Fetching diary entry details...')
        url = 'https://my.replika.com/api/mobile/1.4/saved_chat_items/actions/get_by_ids'
        data = {'ids': [entry['id'] for entry in entries]}
        response = requests.post(url, headers=self.headers, json=data)
        data = response.json()
        print('Fetched diary entry details.')
        return data

    async def export(self):
        print('Exporting diary...')
        all_diary_entries = await self.get_all_diary_entries()
        all_with_details = await self.get_diary_entries_details(all_diary_entries)
        with open(os.path.join(self.out_dir, 'diary.json'), 'w') as f:
            json.dump(all_with_details, f, indent=2)
        print('Exported diary to diary.json.')
        for entry in all_with_details:
            if 'image_url' in entry and entry['image_url'] is not None:
                print(f'Downloading image for entry {entry["id"]}...')
                response = requests.get(entry['image_url'])
                with open(os.path.join(self.out_dir, 'images', f'{entry["id"]}.jpg'), 'wb') as f:
                    f.write(response.content)
                print(f'Downloaded image for entry {entry["id"]}.')
        print('Export complete.')

if __name__ == '__main__':
    replika_diary_export = ReplikaDiaryExport()
    print('Calling export method...')
    asyncio.run(replika_diary_export.export())
    print('Export method called.')
