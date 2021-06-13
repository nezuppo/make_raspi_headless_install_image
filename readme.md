# はじめに

ラズパイ OS をヘッドレスでインストールできるよう、ansible を使ってインストールイメージファイルに以下の変更を加えます。

<br/>

boot パーティション

- ssh サービスが有効になるように ssh という名前の空ファイルを設置

root パーティション

- 無線 LAN が有効になるように ``etc/wpa_supplicant/wpa_supplicant.conf`` に SSID とパスワード関連のネットワーク情報を追記

  - ラズパイ OS の仕様上、インストールイメージの boot パーティションに wpa_supplicant.conf を置けば ``etc/wpa_supplicant/wpa_supplicant.conf`` が置き換わる仕様となっているようですが、本スクリプトでは ansible が ``etc/wpa_supplicant/wpa_supplicant.conf`` を直接編集します。

- 無線 LAN インターフェースに固定 IP アドレスが振られるように ``etc/dhcpcd.conf`` に無線 LAN インターフェスの IP アドレス関連の情報を追記

<br/>

# 実施する手順

- 手動で Raspberry Pi のサイトからラズパイ OS のインストールイメージファイルをダウンロード
- 手動で wpa_supplicant.conf に追記する情報が書かれたファイル ``tmp/wpa_supplicant_network`` を用意
- 手動で dhcpcd.conf に追記する情報が書かれたファイル ``tmp/dhcpcd_wlan0`` を用意
- ansible-playbook コマンドを実行

<br/>

以下、具体的な手順です。 windows10 の wsl で実施します。

<br/>

# ラズパイ OS のインストールイメージファイルをダウンロード

[本家ラズパイのサイト](https://www.raspberrypi.org/) からラズパイのインストールイメージ (例: 2021-05-07-raspios-buster-armhf-lite.zip) をダウンロードし、zipped-original-image/ ディレクトリに置く

<br/>

# wpa_supplicant.conf に追記する SSID、パスワード関連のネットワーク情報が書かれたファイルを用意

wpa_passphrase コマンドが使えるように wpasupplicant コマンドをインストール

```
$ sudo apt install wpasupplicant
```

<br/>

``etc/wpa_supplicant/wpa_supplicant.conf`` に追記する内容が書かれた wpa_supplicant_network ファイルを用意

```
$ wpa_passphrase MY_SSID > tmp/wpa_supplicant_network
```

- MY_SSID は実際の WiFi 環境の SSID を指定
- コマンドを実行すると入力待ちの状態になるので SSID のパスワードを入力してリターンキーを押す

<br/>

``tmp/wpa_supplicant_network`` の中身は以下のようになりました。

```
# reading passphrase from stdin
network={
        ssid="MY_SSID"
        #psk="nantokakantokapassword"
        psk=f53105d1b5a1e3562c9726422127310547cdda57ae765204f6734b27b99d7a72
}
```

<br/>

コメントは不要で、かつパスワードが平文で見えてしまっているので削除して以下のように修正

```

network={
        ssid="MY_SSID"
        psk=f53105d1b5a1e3562c9726422127310547cdda57ae765204f6734b27b99d7a72
}
```

<br/>

# dhcpcd.conf に追記する無線 LAN インターフェスの IP アドレス関連の情報が書かれたファイルを用意

``tmp/dhcpcd_wlan0`` を以下のような内容で用意します。この内容が ``etc/dhcpcd.conf`` の最後に追記されます。

```

interface wlan0
static ip_address=192.168.0.1/24
static routers=192.168.0.254
static domain_name_servers=192.168.0.253 192.168.0.252
```

<br/>

# ansible-playbook コマンドを実行

```
$ ansible-playbook --ask-become-pass -i local, ./playbook.yml
```

- ``BECOME password`` というプロンプトで sudo パスワードを聞いてくるので入力してリターンキーを押す

一応、冪等性は担保されています。

ansible-playbook が正常終了すると tmp/unzipped/ ディレクトリにヘッドレスインストール用のイメージファイル (例: 2021-05-07-raspios-buster-armhf-lite.img) が出来ています。

```
$ ls -l tmp/unzipped/
total 1830912
-rwxrwxrwx 1 worker worker 1874853888 Jun 12 21:56 2021-05-07-raspios-buster-armhf-lite.img
```

このイメージを MicroSD カードに焼いてラズパイを起動すると、無線 LAN に割り当てた IP アドレスでラズパイに ssh することができます。

<br/>

<span style="color: red; ">ssh は外部からの不正侵入に使われる恐れがあるので、インストールが完了したらすぐに pi ユーザーのパスワードを変更して下さい。</span>

<br/>

# ansible-playbook コマンドがエラーとなった場合

ansible-playbook コマンドが途中でエラーとなった場合はエラーが起きた状況により以下の状態になっている場合があります。

- インストールイメージの boot、root パーティションがマウントされたまま (ansible-playbook 正常終了時はマウントが解除されている)
- インストールイメージが loopback デバイスに割り当てられたまま (ansible-playbook 正常終了時は loopback デバイスへの割り当ては解除されている)

エラーを解消した後、再度 ansible-playbook コマンドを実行して正常終了できれば上記の途中の状態は解除されます。(マウントは解除され、loopback デバイスの割り当ても解除された状態で終了となる)

正常終了させず中断する場合は mount コマンドでマウントされたパーティションを確認して手動でアンマウントして下さい。
その後、lsblk コマンドで割り当てられた loopback デバイスを確認して losetup コマンドで割り当て解除して下さい。
