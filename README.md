# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/cal-itp/littlepay/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                |    Stmts |     Miss |   Branch |   BrPart |   Cover |   Missing |
|------------------------------------ | -------: | -------: | -------: | -------: | ------: | --------: |
| littlepay/\_\_init\_\_.py           |        5 |        2 |        0 |        0 |     60% |       5-7 |
| littlepay/api/\_\_init\_\_.py       |       40 |        6 |        6 |        0 |     87% |73, 90, 105, 118, 138, 157 |
| littlepay/api/card\_tokenization.py |       10 |        0 |        0 |        0 |    100% |           |
| littlepay/api/client.py             |       83 |        0 |       12 |        0 |    100% |           |
| littlepay/api/funding\_sources.py   |       68 |        0 |       10 |        0 |    100% |           |
| littlepay/api/groups.py             |       67 |        0 |       10 |        0 |    100% |           |
| littlepay/api/products.py           |       46 |        0 |        8 |        0 |    100% |           |
| littlepay/commands/\_\_init\_\_.py  |        7 |        0 |        0 |        0 |    100% |           |
| littlepay/commands/configure.py     |       34 |        0 |       10 |        0 |    100% |           |
| littlepay/commands/groups.py        |      140 |        0 |       50 |        0 |    100% |           |
| littlepay/commands/products.py      |       38 |        0 |       20 |        0 |    100% |           |
| littlepay/commands/switch.py        |       11 |        0 |        6 |        1 |     94% |    13->16 |
| littlepay/config.py                 |       97 |        0 |       24 |        0 |    100% |           |
| littlepay/main.py                   |       65 |        1 |       10 |        1 |     97% |       137 |
|                           **TOTAL** |  **711** |    **9** |  **166** |    **2** | **99%** |           |


## Setup coverage badge

Below are examples of the badges you can use in your main branch `README` file.

### Direct image

[![Coverage badge](https://raw.githubusercontent.com/cal-itp/littlepay/python-coverage-comment-action-data/badge.svg)](https://htmlpreview.github.io/?https://github.com/cal-itp/littlepay/blob/python-coverage-comment-action-data/htmlcov/index.html)

This is the one to use if your repository is private or if you don't want to customize anything.

### [Shields.io](https://shields.io) Json Endpoint

[![Coverage badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/cal-itp/littlepay/python-coverage-comment-action-data/endpoint.json)](https://htmlpreview.github.io/?https://github.com/cal-itp/littlepay/blob/python-coverage-comment-action-data/htmlcov/index.html)

Using this one will allow you to [customize](https://shields.io/endpoint) the look of your badge.
It won't work with private repositories. It won't be refreshed more than once per five minutes.

### [Shields.io](https://shields.io) Dynamic Badge

[![Coverage badge](https://img.shields.io/badge/dynamic/json?color=brightgreen&label=coverage&query=%24.message&url=https%3A%2F%2Fraw.githubusercontent.com%2Fcal-itp%2Flittlepay%2Fpython-coverage-comment-action-data%2Fendpoint.json)](https://htmlpreview.github.io/?https://github.com/cal-itp/littlepay/blob/python-coverage-comment-action-data/htmlcov/index.html)

This one will always be the same color. It won't work for private repos. I'm not even sure why we included it.

## What is that?

This branch is part of the
[python-coverage-comment-action](https://github.com/marketplace/actions/python-coverage-comment)
GitHub Action. All the files in this branch are automatically generated and may be
overwritten at any moment.