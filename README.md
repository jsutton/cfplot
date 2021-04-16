# cfplot

## Overview

It was increasingly cumbersome to eye-grep CF output in the AWS console. I couldn't find another tool out there to provide individual resource deployment time so I wrote this. Please use at your own risk. No warranties expressed or implied.

## Requirements

* An AWS profile configured locally
* python 3.8+
* pipenv

## Installation

```bash
pipenv install
pipenv shell
./cfplot.py --help
```

## Example

```bash
./cfplot.py stackname --region us-east-1 --profile your-profile-name
```
