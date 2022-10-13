"""
Эмулятор начнет движение усли установить скорость > 0
"""


#import imp
import sys
from time import sleep  # sys нужен для передачи argv в QApplication
from PyQt5 import QtWidgets, QtCore
import ui_GUITruck  # Это наш конвертированный файл дизайна

import paho.mqtt.client as mqtt  # mqtt paho
import json  # json converter
import threading

localCounter = 0

class ExampleApp(QtWidgets.QMainWindow, ui_GUITruck.Ui_MainWindow):
    def __init__(self):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        super().__init__()
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна

        self.pushButton_suddenBraking.clicked.connect(self.buttonClicked)

        self.slider_temperatureIn.valueChanged.connect(self.sliderCangeTemperatureIn)
        self.slider_temperatureIn.sliderReleased.connect(self.sendSliderCangeTemperatureIn)        

        self.slider_temperatureOut.valueChanged.connect(self.sliderCangeTemperatureOut)
        self.slider_temperatureOut.sliderReleased.connect(self.sendSliderCangeTemperatureOut)      

        self.slider_humidityIn.valueChanged.connect(self.sliderCangeHumidityeIn)
        self.slider_humidityIn.sliderReleased.connect(self.sendSliderCangeHumidityIn)
        
        self.slider_humidityOut.valueChanged.connect(self.sliderCangeHumidityeOut)       
        self.slider_humidityOut.sliderReleased.connect(self.sendSliderCangeHumidityOut)    

        self.slider_speed.valueChanged.connect(self.sliderCangeSpeed)       
        self.slider_speed.sliderReleased.connect(self.sendSliderCangeSpeed)    

        self.spinBox_conditionerOn.valueChanged.connect(self.spinboxChangeConditionerOn)

        self.spinBox_conditionerOff.valueChanged.connect(self.spinboxChangeConditionerOff)

        self.slider_chock.valueChanged.connect(self.sliderCangeChock)       
        self.slider_chock.sliderReleased.connect(self.sendSliderCangeChock)   

        self.spinBox_argon.valueChanged.connect(self.spinboxChangeArgon)

        self.spinBox_azot.valueChanged.connect(self.spinboxChangeAzot)
        
        self.spinBox_heli.valueChanged.connect(self.spinboxChangeHeli)

        self.spinBox_vodorod.valueChanged.connect(self.spinboxChangeVodorod)

        self.spinBox_CO2.valueChanged.connect(self.spinboxChangeCO2)

        self.spinBox_CO.valueChanged.connect(self.spinboxChangeCO)   
             
        self.spinBox_O2.valueChanged.connect(self.spinboxChangeO2)  

        self.spinBox_weight.valueChanged.connect(self.spinboxChangeWeight)  

        self.threadTest_instace = coordinateSender() # Сюда на



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
        self.suddenBraking = 0  #аварийное торможеие для отправки 
        self.suddenBrakingLael = 0 #аварийное торможеие для Отображения на эмуляторе 
        self.gassArgon = 0
        self.gassAzot = 0
        self.gassGeli = 0
        self.gassVodorod = 0
        self.gassCO2 = 0    #Углекислый
        self.gassCO = 0     #Угарный
        self.gassO2 = 0
        self.weight = 0
    #Пороги включения и выключения кондиционера
        self.conditionerPorogOn = 0
        self.conditionerPorogOff = 0
    #Топики    
        # отправляемое сообщеие
        self.topic_data = "data/state"  # текущее состояние
        self.topic_conditionerCmd = "command/conditioner"  # Команда на управление кондиционером
        
        self.mqtt_client = init("mqtt-vikonik-Truck")#mqtt-vikonik-Truck
      

        self.mqtt_client.subscribe(self.topic_conditionerCmd)
        self.mqtt_client.message_callback_add(self.topic_conditionerCmd, self.command_conditionerCmd)
       
        run(self.mqtt_client)



    def lunch_thread(self):
        self.threadTest_instace.start()



#Температура внутри
# Отправляем новые данные после отпускаиня слайдера
    def sendSliderCangeTemperatureIn(self):
        self.temperatureIn = self.slider_temperatureIn.value()
        self.label_temperatureIn.setText(str(self.temperatureIn))
      #  publish_data(self.mqtt_client,self.topic_data,self.get_data())
        #self.checkConditioner()

# Отображаем новые данные без отправки
    def sliderCangeTemperatureIn(self, value):
        self.temperatureIn = value
        self.label_temperatureIn.setText(str(value))

#Температура снаружи
# Отправляем новые данные после отпускаиня слайдера
    def sendSliderCangeTemperatureOut(self):
        self.temperatureOut = self.slider_temperatureOut.value()
        self.label_temperatureOut.setText(str(self.temperatureOut))
      #  publish_data(self.mqtt_client,self.topic_data,self.get_data())


# Отображаем новые данные без отправки
    def sliderCangeTemperatureOut(self, value):
        self.temperatureOut = value
        self.label_temperatureOut.setText(str(value))  

# Влажность внутри
# Отправляем новые данные после отпускаиня слайдера
    def sendSliderCangeHumidityIn(self):
        self.humidityIn = self.slider_humidityIn.value()
        self.label_humidityIn.setText(str(self.humidityIn))
        #publish_data(self.mqtt_client,self.topic_data,self.get_data())

# Отображаем новые данные без отправки
    def sliderCangeHumidityeIn(self, value):
        self.humidityIn = value
        self.label_humidityIn.setText(str(value))  

# Влажность снаружи
# Отправляем новые данные после отпускаиня слайдера
    def sendSliderCangeHumidityOut(self):
        self.humidityOut = self.slider_humidityOut.value()
        self.label_humidityOut.setText(str(self.humidityOut))
       # publish_data(self.mqtt_client,self.topic_data,self.get_data())

# Отображаем новые данные без отправки
    def sliderCangeHumidityeOut(self, value):
        self.humidityOut = value
        self.label_humidityOut.setText(str(value))  

 
#Скорость
# Отправляем новые данные после отпускаиня слайдера
    def sendSliderCangeSpeed(self):
        self.speed = self.slider_speed.value()
        self.label_speed.setText(str(self.speed))
       # publish_data(self.mqtt_client,self.topic_data,self.get_data())

# Отображаем новые данные без отправки
    def sliderCangeSpeed(self, value):
        self.speed = value
        self.label_speed.setText(str(value))  

#Температура включения кондиционера
    def spinboxChangeConditionerOn(self):
        self.conditionerPorogOn = self.spinBox_conditionerOn.value()
        print(self.conditionerPorogOn)
#        self.checkConditioner()

#Температура выключения кондиционера
    def spinboxChangeConditionerOff(self):
        self.conditionerPorogOff = self.spinBox_conditionerOff.value()
        print(self.conditionerPorogOff)  


#Проверка включения кондиционера
    ''' 
    def checkConditioner(self):
        if self.conditionerPorogOn < self.temperatureIn and self.conditionerState != True:
            self.conditionerState = True
            self.label_conditionerState.setText("Вкл.")
            publish_data(self.mqtt_client,self.topic_data,self.get_data())

        if self.conditionerPorogOff > self.temperatureIn and self.conditionerState == True:
            self.conditionerState = False
            self.label_conditionerState.setText("Откл.")            
            publish_data(self.mqtt_client,self.topic_data,self.get_data())
    '''            

#Команда на управление кондиционером
    def command_conditionerCmd(self, client, userdata, message):
        print("CMD: changeConditionerState, value: %s" % message.payload)
        try:
            self.conditionerState  = bool(message.payload)
            print(self.conditionerState )
            if self.conditionerState == True:
                self.label_conditionerState.setText("Вкл.")  
                self.label_conditionerState.setStyleSheet("background-color: green")
            if self.conditionerState == False:
                self.label_conditionerState.setText("Откл.")  
                self.label_conditionerState.setStyleSheet("background-color: red")  
        except:
            print("can't change staste to %s" % message.payload)




#Кнопка резких торможений
    def buttonClicked(self):
        self.suddenBrakingLael = self.suddenBrakingLael + 1
        self.label_suddenBraking.setText(str(self.suddenBrakingLael))
        self.suddenBraking = 1
      #  publish_data(self.mqtt_client,self.topic_data,self.get_data())
        self.suddenBraking = 0


#Уровень тряски
# Отправляем новые данные после отпускаиня слайдера
    def sendSliderCangeChock(self):
        self.choke = self.slider_chock.value()
        self.label_choke.setText(str(self.choke))
       # publish_data(self.mqtt_client,self.topic_data,self.get_data())


# Отображаем новые данные без отправки
    def sliderCangeChock(self, value):
        self.choke = value
        self.label_choke.setText(str(value))

#Выделение газов
#Аргон
    def spinboxChangeArgon(self):
        self.gassArgon = self.spinBox_argon.value()
       # publish_data(self.mqtt_client,self.topic_data,self.get_data())

#Азот
    def spinboxChangeAzot(self):
        self.gassAzot = self.spinBox_azot.value()
       # publish_data(self.mqtt_client,self.topic_data,self.get_data())

#Гелий
    def spinboxChangeHeli(self):
        self.gassGeli = self.spinBox_heli.value()
      #  publish_data(self.mqtt_client,self.topic_data,self.get_data())

#Водород
    def spinboxChangeVodorod(self):
        self.gassVodorod= self.spinBox_vodorod.value()
       # publish_data(self.mqtt_client,self.topic_data,self.get_data())

#Углекислый газ
    def spinboxChangeCO2(self):
        self.gassCO2= self.spinBox_CO2.value()
       # publish_data(self.mqtt_client,self.topic_data,self.get_data())

#Угарный газ
    def spinboxChangeCO(self):
        self.gassCO= self.spinBox_CO.value()
        #publish_data(self.mqtt_client,self.topic_data,self.get_data())
#Кислород
    def spinboxChangeO2(self):
        self.gassO2= self.spinBox_O2.value()
       # publish_data(self.mqtt_client,self.topic_data,self.get_data())

#Масса
    def spinboxChangeWeight(self):
        self.weight= self.spinBox_weight.value()
        #publish_data(self.mqtt_client,self.topic_data,self.get_data())


    # Формируем данные для отправки
    def get_data(self):
        data = json.dumps({
            "pos":{
                "lat": self.lat,
                "lon": self.lon
            },#Исключим координаты для симулятора. Их будем отправлять в другом потоке
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
            }
        })
        return data

    #Читаем данные при загрузке формы
    def readFormData(self):
        self.humidityIn = self.slider_humidityIn.value()
        self.humidityOut = self.slider_humidityOut.value()
        self.spinboxChangeConditionerOff()
        self.spinboxChangeConditionerOn()
        publish_data(self.mqtt_client,self.topic_data,self.get_data())



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
    #print(topic, data)
    return client.publish(topic, data)


def run(client, host="dev.rightech.io", port=1883):
    client.connect(host, port, 60)
    client.loop_start()




'''
В этом классе реализуем отдельный поток для отправки координат автомобиля.
Ечли скоость не равна 0 то эмулятор начнет отправку коордеинат
            [28.321445, 57.349902],
            [28.321579, 57.349832],
            [28.321724, 57.349731],
            [28.321939, 57.349624],
            [28.322153, 57.349465],
            [28.322368, 57.349346],
            [28.32262, 57.349216],
            [28.322915, 57.349028],
            [28.323269, 57.348811],
            [28.323526, 57.348663],
            [28.323816, 57.348492],
            [28.32409, 57.348307],
            [28.324422, 57.348113],
            [28.324776, 57.347905],
            [28.325082, 57.347725],
            [28.325425, 57.347491],
            [28.325801, 57.347219],
            [28.326273, 57.346924],
            [28.326788, 57.346533],
            [28.327432, 57.346104],
            [28.328032, 57.345711],
            [28.328741, 57.345167],
            [28.329363, 57.344842],
            [28.330307, 57.344866],
            [28.331809, 57.344958],
            [28.332882, 57.344981],
            [28.333676, 57.345074],
            [28.334405, 57.345005],
            [28.335736, 57.344738],
            [28.336744, 57.344507],
            [28.338053, 57.344229],
'''
class coordinateSender(QtCore.QThread):
    def __init__(self, parent = None):
        super().__init__()
        self.topic_data = "data/state"  # текущее состояние
        self.mqtt_client = init("mqtt-vikonik-Truck")#mqtt-vikonik-Truck
        self.lat = 57.0  # Текущая координата устройства
        self.lon = 28.0  # Текущая координата устройства
        self.pointCnt = 0
        self.numOfPoint = 5 #36
        self.dir = 0 #Направление движения автомобиля 0-На склад, 1-на ферму
         #Координаты на склад и назад
        self.coordinates =  [

            [28.338954, 57.343986],
            [28.340113, 57.34365],
            [28.34125, 57.343233],
            [28.341916, 57.343036],
            [28.342195, 57.342967],
            [28.341916, 57.342816]
            ]
  

        
    def run(self):
        while(1):
            sleep(5)            
            #print("Поток кординаты , %d ", self.pointCnt)
            if window.speed > 0:
                if self.pointCnt == 0:
                    self.dir = 0 
                if self.pointCnt == self.numOfPoint:
                    self.dir = 1    

                if self.dir == 0 :
                    self.pointCnt = self.pointCnt + 1
                    #self.pointCnt = self.pointCnt % 37
                if self.dir == 1 :
                    self.pointCnt = self.pointCnt - 1
       

                #self.lat = self.coordinates[self.pointCnt][0]     # Эмулятор движения
                #self.lon = self.coordinates[self.pointCnt][1] 

                window.lat = self.coordinates[self.pointCnt][1] 
                window.lon = self.coordinates[self.pointCnt][0] 
                window.label_lat.setText(str(window.lat))
                window.label_lon.setText(str(window.lon))

            publish_data(window.mqtt_client,window.topic_data,window.get_data())

    # Формируем данные для отправки
    def get_data(self):
        data = json.dumps({
            "pos":{
                "lat": self.lat,
                "lon": self.lon
            },#Исключим координаты для симулятора. Их будем отправлять в другом потоке
            "speed": self.pointCnt  # скорость
        })
        return data



   



print("Start GIU")
app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
window = ExampleApp()  # Создаём объект класса ExampleApp
window.show()  # Показываем окно
window.readFormData()
publish_data(window.mqtt_client,window.topic_data, window.get_data())
print("OK")
window.lunch_thread()
app.exec_()  # и запускаем приложение
    


'''
def main():
    print("READY")
    printTest()
    initMQTT()

    timer = QtCore.QTimer()
    

    timer.timeout.connect(timerEvent)
    timer.start(1000)

    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = ExampleApp()  # Создаём объект класса ExampleApp
    window.show()  # Показываем окно
    app.exec_()  # и запускаем приложение
    




if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    main()  # то запускаем функцию main()
'''
''''''

