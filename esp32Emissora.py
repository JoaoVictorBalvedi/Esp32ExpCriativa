import machine
from machine import Pin, PWM
import _thread
from time import sleep
import time
import dht
import network
from umqtt.simple import MQTTClient

MQTT_CLIENT_ID = "esp1"
MQTT_BROKER    = "broker.mqttdashboard.com"
MQTT_USER      = ""
MQTT_PASSWORD  = ""
MQTT_TOPIC    = "medidor_umidade"

print("Connecting to WiFi", end="")
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect('Wokwi-GUEST', '')
while not sta_if.isconnected():
    print(".", end="")
    sleep(0.1)
print(" Connected!")

print("Connecting to MQTT server... ", end="")
client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, user=MQTT_USER, password=MQTT_PASSWORD)
client.connect()

print("Connected!")

sensor1 = dht.DHT22(machine.Pin(16))
sensor2 = dht.DHT22(machine.Pin(4))
servo1 = PWM(Pin(18), freq=50)
servo2 = PWM(Pin(19), freq=50)
chave = Pin(12, Pin.IN, Pin.PULL_DOWN)

umidade_baixa = False

def calcular_duty(angulo):
    """Calcula o valor do duty para o ângulo desejado."""
    return int((angulo / 180.0) * 1023)

def monitorar_sensor1():
    global umidade_baixa
    while True:
        if chave.value() == 0:
            try:
                sensor1.measure()
                temp = sensor1.temperature()
                umidade = sensor1.humidity()
                
                print(f"Sensor 1 - Temperatura: {temp}°C, Umidade: {umidade}%")

                if temp >= 60:
                    print("Temperatura alta no sensor 1! Abrindo comporta 1 em 50°")
                    servo1.duty(calcular_duty(50))  # Abrir servo 1 em 50°
                else:
                    print("Temperatura normal no sensor 1.")
                    servo1.duty(calcular_duty(0))  # Fechar servo 1

                if umidade < 20:
                    if not umidade_baixa:
                        print("Umidade baixa detectada no sensor 1! Enviando alerta...")
                        enviar_alerta("umidade baixa")
                        umidade_baixa = True
                else:
                    if umidade_baixa:
                        print("Umidade normalizada no sensor 1! Enviando alerta de normalização...")
                        enviar_alerta("umidade normalizada")
                        umidade_baixa = False
            except Exception as e:
                print("Erro ao ler sensor 1:", e)
        else:
            print("Chave desativada. Fechando comporta 1")
            servo1.duty(calcular_duty(0))  # Fechar servo 1
        time.sleep(2)

def monitorar_sensor2():
    global umidade_baixa
    while True:
        if chave.value() == 0:
            try:
                sensor2.measure()
                temperatura = sensor2.temperature()
                umidade = sensor2.humidity()
                
                print(f"Sensor 2 - Temperatura: {temperatura}°C, Umidade: {umidade}%")

                if temperatura >= 60:
                    print("Temperatura alta no sensor 2! Abrindo comporta 2 em 180°")
                    servo2.duty(calcular_duty(180))  # Abrir servo 2 em 180°
                else:
                    print("Temperatura normal no sensor 2.")
                    servo2.duty(calcular_duty(0))  # Fechar servo 2

                if umidade < 20:
                    if not umidade_baixa:
                        print("Umidade baixa detectada no sensor 2! Enviando alerta...")
                        enviar_alerta("umidade baixa")
                        umidade_baixa = True
                else:
                    if umidade_baixa:
                        print("Umidade normalizada no sensor 2! Enviando alerta de normalização...")
                        enviar_alerta("umidade normalizada")
                        umidade_baixa = False
            except Exception as e:
                print("Erro ao ler sensor 2:", e)
        else:
            print("Chave desativada. Fechando comporta 2")
            servo2.duty(calcular_duty(0))  # Fechar servo 2
        time.sleep(2)

def enviar_alerta(tipo_alerta):
    try:
        mensagem = f"{tipo_alerta}"
        client.publish(MQTT_TOPIC, mensagem)
        print(f"Alerta enviado: {mensagem}")
    except Exception as e:
        print("Erro ao enviar alerta:", e)

_thread.start_new_thread(monitorar_sensor1, ())
_thread.start_new_thread(monitorar_sensor2, ())

while True:
    sleep(10)
