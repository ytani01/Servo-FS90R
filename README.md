# Servo-FS90R
連続回転サーボモーター RS90R

## Shopping
[３６０°連続回転サーボ（ローテーションサーボ）　ＦＳ９０Ｒ](http://akizukidenshi.com/catalog/g/gM-13206/)

## Raspberry Pi の Python でサーボを制御する方法

従来は、WiringPiかRPi.GPIOが主流だったが、それぞれ利点・欠点があり、用途に応じて使い分ける必要があった。
pigpioは、デーモンを利用するのが特徴で、柔軟で高度なGPIO制御をシンプルに行うことができる。
 
### WiringPi

ハードウェアPWMがりようできるため、高精度で軽い。
ファームウェアのバージョンの違いで動かないことがある。

### RPi.GPIO

ソフトウェアPWMをサポートしているが、制度が悪い。
割り込み処理など、PWM以外のGPIOの操作が充実している。

### pigpio

GPIOライブラリの決定版!?
デーモン「pigpiod」を起動するという一手間が必要だが、手軽に高度なGPIO制御ができる。
ソフトウェアだが、高精度で柔軟なPWM制御をサポート。
ほとんどのピンでPWMが可能になる。
サーボモーターを制御する場合など、複雑な初期設定(クロックや周波数などの設定)をほとんど省くことができる。
コールバック関数による割り込み制御、ネットワーク経由のGPIO制御など機能が豊富。


## 基本的な利用方法

```python
#!/usr/env/bin python3

import pigpio

pi = pigpio.pi()

pi.set_mode(pin1, pigpio.INPUT)
pi.set_mode(pin2, pigpio.OUTPUT)

pi.set_servo_pulsewidth(pin2, pulse_width)
# pin2: 0 .. 31
# pulse_width: 500 .. 1500 .. 2500
```
