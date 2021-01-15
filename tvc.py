import asyncio
from asyncio.protocols import DatagramProtocol
import csv
import sys
from pprint import pprint
from typing import List

import httpx

PROXYCURL_HOST = "https://nubela.co/proxycurl"
PROXYCURL_API_KEY = "TODO - YOUR API KEY" # todo <--- FILL IN YOUR PROXYCURL API KEY HERE
PROXYCURL_XHR_DEFAULT_TIMEOUT = 100
WORKER_COUNT = 100
INPUT_FILE = 'input.csv' # a csv file containing a list of Linkedin Companies
OUTPUT_FILE = 'output.csv'
EXCEPTION_RETRY_COUNT = 3


async def get_coy_profile(url: str) -> dict:
    last_exc = Exception()
    for _ in range(EXCEPTION_RETRY_COUNT):
        try:
            print(f"Enriching {url}")
            api_endpoint = f'{PROXYCURL_HOST}/api/linkedin/company'
            header_dic = {'Authorization': 'Bearer ' + PROXYCURL_API_KEY}
            async with httpx.AsyncClient() as client:
                params = {'url': url}
                resp = await client.get(api_endpoint,
                                        params=params,
                                        headers=header_dic,
                                        timeout=PROXYCURL_XHR_DEFAULT_TIMEOUT
                                        )
                if resp.status_code == 404:
                    return None  # invalid company
                assert resp.status_code == 200
                return resp.json()

        except KeyboardInterrupt:
            sys.exit()
        except Exception as exc:
            last_exc = exc

    raise last_exc


async def company_q_consumer(q: asyncio.Queue, result_lis: List):
    while not q.empty():
        linkedin_url = await q.get()
        try:
            company_data = await get_coy_profile(linkedin_url)
            result_lis += [[linkedin_url, company_data]]
        except Exception:
            print(f"Cannot enrich {linkedin_url}.")
            pass


def populate_queue(q):
    with open(INPUT_FILE, 'r') as f:
        csv_reader = csv.reader(f)
        for idx, row in enumerate(csv_reader):
            print(f"{idx+1}: Adding {row[0]} to work queue")
            q.put_nowait(row[0])


def main():
    async def run():
        q = asyncio.Queue()
        populate_queue(q)

        results = []
        worker_lis = [company_q_consumer(q, results)
                      for _ in range(WORKER_COUNT)]
        await asyncio.gather(*worker_lis)

        with open(OUTPUT_FILE, 'w') as f:
            writer = csv.writer(f)
            header = ['Linkedin URL', 'Website', 'Company Name',
                      'Employee Count', 'Follower Count']
            data = [[row[0],
                    row[1]['website'] if row[1] is not None else '',
                    row[1]['name'] if row[1] is not None else '',
                    row[1]['company_size'] if row[1] is not None else '',
                    row[1]['follower_count'] if row[1] is not None else '',
                    ] for row in results]
            writer.writerows([header] + data)
        print(f"Done. Check {OUTPUT_FILE}")

    asyncio.run(run())

main()
