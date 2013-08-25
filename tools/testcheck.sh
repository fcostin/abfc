#! /usr/bin/env bash
((diff -q $1 $2) && (echo "PASS" > $3)) || (echo "FAIL" > $3)
