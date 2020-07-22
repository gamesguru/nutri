#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 18 16:16:08 2020

@author: shane
"""

import csv

from tabulate import tabulate

from .utils import remote


def list_nutrients():
    response = remote.request("/nutrients")
    results = response.json()["data"]

    table = tabulate(results, headers="keys", tablefmt="presto")
    print(table)
    return table


def sort_foods_by_nutrient_id(id):
    response = remote.request("/foods/sort", params={"nutr_id": id})
    results = response.json()["data"]

    table = tabulate(results, headers="keys", tablefmt="presto")
    print(table)
    return table


def sort_foods_by_kcal_nutrient_id(id):
    pass


def day_analyze(day_csv, rda_csv=None):
    day_csv_input = csv.DictReader(day_csv)

    log = []
    for row in day_csv_input:
        log.append(row)

    rda = []
    if rda_csv:
        rda_csv_input = csv.DictReader(rda_csv)
        for row in rda_csv_input:
            rda.append(row)

    response = remote.request("/day/analyze", body={"log": log, "rda": rda})
    results = response.json()["data"]

    totals = results["nutrient_totals"]
    print(totals)
