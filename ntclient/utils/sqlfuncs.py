#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug  4 21:23:47 2020

@author: shane
"""

import os
import sqlite3

from . import verify_db

verify_db()

# Connect to DB
db_path = os.path.expanduser("~/.nutra/nutra.db")
conn = sqlite3.connect(db_path)
# conn.row_factory = sqlite3.Row  # see: https://chrisostrouchov.com/post/python_sqlite/
c = conn.cursor()


def _sql(query):
    """Executes a SQL command to nutra.db"""
    result = c.execute(query)
    keys = [x[0] for x in result.description]
    return keys, result.fetchall()


# ----------------------
# SQL syntax functions
# ----------------------


def nutrients():
    """Nutrient details"""
    query = """
SELECT
  id,
  nutr_desc,
  rda,
  unit,
  tagname,
  anti_nutrient,
  COUNT(nut_data.nutr_id) AS food_count,
  ROUND(avg(nut_data.nutr_val), 3) AS avg_val
FROM
  nutr_def
  INNER JOIN nut_data ON nut_data.nutr_id = id
GROUP BY
  id
ORDER BY
  id;
"""
    return _sql(query)


def servings(food_ids=["None"]):
    """Food servings"""
    # TODO: apply connective logic from `sort_foods()` IS ('None') ?
    food_ids = ",".join([str(x) for x in set(food_ids)])
    query = """
SELECT
  serv.food_id,
  serv.msre_id,
  serv_desc.msre_desc,
  serv.grams
FROM
  serving serv
  LEFT JOIN serv_desc ON serv.msre_id = serv_desc.id
WHERE
  serv.food_id IN ({0}) OR '{0}' IS 'None';
"""
    return _sql(query.format(food_ids))


def analyze_foods(food_ids_in):
    """Nutrient analysis for foods"""
    food_ids_in = ", ".join(str(x) for x in set(food_ids_in))
    query = """
SELECT
  id,
  nutr_id,
  nutr_val
FROM
  food_des des
  INNER JOIN nut_data ON des.id = nut_data.food_id
WHERE
  des.id IN (%s);
"""
    return _sql(query % food_ids_in)


def food_details(food_ids_in):
    """Readable human details for foods"""
    food_ids_in = ", ".join(str(x) for x in set(food_ids_in))
    query = "SELECT * FROM food_des WHERE id in (%s)"
    return _sql(query % food_ids_in)


def sort_foods(nutr_id, fdgrp_id_in=["'None'"]):
    """Sort foods by nutr_id per 100 g"""
    fdgrp_ids = ",".join([str(x) for x in set(fdgrp_id_in)])
    query = """
SELECT
  nut_data.food_id,
  fdgrp_id,
  nut_data.nutr_val,
  kcal.nutr_val AS kcal,
  long_desc
FROM
  nut_data
  INNER JOIN food_des food ON food.id = nut_data.food_id
  INNER JOIN nutr_def ndef ON ndef.id = nut_data.nutr_id
  INNER JOIN fdgrp ON fdgrp.id = fdgrp_id
  LEFT JOIN nut_data kcal ON food.id = kcal.food_id
    AND kcal.nutr_id = 208
WHERE
  nut_data.nutr_id = {0}
  -- filter by food id, if supplied
  AND (fdgrp_id IN ({1})
    OR ({1}) IS ('None'))
ORDER BY
  nut_data.nutr_val DESC;
"""
    return _sql(query.format(nutr_id, fdgrp_ids))


def sort_foods_by_kcal(nutr_id, fdgrp_id_in=["'None'"]):
    """Sort foods by nutr_id per 200 kcal"""
    fdgrp_ids = ",".join([str(x) for x in set(fdgrp_id_in)])
    query = """
SELECT
  nut_data.food_id,
  fdgrp_id,
  ROUND((nut_data.nutr_val * 200 / kcal.nutr_val), 2),
  kcal.nutr_val,
  long_desc
FROM
  nut_data
  INNER JOIN food_des food ON food.id = nut_data.food_id
  INNER JOIN nutr_def ndef ON ndef.id = nut_data.nutr_id
  INNER JOIN fdgrp ON fdgrp.id = fdgrp_id
  -- filter out NULL kcal
  INNER JOIN nut_data kcal ON food.id = kcal.food_id
    AND kcal.nutr_id = 208
    AND kcal.nutr_val > 0
WHERE
  nut_data.nutr_id = {0}
  -- filter by food id, if supplied
  AND (fdgrp_id IN ({1})
    OR ({1}) IS ('None'))
ORDER BY
  (nut_data.nutr_val / kcal.nutr_val) DESC;
"""
    return _sql(query.format(nutr_id, fdgrp_ids))
