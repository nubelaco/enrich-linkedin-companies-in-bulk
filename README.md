# Bulk Enrich Linkdein Companies

A script commissioned (and with permission, open-sourced) by TVC Capital.

This script takes in a batc

## Setup

1. `$ poetry install`
2. Update the following variables in `tvc.py`
    * `PROXYCURL_API_KEY`


## Use

`$ poetry run python3 tvc.py`

## Notes

* A blank row with nothing but the Linkedin Company URL represents an invalid profile that cannot be scraped.
* `Employee Count` is an array representing a range of employees. For example, `[1,10]` means 1-10 employees.
* Increase `WORKER_COUNT` if you want the script to faster.
* Requires Python 3