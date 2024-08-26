import machine
from machine import Pin, PWM
import _thread
from time import sleep
import time
import network
from umqtt.simple import MQTTClient

MQTT_CLIENT_ID = "esp2"
MQTT_BROKER    = "broker.mqttdashboard.com"
MQTT_TOPIC     = "medidor_umidade"

print("Connecting to WiFi", end="")
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect('Wokwi-GUEST', '')
while not sta_if.isconnected():
    print(".", end="")
    sleep(0.1)
print(" Connected!")

print("Connecting to MQTT server... ", end="")
client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER)
client.connect()
print("Connected!")

buzzer = PWM(Pin(13), freq=1000)
led = Pin(2, Pin.OUT)
chave = Pin(12, Pin.IN, Pin.PULL_DOWN)

alarme_ativo = False

def tratar_mensagem(topic, msg):
    global alarme_ativo
    print("Mensagem recebida:", msg)
    if chave.value() == 0:  
        if msg == b"umidade baixa":
            alarme_ativo = True
        elif msg == b"umidade normalizada":
            alarme_ativo = False

client.set_callback(tratar_mensagem)
client.subscribe(MQTT_TOPIC)

def alarme():
    global alarme_ativo
    while True:
        if alarme_ativo:
            buzzer.duty(512) 
            led.on() 
            sleep(1)
            buzzer.duty(0)  
            led.off()  
            sleep(1)
        else:
            buzzer.duty(0)  
            led.off() 
        sleep(0.1)

_thread.start_new_thread(alarme, ())

try:
    while True:
        client.check_msg() 
        sleep(0.1)
except KeyboardInterrupt:
    print("Encerrando programa...")
finally:
    client.disconnect()
