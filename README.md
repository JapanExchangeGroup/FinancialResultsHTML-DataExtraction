# 決算短信セグメント情報のデータ抽出ハンズオン

[![Source Code Check](https://github.com/JapanExchangeGroup/FinancialResultsHTML-DataExtraction/actions/workflows/ci.yml/badge.svg)](https://github.com/JapanExchangeGroup/FinancialResultsHTML-DataExtraction/actions/workflows/ci.yml)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Code style: flake8](https://img.shields.io/badge/code%20style-flake8-black)](https://github.com/PyCQA/flake8)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![Typing: mypy](https://img.shields.io/badge/typing-mypy-blue)](https://github.com/python/mypy)


HTML 化された決算短信から、セグメント情報を抽出する方法が学べるハンズオンです。

![top.jpg](notebooks/images/top.jpg)

HTML 化された決算短信は、[適時開示情報閲覧サービス](https://www.release.tdnet.info/inbs/I_main_00.html)か、[東証上場会社情報サービス](https://www.jpx.co.jp/listing/co-search/index.html)から取得できます。データを取得し、セグメント情報を抽出する方法はハンズオン資料を参照してください。

## ハンズオンコンテンツ

1. HTML から情報を抽出する方法を学ぶ [![Open in SageMaker Studio Lab](https://studiolab.sagemaker.aws/studiolab.svg)](https://studiolab.sagemaker.aws/import/github/JapanExchangeGroup/FinancialResultsHTML-DataExtraction/blob/main/notebooks/01_how_to_extract_from_html.ipynb)
   * HTML とは
   * Python による HTML からの情報抽出
   * Exercise1: 目的の HTML 要素を検索する
   * Exercise2: 目的の HTML 要素へ移動する
2. HTML 化された決算短信からセグメント情報を抽出する方法を学ぶ  [![Open in SageMaker Studio Lab](https://studiolab.sagemaker.aws/studiolab.svg)](https://studiolab.sagemaker.aws/import/github/JapanExchangeGroup/FinancialResultsHTML-DataExtraction/blob/main/notebooks/02_how_to_extract_segment_data_from_html.ipynb)
   * HTML 化された決算短信とは
   * Exercies1: 決算短信 HTML ファイルからセグメント情報を抽出する
   * Exercies2: セグメント情報の抽出が失敗する理由を分析する

※本ハンズオンはあらゆる企業の HTML からセグメント情報が抽出できるプログラムを提供するものではありません。抽出が失敗する理由を理解し、修正箇所を特定できる技能を身に着けることを目的としています。

## ハンズオンの進め方

Amazon SageMaker Studio Lab を使用し簡単に始めることができます。ハンズオンのはじめ方は、 [ハンズオンの進め方](docs/README_usage.md)を参照してください。

ハンズオンは2部構成を想定して作られています。

* Day1: ハンズオンコンテンツを実施し、HTMLから情報を抽出する方法を身に着ける。宿題として興味ある企業からセグメント情報の抽出を試み、HomeworkTemplateに記載する。
* Day2: Homeworkの共有を行う。読み取り結果の統計を参照しながら、発行体に促すべき記載の方式についてディスカッションする。
   * 決算短信HTMLの読み取り可否状況レポート [![Open in SageMaker Studio Lab](https://studiolab.sagemaker.aws/studiolab.svg)](https://studiolab.sagemaker.aws/import/github/JapanExchangeGroup/FinancialResultsHTML-DataExtraction/blob/main/notebooks/a1_financial_result_to_dataframe.ipynb)
