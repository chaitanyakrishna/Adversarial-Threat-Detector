# Adversarial-Threat-Detector
Adversarial Threat Detector (a.k.a. ATD) は、**ディープラーニングで構築された分類器の脆弱性を検知するためのスキャナー**です。  

ATDは「脆弱性の発見（Scanning & Detection）」→「開発者の脆弱性の理解（Understand）」→「脆弱性の修正（Fix）」→「修正確認（Re-Scanning）」のサイクルを回すことで、あなたのAIの安全確保に貢献します。  

<div align="center">
  <center>
  <img src="./img/atd_concept.jpg" width="400">
  <figcaption><b>ATDサイクル</b></figcaption>
  </center>
  <br>
</div>

|注意|
|:---|
|ATDの現バージョンは、`tf.keras`で構築された画像分類器にのみ対応しています。他の分類器は今後順次対応する予定です。|

#### 1. 脆弱性のスキャン・検知（Scanning & Detection）  
ATDは、**AIに対する様々な攻撃を全自動で実行し、脆弱性を検知**します。  

<div align="center">
  <center>
  <img src="./img/atd_scanning.png" width="800">
  <figcaption><b>脆弱性スキャン</b></figcaption>
  </center>
  <br>
</div>

脆弱性スキャン対象の分類器やデータセット、攻撃手法などを引数で指定するだけで、脆弱性の有無を検証することができます。  

#### 2. 脆弱性の理解（Understanding）  
脆弱性が検知された場合、ATDは**対策レポート（HTML）と脆弱性の再現環境（ipynb）を生成**します。  
開発者は、対策レポートと再現環境を参照することで、**脆弱性に関する理解を深めることができます**。  

* 対策レポート（HTML形式）  
<div align="center">
  <center>
  <img src="./img/scan_report_samples.png">
  <figcaption><b>HTML形式のレポート</b></figcaption>
  </center>
  <br>
</div>

検出された脆弱性の概要や対策を参照することで、脆弱性に対処する方法を知ることができます。  

* 脆弱性の再現環境（ipynb形式）  
<div align="center">
  <center>
  <img src="./img/ipynb_samples.png">
  <figcaption><b>Jupyter Notebook形式のレポート</b></figcaption>
  </center>
  <br>
</div>

ATDが自動生成したipynbをJupyter Notebookで読み込むことで、分類器に対する攻撃手順を一つずつ確認することができます。これにより、脆弱性を深く理解することができます。  

#### 3. 脆弱性の修正（Fix）  
ATDは、検知された**脆弱性を自動で修正**します。  

**※本機能は次期リリースで対応予定です。**  

#### 4. 修正確認（Re-Scanning）  
ATDは、脆弱性が修正されたAIに対し、修正確認の再スキャンを実行します。  

**※本機能は次期リリースで対応予定です。**  

## Road Map
ATDは１ヶ月おきに新機能をリリースしていく予定です。  
今後の開発スケジュールは以下の通りです。  

* 2021/01: 回避攻撃の実装（完了）  
* 2021/02: 抽出攻撃の実装  
* 2021/03: モデル汚染検知の実装  
* 2021/04: データ汚染検知の実装
* 2021/05: Keras以外への対応
* 2021/06~: 画像分類器以外への対応  

## Installation
1. ATDのリポジトリを`git clone`します。  
```
root@kali:~# git clone https://github.com/gyoisamurai/Adversarial-Threat-Detector
```

2. `pip3`をインストールします。  
```
root@kali:~# apt-get update
root@kali:~# apt-get install python3-pip
```

3. ATDの実行に必要なライブラリをインストールします。  
```
root@kali:~# cd Adversarial-Threat-Detector
root@kali:~/Adversarial-Threat-Detector# pip3 install -r requirements.txt
root@kali:~/Adversarial-Threat-Detector# apt install python3-tk
```

## Usage
ATDへの引数

|注意|
|:---|
|ATDの現バージョンは、回避攻撃にのみ対応しています。他の攻撃手法は今後対応する予定です。|

```
usage: atd.py [-h] [--model_name MODEL_NAME] [--dataset_name DATASET_NAME] [--use_dataset_num USE_DATASET_NUM] [--label_name LABEL_NAME]
              [--attack_type {all,data_poisoning,model_poisoning,evasion,exfiltration}] [--data_poisoning_method {fc,cp}] [--model_poisoning_method {node_injection,layer_injection}]
              [--evasion_method {all,fgsm,cnw,jsma}] [--exfiltration_method {mi,label_only,inversion}] [--lang {en,ja}]

Adversarial Threat Detector.

optional arguments:
  -h, --help            show this help message and exit
  --model_name MODEL_NAME
                        Target model name.
  --dataset_name DATASET_NAME
                        Dataset name.
  --use_dataset_num USE_DATASET_NUM
                        Dataset number for test.
  --label_name LABEL_NAME
                        Label name.
  --attack_type {all,data_poisoning,model_poisoning,evasion,exfiltration}
                        Specify attack type.
  --data_poisoning_method {fc,cp}
                        Specify method of Data Poisoning Attack.
  --model_poisoning_method {node_injection,layer_injection}
                        Specify method of Poisoning Attack.
  --evasion_method {all,fgsm,cnw,jsma}
                        Specify method of Evasion Attack.
  --exfiltration_method {mi,label_only,inversion}
                        Specify method of Exfiltration Attack.
  --lang {en,ja}        Specify language of report.
```

|パラメータ名|概要|
|:---|:---|
|model_name|脆弱性スキャン対象の学習済みモデルのファイル名を指定。ファイルは`targets`ディレクトリに配置。現在は`*.h5`形式にのみ対応。|
|dataset_name|脆弱性スキャンに必要なデータセットのファイル名を指定。ファイルは`targets`ディレクトリに配置。現在は`*.npz`形式にのみ対応。最低100個のデータが必要。|
|use_dataset_num|`dataset_name`で指定したデータセットのうち、脆弱性スキャンに使用するデータ数を指定。|
|label_name|脆弱性スキャンに必要なデータセットラベルのファイル名を指定。ファイルは`targets`ディレクトリに配置。現在は`*.npz`形式にのみ対応。|
|attack_type|`model_name`で指定した分類器に対する攻撃タイプを指定。現在は`evasion`のみ対応。|
|evasion_method|`attack_type`で`evasion`を指定した場合に使用。回避攻撃の手法を指定。|
|lang|レポートの言語を指定。デフォルトは`en`。|

### チュートリアル
#### 回避攻撃（FGSM）の実行
```
root@kali:~# python3 atd.py --model_name model.h5 --dataset_name X_test.npz --label_name y_test.npz --use_dataset_num 100 --attack_type evasion --evasion_method fgsm
```

#### 回避攻撃（C&W）の実行
```
root@kali:~# python3 atd.py --model_name model.h5 --dataset_name X_test.npz --label_name y_test.npz --use_dataset_num 100 --attack_type evasion --evasion_method cnw
```

#### 回避攻撃（JSMA）の実行
```
root@kali:~# python3 atd.py --model_name model.h5 --dataset_name X_test.npz --label_name y_test.npz --use_dataset_num 100 --attack_type evasion --evasion_method jsma
```

## Licence
[MIT License](https://github.com/gyoisamurai/Adversarial-Threat-Detector/blob/main/LICENSE)

## Contact us
* Email  
[gyoiler3@gmail.com](gyoiler3@gmail.com)  

* Twitter  
[https://twitter.com/bbr_bbq](https://twitter.com/bbr_bbq)  
