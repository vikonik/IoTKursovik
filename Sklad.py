'''
Отправку данных делаем в отдельном потоке
'''
import sys  # sys нужен для передачи argv в QApplication
from PyQt5 import QtWidgets, QtCore
import ui_GUISklad  # Это наш конвертированный файл дизайна

import paho.mqtt.client as mqtt  # mqtt paho
import json  # json converter

class ExampleApp(QtWidgets.QMainWindow, ui_GUISklad.Ui_MainWindow):
    def __init__(self):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        super().__init__()
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна

        self.slider_temperatureIn.valueChanged.connect(self.sliderCangeTemperatureIn)
        self.slider_temperatureIn.sliderReleased.connect(self.sendSliderCangeTemperatureIn)    

        self.slider_humidityIn.valueChanged.connect(self.sliderCangeHumidityeIn)
        self.slider_humidityIn.sliderReleased.connect(self.sendSliderCangeHumidityIn)

        self.verticalSlider_barrierSwitsh.valueChanged.connect(self.sliderCangeBarrier)
        self.verticalSlider_barrierSwitsh.sliderReleased.connect(self.sendSliderCahngeBarrier)      

        #Выделение газов
        self.spinBox_argon.valueChanged.connect(self.spinboxChangeArgon)        #Аргон
        self.spinBox_azot.valueChanged.connect(self.spinboxChangeAzot)          #Азот
        self.spinBox_heli.valueChanged.connect(self.spinboxChangeHeli)          #Гелий
        self.spinBox_vodorod.valueChanged.connect(self.spinboxChangeVodorod)    #Водород
        self.spinBox_CO2.valueChanged.connect(self.spinboxChangeCO2)            #Углекислый газ
        self.spinBox_CO.valueChanged.connect(self.spinboxChangeCO)              #Угарный газ
        self.spinBox_O2.valueChanged.connect(self.spinboxChangeO2)              #Кислород

        self.spinBox_weight.valueChanged.connect(self.spinboxChangeWeight)      #Масса 
    #Объявляем переменные для класса
        self.temperatureIn = 0
        self.temperatureOut = 0
        self.humidityIn = 0
        self.humidityOut = 0
        self.conditionerState = False
        self.speed = 0
        self.lat = 57.343773782603854  # Текущая координата устройства
        self.lon = 28.34066446324784  # Текущая координата устройства
        self.choke = 0
        self.suddenBraking = 0  #аварийное торможеие
        self.gassArgon = 0
        self.gassAzot = 0
        self.gassGeli = 0
        self.gassVodorod = 0
        self.gassCO2 = 0    #Углекислый
        self.gassCO = 0     #Угарный
        self.gassO2 = 0
        self.weight = 0
        self.barrier = False
        self.tt = 0
    #Пороги включения и выключения кондиционера
        self.conditionerPorogOn = 0
        self.conditionerPorogOff = 0
    #Топики    
        # отправляемое сообщеие
        self.topic_data = "data/state"  # текущее состояние
        # принимаемые команды
        self.topic_barrierCmd = "command/barrier"  # Команда на управление шлакбаумом
        self.topic_conditionerCmd = "command/conditioner"  # Команда на управление кондиционером

        self.mqtt_client = init("mqtt-vikonik-sklad")#mqtt-vikonik-Truck

        #Подпишимся на топик
        self.mqtt_client.subscribe(self.topic_barrierCmd)
        self.mqtt_client.message_callback_add(self.topic_barrierCmd, self.command_barrierCmd)

        self.mqtt_client.subscribe(self.topic_conditionerCmd)
        self.mqtt_client.message_callback_add(self.topic_conditionerCmd, self.command_conditionerCmd)


        #Подключаемся к клиенту

        run(self.mqtt_client)

        self.label_barrierState.setStyleSheet("background-color: red")


#Температура внутри
# Отправляем новые данные после отпускаиня слайдера
    def sendSliderCangeTemperatureIn(self):
        self.temperatureIn = self.slider_temperatureIn.value()
        self.label_temperatureIn.setText(str(self.temperatureIn))
        publish_data(self.mqtt_client,self.topic_data,self.get_data())
        #self.checkConditioner()

# Отображаем новые данные без отправки
    def sliderCangeTemperatureIn(self, value):
        self.temperatureIn = value
        self.label_temperatureIn.setText(str(value))


# Влажность внутри
# Отправляем новые данные после отпускаиня слайдера
    def sendSliderCangeHumidityIn(self):
        self.humidityIn = self.slider_humidityIn.value()
        self.label_humidityIn.setText(str(self.humidityIn))
        publish_data(self.mqtt_client,self.topic_data,self.get_data())

# Отображаем новые данные без отправки
    def sliderCangeHumidityeIn(self, value):
        self.humidityIn = value
        self.label_humidityIn.setText(str(value))  

# Шлакбаум
# Отправляем новые данные после отпускаиня слайдера
    def sendSliderCahngeBarrier(self):
        if self.verticalSlider_barrierSwitsh.value() == 1:
            self.barrier = True
        else:
            self.barrier = False 
        #self.label_barrierState.setText(str(self.barrier))
        publish_data(self.mqtt_client,self.topic_data,self.get_data())

# Отображаем новые данные без отправки
    def sliderCangeBarrier(self, value):
        if value == 1:
            self.barrier = True
        else:
            self.barrier = False 
            
        if self.barrier == True:
            self.label_barrierState.setText("Откр.")  
            self.label_barrierState.setStyleSheet("background-color: green")
        else:
            self.label_barrierState.setText("Закр.") 
            self.label_barrierState.setStyleSheet("background-color: red")
        publish_data(self.mqtt_client,self.topic_data,self.get_data())


#Выделение газов
#Аргон
    def spinboxChangeArgon(self):
        self.gassArgon = self.spinBox_argon.value()
        publish_data(self.mqtt_client,self.topic_data,self.get_data())

#Азот
    def spinboxChangeAzot(self):
        self.gassAzot = self.spinBox_azot.value()
        publish_data(self.mqtt_client,self.topic_data,self.get_data())

#Гелий
    def spinboxChangeHeli(self):
        self.gassGeli = self.spinBox_heli.value()
        publish_data(self.mqtt_client,self.topic_data,self.get_data())

#Водород
    def spinboxChangeVodorod(self):
        self.gassVodorod= self.spinBox_vodorod.value()
        publish_data(self.mqtt_client,self.topic_data,self.get_data())

#Углекислый газ
    def spinboxChangeCO2(self):
        self.gassCO2= self.spinBox_CO2.value()
        publish_data(self.mqtt_client,self.topic_data,self.get_data())

#Угарный газ
    def spinboxChangeCO(self):
        self.gassCO= self.spinBox_CO.value()
        publish_data(self.mqtt_client,self.topic_data,self.get_data())
#Кислород
    def spinboxChangeO2(self):
        self.gassO2= self.spinBox_O2.value()
        publish_data(self.mqtt_client,self.topic_data,self.get_data())

#Масса
    def spinboxChangeWeight(self):
        self.weight= self.spinBox_weight.value()
        publish_data(self.mqtt_client,self.topic_data,self.get_data())


    # Формируем данные для отправки
    def get_data(self):
        data = json.dumps({
            "pos":{
                "lat": self.lat,
                "lon": self.lon
            },
            "humidity":{
                "humidityIn":  self.humidityIn, 
                "humidityOut": self.humidityOut
            },
            "temperature":{
                "temperatureIn":  self.temperatureIn, 
                "temperatureOut": self.temperatureOut
            },
            "speed": self.speed,  # скорость
            "conditionerState": self.conditionerState,
            "weight": self.weight,
            "choke": self.choke,
            "suddenBraking":self.suddenBraking,
            "gass":{
                "gassArgon":self.gassArgon,
                "gassAzot":self.gassAzot,
                "gassGeli":self.gassGeli,
                "gassVodorod":self.gassVodorod,
                "gassCO2":self.gassCO2,
                "gassCO":self.gassCO,
                "gassO2":self.gassO2,
                "weight":self.weight          
            },
            "barrier": self.barrier
        })
        return data

#Команда на управление шлакбаумом
    def command_barrierCmd(self, client, userdata, message):
        print("CMD: changeBarrierState, value: %s" % message.payload)
        try:
            self.barrier  = bool(message.payload)
            print(self.barrier )
            if self.barrier == True:
                self.label_barrierState.setText("Откр.")  
                self.label_barrierState.setStyleSheet("background-color: green")
                self.verticalSlider_barrierSwitsh.setValue(1)
            if self.barrier == False:
                self.label_barrierState.setText("Закр.")  
                self.label_barrierState.setStyleSheet("background-color: red")  
                self.verticalSlider_barrierSwitsh.setValue(0)
        except:
            print("can't change staste to %s" % message.payload)

#Команда на управление кондиционером
    def command_conditionerCmd(self, client, userdata, message):
        print("CMD: changeConditionerState, value: %s" % message.payload)
        try:
            self.conditionerState  = bool(message.payload)
            print(self.barrier )
            if self.conditionerState == True:
                self.label_conditionerState.setText("Вкл.")  
                self.label_conditionerState.setStyleSheet("background-color: green")
            if self.conditionerState == False:
                self.label_conditionerState.setText("Откл.")  
                self.label_conditionerState.setStyleSheet("background-color: red")  
        except:
            print("can't change staste to %s" % message.payload)




#***********************************************************************************************************************
# Инициализация mqtt
def init(clientid, clientUsername="", clientPassword=""):
    client = mqtt.Client(client_id=clientid)
    client.on_connect = on_connect
    client.on_message = on_message
    client.username_pw_set(username=clientUsername, password=clientPassword)
    return client

# connect reaction
def on_connect(client, userdata, flags, rc):
    print("Connected with result code %s" % str(rc))
    if rc == 0:
        isConnect = 1
        client.publish("connect", "true", 1)
    if rc == 5:
        print("Authorization error")

# default message reaction
def on_message(client, userdata, message):
    print("Some message received topic: %s, payload: %s" %
          (message.topic, message.payload))

# connect to server
def publish_data(client, topic, data):
    print(topic, data)
    return client.publish(topic, data)


def run(client, host="dev.rightech.io", port=1883):
    client.connect(host, port, 60)
    client.loop_start()


print("Start GIU")
app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
window = ExampleApp()  # Создаём объект класса ExampleApp
window.show()  # Показываем окно
print("OK")
app.exec_()  # и запускаем приложение        