#!/bin/bash

python src/main/app/voucher_data_preparation.py

uvicorn src.main.api.voucher_api:app
