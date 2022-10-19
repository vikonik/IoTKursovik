'''
Отправку данных делаем в отдельном потоке
'''
import sys  # sys нужен для передачи argv в QApplication
from time import sleep  # sys нужен для передачи argv в QApplication
from PyQt5 import QtWidgets, QtCore
import ui_GUISklad  # Это наш конвертированный файл дизайна

import paho.mqtt.client as mqtt  # mqtt paho
import json  # json converter
import threading

sendWenChange = False #Отправка пакета при изменении состояния ползунка

modeAuto = "modeAuto"
modeManual = "modeManual"

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

        self.slider_air.valueChanged.connect(self.sliderCangeAir)
        self.slider_air.sliderReleased.connect(self.sendSliderCahngeAir)   

        self.spinBox_conditionerOn.valueChanged.connect(self.spinboxChangeConditionerOn)

        self.spinBox_conditionerOff.valueChanged.connect(self.spinboxChangeConditionerOff)

        self.checkBox_conditionerManualControl.clicked.connect(self.checkConditionerRegim)

        self.pushButton_conditionerManualControl.clicked.connect(self.pushButtonConditionerManualControl)
    
        #Выделение газов
        self.spinBox_argon.valueChanged.connect(self.spinboxChangeArgon)        #Аргон
        self.spinBox_azot.valueChanged.connect(self.spinboxChangeAzot)          #Азот
        self.spinBox_heli.valueChanged.connect(self.spinboxChangeHeli)          #Гелий
        self.spinBox_vodorod.valueChanged.connect(self.spinboxChangeVodorod)    #Водород
        self.spinBox_CO2.valueChanged.connect(self.spinboxChangeCO2)            #Углекислый газ
        self.spinBox_CO.valueChanged.connect(self.spinboxChangeCO)              #Угарный газ
        self.spinBox_O2.valueChanged.connect(self.spinboxChangeO2)              #Кислород

        self.spinBox_weight.valueChanged.connect(self.spinboxChangeWeight)      #Масса 

        self.threadTest_instace = dataSender()


    #Объявляем переменные для класса
        self.temperatureIn = 0
        self.temperatureOut = 0
        self.humidityIn = 0
        self.humidityOut = 0
        self.conditionerState = False
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
        self.air = 0
    #Пороги включения и выключения кондиционера
        self.conditionerPorogOn = 0
        self.conditionerPorogOff = 0
        self.conditionerControlStatus = modeAuto #False Автоматический, True ручной
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

#Запуск потока
    def lunch_thread(self):
        self.threadTest_instace.start()


#Температура внутри
# Отправляем новые данные после отпускаиня слайдера
    def sendSliderCangeTemperatureIn(self):
        self.temperatureIn = self.slider_temperatureIn.value()
        self.label_temperatureIn.setText(str(self.temperatureIn))
        if sendWenChange == True:
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
        if sendWenChange == True:
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
        if sendWenChange == True:
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
        if sendWenChange == True:
            publish_data(self.mqtt_client,self.topic_data,self.get_data())


            
#Температура включения кондиционера
    def spinboxChangeConditionerOn(self):
        self.conditionerPorogOn = self.spinBox_conditionerOn.value()
        print(self.conditionerPorogOn)
        print("")
#        self.checkConditioner()

#Температура выключения кондиционера
    def spinboxChangeConditionerOff(self):
        self.conditionerPorogOff = self.spinBox_conditionerOff.value()
        print(self.conditionerPorogOff)
        print("")


        
    def checkConditionerRegim(self):
         if self.checkBox_conditionerManualControl.isChecked():
             self.conditionerControlStatus = modeManual
         else:     
            self.conditionerControlStatus = modeAuto

         if self.conditionerControlStatus == modeManual:
            print("Ручной режим")
            print("")
            self.pushButton_conditionerManualControl.setEnabled(True)
            self.spinBox_conditionerOn.setDisabled(True)
            self.spinBox_conditionerOff.setDisabled(True)
            if self.conditionerState == True:
                self.pushButton_conditionerManualControl.setText("Выкл.")
            else:
                self.pushButton_conditionerManualControl.setText("Вкл.")    

         else :
            print("Автоматический режим")
            print("")
            self.pushButton_conditionerManualControl.setDisabled(True)
            self.spinBox_conditionerOn.setEnabled(True)
            self.spinBox_conditionerOff.setEnabled(True)



#Кнопка ручного управления кондиционером
    def pushButtonConditionerManualControl(self):
        if self.conditionerState == False:
            self.label_conditionerState.setText("Вкл.")  
            self.label_conditionerState.setStyleSheet("background-color: green")
            self.pushButton_conditionerManualControl.setText("Откл.")
            self.conditionerState = True
            return
        
        if self.conditionerState == True:
            self.label_conditionerState.setText("Откл.")  
            self.label_conditionerState.setStyleSheet("background-color: red")  
            self.pushButton_conditionerManualControl.setText("Вкл.")
            self.conditionerState = False
            return


# Воздухообмен
# Отправляем новые данные после отпускаиня слайдера
    def sendSliderCahngeAir(self):
        self.air = self.slider_air.value()
        self.label_air.setText(str(self.air))
        if sendWenChange == True:
            publish_data(self.mqtt_client,self.topic_data,self.get_data())


# Отображаем новые данные без отправки
    def sliderCangeAir(self, value):
        self.air = value
        self.label_air.setText(str(value))  


#Выделение газов
#Аргон
    def spinboxChangeArgon(self):
        self.gassArgon = self.spinBox_argon.value()
        if sendWenChange == True:
            publish_data(self.mqtt_client,self.topic_data,self.get_data())

#Азот
    def spinboxChangeAzot(self):
        self.gassAzot = self.spinBox_azot.value()
        if sendWenChange == True:
            publish_data(self.mqtt_client,self.topic_data,self.get_data())

#Гелий
    def spinboxChangeHeli(self):
        self.gassGeli = self.spinBox_heli.value()
        if sendWenChange == True:
            publish_data(self.mqtt_client,self.topic_data,self.get_data())

#Водород
    def spinboxChangeVodorod(self):
        self.gassVodorod= self.spinBox_vodorod.value()
        if sendWenChange == True:
            publish_data(self.mqtt_client,self.topic_data,self.get_data())

#Углекислый газ
    def spinboxChangeCO2(self):
        self.gassCO2= self.spinBox_CO2.value()
        if sendWenChange == True:
            publish_data(self.mqtt_client,self.topic_data,self.get_data())

#Угарный газ
    def spinboxChangeCO(self):
        self.gassCO= self.spinBox_CO.value()
        if sendWenChange == True:
            publish_data(self.mqtt_client,self.topic_data,self.get_data())

#Кислород
    def spinboxChangeO2(self):
        self.gassO2= self.spinBox_O2.value()
        if sendWenChange == True:
            publish_data(self.mqtt_client,self.topic_data,self.get_data())

#Масса
    def spinboxChangeWeight(self):
        self.weight= self.spinBox_weight.value()
        if sendWenChange == True:
            publish_data(self.mqtt_client,self.topic_data,self.get_data())


    # Формируем данные для отправки
    def get_data(self):
        data = json.dumps({
            "humidity":{
                "humidityIn":  self.humidityIn, 
                "humidityOut": self.humidityOut
            },
            "temperature":{
                "temperatureIn":  self.temperatureIn, 
                "temperatureOut": self.temperatureOut
            },

            "conditionerState": self.conditionerState, #Состояние кондиционера Вкл/Выкл
            "conditionerControlStatus":self.conditionerControlStatus,#Режим управления ручной/автоматический
            "conditionerPorogOn": self.conditionerPorogOn,
            "conditionerPorogOff": self.conditionerPorogOff,

            "weight": self.weight,
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
            "barrier": self.barrier,
            "air": self.air
        })
        return data
    

    #Читаем данные при загрузке формы
    def readFormData(self):
        self.humidityIn = self.slider_humidityIn.value()
        self.spinboxChangeConditionerOff()
        self.spinboxChangeConditionerOn()
        publish_data(self.mqtt_client,self.topic_data,self.get_data())


#Команда на управление шлакбаумом
    def command_barrierCmd(self, client, userdata, message):
        print("CMD: changeBarrierState, value: %s" % message.payload)
        print("")
        try:
            self.barrier  = bool(message.payload)
            print(self.barrier )
            print("")
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
            print("")

#Команда на управление кондиционером
    def command_conditionerCmd(self, client, userdata, message):
        print("CMD: changeConditionerState, value: %s" % message.payload)
        print("")
        try:
            self.conditionerState  = bool(message.payload)
            print(self.barrier )
            print("")
            if self.conditionerState == True:
                self.label_conditionerState.setText("Вкл.")  
                self.label_conditionerState.setStyleSheet("background-color: green")
            if self.conditionerState == False:
                self.label_conditionerState.setText("Откл.")  
                self.label_conditionerState.setStyleSheet("background-color: red")  
        except:
            print("can't change staste to %s" % message.payload)
            print("")




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
    print("")
    if rc == 0:
        isConnect = 1
        client.publish("connect", "true", 1)
    if rc == 5:
        print("Authorization error")
        print("")

# default message reaction
def on_message(client, userdata, message):
    print("Some message received topic: %s, payload: %s" %
          (message.topic, message.payload))
    print("")

# connect to server
def publish_data(client, topic, data):
    print(topic, data)
    print("")
    return client.publish(topic, data)


def run(client, host="dev.rightech.io", port=1883):
    client.connect(host, port, 60)
    client.loop_start()



'''
В этом классе реализуем отдельный поток для отправки данных от батчиков склада
'''
class dataSender(QtCore.QThread):
    def __init__(self, parent = None):
        super().__init__()
     
        
    def run(self):
        while(1):
            sleep(10)            
            print("Поток ")
            print("")
            publish_data(window.mqtt_client,window.topic_data,window.get_data())




#***********************************Основная программа****************************************************
print("Start GIU")
print("")
app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
window = ExampleApp()  # Создаём объект класса ExampleApp
window.show()  # Показываем окно
window.readFormData()
publish_data(window.mqtt_client,window.topic_data, window.get_data())
print("OK")
print("")
window.lunch_thread()
app.exec_()  # и запускаем приложение        
