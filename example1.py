#!/usr/bin/env python3
"""
Reads and prints data from COVID-19 daily csv files from
    https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_daily_reports

To use this script, first clone the COVID-19 data repo into the same directory
as this script is in:

    git clone https://github.com/CSSEGISandData/COVID-19

Then run this script:

    python3 ./example1.py --county Whatcom --state WA --country US

If you've cloned the CSSEGISandData/COVID-19 repo to a different location than the
same directory this script is in, you can set with the --data-repo-dir argument.
"""
import argparse
import csv
import glob


def get_files_in_date_order(data_repo_dir):
    reports_dir = data_repo_dir + '/csse_covid_19_data/csse_covid_19_daily_reports'

    # The file format before 3/22 did not contain county-level data but instead
    # only state-level data. So, only look at files from 3/22 onward.
    file_list = glob.glob(reports_dir + '/03-2[2-9]-2020.csv')
    file_list += glob.glob(reports_dir + '/03-3[0-1]-2020.csv')
    file_list += glob.glob(reports_dir + '/04-*-2020.csv')
    file_list.sort()

    return file_list


def get_file_date(path):
    filename = path.split('/')[-1]
    before_dot = filename.split('.')[0]
    return before_dot


def get_records(combined_key, data_repo_dir):
    records = []

    prev_confirmed = 0
    prev_deaths = 0
    prev_recovered = 0
    prev_active = 0

    for filepath in get_files_in_date_order(data_repo_dir):
        rec = {}
        records.append(rec)

        rec['date'] = get_file_date(filepath)

        with open(filepath) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['Combined_Key'] != combined_key:
                    continue

                rec['confirmed'] = int(row['Confirmed'])
                rec['deaths'] = int(row['Deaths'])
                rec['recovered'] = int(row['Recovered'])
                rec['active'] = int(row['Active'])

                rec['new_confirmed'] = rec['confirmed'] - prev_confirmed
                rec['new_deaths'] = rec['deaths'] - prev_deaths
                rec['new_recovered'] = rec['recovered'] - prev_recovered
                rec['new_active'] = rec['active'] - prev_active

                prev_confirmed = rec['confirmed']
                prev_deaths = rec['deaths']
                prev_recovered = rec['recovered']
                prev_active = rec['active']

    # Drop the first record since the "new" counts won't be accurate as
    # they will start out with the total so far in the first record.
    return records[1:]


def print_raw(records):
    for record in records:
        print(record)


def print_histogram(records, key):
    for rec in records:
        print(rec['date'], end='')
        print('\t', end='')
        print('| ', end='')
        print('#' * rec[key])


def main(county, state, country, data_repo_dir):
    combined_key = f'{county}, {state}, {country}'

    print('*' * 80)
    print(f'Location: {combined_key}')
    print('*' * 80)

    records = get_records(combined_key, data_repo_dir)

    print()
    print('Raw')
    print('-' * 40)
    print_raw(records)

    print()
    print('Confirmed')
    print('-' * 40)
    print_histogram(records, key='new_confirmed')

    print()
    print('Deaths')
    print('-' * 40)
    print_histogram(records, key='new_deaths')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--county', default='Whatcom')
    parser.add_argument('--state', default='Washington')
    parser.add_argument('--country', default='US')
    parser.add_argument('--data-repo-dir', default='COVID-19')

    args = parser.parse_args()
    main(args.county, args.state, args.country, args.data_repo_dir)
