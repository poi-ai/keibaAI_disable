![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/poi-ai/keibaAI)
![Lines of code](https://img.shields.io/tokei/lines/github/poi-ai/keibaAI)
![Relative date](https://img.shields.io/date/1640011380?label=first%20commit)
![GitHub last commit](https://img.shields.io/github/last-commit/poi-ai/keibaAI)
![GitHub commit activity](https://img.shields.io/github/commit-activity/m/poi-ai/keibaai)<br>
[![Twitter](img/twitter.png)](https://twitter.com/intent/tweet?text=poi-ai/keibaAI&url=https://github.com/poi-ai/keibaAI)
[![はてなブックマーク](img/hatebu.png)](https://b.hatena.ne.jp/entry/s/github.com/poi-ai/keibaAI)
[![Facebook](img/facebook.png)](https://www.facebook.com/sharer/sharer.php?u=https://github.com/poi-ai/keibaAI)

|項目|
| :--- |
| 1. [概要](#anchor1) |
| 2. [開発環境](#anchor2)|
| 3. [初期設定](#anchor3)|

<!--
| 4. [](#anchor4)|
| 5. [](#anchor5)| -->

<a id="anchor1"></a>
## 1. 概要
競馬AIを開発するプロジェクトです。

本リポジトリでは、データスクレイピングからクレンジング、モデル構築、予測まで一通りのソースコードを管理予定です。

実データは容量の都合上、本リポジトリでは扱わず、別の場所で管理を行なっております。

協力者募集中です。

<a id="anchor2"></a>
## 2. 開発環境

#### 使用言語
Python => 3.0

#### 使用ライブラリ
`requirements.txt`に記載

##### 動作確認環境
* Windows 10 [Core i7-1065G7, 16GB]
* CentOS 7   [さくらのVPS、1GBプラン]

<a id="anchor3"></a>
## 3. 初期設定
#### clone
```
$ git clone https://github.com/poi-ai/keibaAI.git
```

#### 外部ライブラリのインストール
```
$ pip install -r requirements.txt
```

#### 設定ファイル
coming soon...

<!--

## 3. データ
モデル作成に使用する大元となるデータは、netkeibaからスクレイピングを用いて取得しております。

スクレイピング済のcsvファイルは、サイズ的な問題でここに載せられないため、

`$ python src¥scraping¥netkeiba.py [開始日] [終了日]`

から

※開始日、終了日はyyyyMMddの形で入力してください。

* リアルタイムオッズデータ

稼働日当日の単勝・複勝オッズを記録、CSVファイルとして保存を行うプログラムです。

ソースコードの保管/起動場所はHeroku(無料の海外サーバー)、CSVの保管場所はGoogle Driveを想定しております。

`$ cd src¥scraping`

`$ python surveillance.py`

詳細は[Wiki](https://github.com/poi-ai/keibaAI/wiki)に書いていますので、そちらをご覧ください。

``
[]()
-->
