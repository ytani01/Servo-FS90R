# Servo-FS90R
連続回転サーボモーター RS90R

## Shopping
秋月電子通商 [３６０°連続回転サーボ（ローテーションサーボ）　ＦＳ９０Ｒ](http://akizukidenshi.com/catalog/g/gM-13206/)

## Raspberry Pi の Python でサーボを制御する方法

従来は、WiringPiかRPi.GPIOが主流だったが、それぞれ利点・欠点があり、用途に応じて使い分ける必要があった。
pigpioは、デーモンを利用するのが特徴で、柔軟で高度なGPIO制御をシンプルに行うことができる。
 
### WiringPi

ハードウェアPWMが利用でき、高精度で軽い。
ただし、ファームウェアの違いで動かないことがある。

### RPi.GPIO

ソフトウェアPWMをサポートしているが精度が悪い。
割り込み処理など、PWM以外のGPIO制御機能が充実している。

### pigpio

GPIOライブラリの決定版!?
デーモン「pigpiod」を起動するという一手間が必要だが、手軽に高度なGPIO制御ができる。
ソフトウェアだが、高精度で柔軟なPWM制御をサポート。
ほとんどのピン(0..31)でPWMが可能になる。
サーボモーターを制御する場合など、複雑な初期設定(クロックや周波数などの設定)をほとんど省くことができる。
コールバック関数による割り込み制御、ネットワーク経由のGPIO制御など機能が豊富。


## 基本的な利用方法

```python
#!/usr/env/bin python3

import pigpio

pi = pigpio.pi()

# pin2: 0 .. 31
pi.set_mode(pin, pigpio.OUTPUT)

# pulse_width: 500 .. 1500 .. 2500
pi.set_servo_pulsewidth(pin, pulse_width)

# stop servo
pi.set_servo_pulsewidth(pin, 0)

pi.stop()
```
