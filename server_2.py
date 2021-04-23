import paho.mqtt.client as mqtt
import numpy as np
from matplotlib import pyplot as plt
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import datetime
import pandas as pd
import time
np.set_printoptions(formatter={'float': lambda x: "{0:0.3f}".format(x)})

#filter
# https://gist.github.com/junzis/e06eca03747fc194e322
from scipy.signal import butter, lfilter, freqz
# Filter requirements.
order = 3
fs = 30.0       # sample rate, Hz
cutoff = 4 # desired cutoff frequency of the filter, Hz

alpha = 0.5
index_filterx = 1
index_filtery = 1
index_filterz = 1
AxFilter=[0] * 10
AyFilter=[0] * 10
AzFilter=[0] * 10

# Set point
position_null_device1_Z = 15
position_null_device1_X = 3.5
position_null_device2_Z = 12
position_null_device2_X = 3.5
position_null_device3_Z = 15
position_null_device3_X = 3.5

# figure

#fig = plt.gcf()
#fig.show()
#fig.canvas.draw()

#plt.ion()

topic_device_1 = "Device1/"
topic_device_2 = "Device2/"
topic_device_3 = "Device3/"
topic_accX = "accX"
topic_accY = "accY"
topic_accZ = "accZ"

# integral sampling time
dt = 0.01
vX = 0
vZ = 0
positionX = 0
positionZ = 0

vxDevice1 = 0
vzDevice1 = 0
positionXDev1 = 0
positionZDev1= 0

vxDevice2 = 0
vzDevice2 = 0
positionXDev2 = 0
positionZDev2= 0

vxDevice3 = 0
vzDevice3 = 0
positionXDev3 = 0
positionZDev3= 0

# low pass
def butter_lowpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

# low pass
def butter_lowpass_filter(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = lfilter(b, a, data)
    return y


# calculate integration of accleration
def double_integration_acc(listAcc,deltaTime=dt):
    '''
        listAcc = array of accelerometer
        deltaTime = sampling time, defaut value 0.001 / 1ms

        return 
            position, velocity
    '''
    velocity = []
    velocity.append(0) # add first element of velocity = 0
    position = []
    position.append(0) # add first element of position = 0
    
    # first integration
    for i in range(len(listAcc)):
        #result += x * deltaTime # integral
        vel_now = velocity[i] + listAcc[i] * deltaTime
        velocity.append(vel_now) # velcocity = prev_velocity + current_accleration*deltaTime

    # double integration
    for i in range(len(velocity)):
        position_now = position[i] + velocity[i] * deltaTime
        position.append(position_now) # position = prev_position + current_velocity*deltaTime

    # sum all element 
    return round(abs(np.sum(position)),3) , round(abs(np.sum(velocity)),3)

# csvwrite
def write_tocsv(topic,dataframe) :
    """
    Write result data to csv file
    :param data:dataSaved as dataframe
    :return:
    """
    global filename
    #csvfilename = filename.replace('devicename',topic)
    csvfilename = topic
    dataframe.to_csv(csvfilename, mode='a', header=False,index=False)

def preprocessing(data_str):
    split_data = data_str.split(",")
    data_float = np.array(split_data).astype(np.float) # convert array of string to array of float
    result = data_float
    return result

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(topic_device_1+"#")
    client.subscribe(topic_device_2+"#")
    client.subscribe(topic_device_3+"#")


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    # 1. Terima data AccX,AccY,AccZ
    # 2. Preprocessing
    # 3. LPF
    # 4. Integral
    # 5. Fuzzy
    '''
    '''
    global decision_result1,decision_result2,decision, vX, vZ, fuzzLongsor, positionX, positionZ
    global vxDevice1,vzDevice1,vxDevice2,vzDevice2,vxDevice3,vzDevice3,positionXDev1,positionXDev2,positionXDev3,positionZDev1,positionZDev2,positionZDev3
    print("----------------------------------------------- \n")
    # device 1
    msg.payload = msg.payload.decode("utf-8")
    if(msg.topic == topic_device_1+topic_accX):
        device_name = msg.topic.split("/")[0]
        print(device_name)
        print("-------------------------------")
        print(topic_device_1 + "AccX")
        # 1 
        data_raw = str(msg.payload)
        # 2
        data_float = preprocessing(data_raw)
        print("RAW Data ")
        print(data_float)
        # 3
        filtered_data = butter_lowpass_filter(data_float, cutoff, fs, order)
        print("LPF AccX : ")
        print(filtered_data)

        '''
        data_filtered_2 = []
        for val in data_float:
            AxFilter[index_filterx]=alpha * val +(1-alpha) * AxFilter[index_filterx-1]
            AxFilter[index_filterx-1]=AxFilter[index_filterx]
            AxFiltered=AxFilter[index_filterx]
            data_filtered_2.append(AxFiltered)

        print("Data Filtered 2 : ")
        print(data_filtered_2)
        

        velocityX = 0 
        for x in data_filtered_2:
            velocityX += x * dt # integral 
        '''
        
        # 4 
        #velocity, position = double_integration(data_filtered_2,data_filtered_2,data_filtered_2)
        vX, positionX = double_integration_acc(filtered_data)
        print("Velocity X  : ")
        print(vX)
        print("Position X : ")
        print(positionX)
        vxDevice1 = vX
        positionXDev1 = positionX
    if(msg.topic == topic_device_1+topic_accZ):
        device_name = msg.topic.split("/")[0]
        print(device_name)
        print(topic_device_1 + " AccZ ")
        # 1 
        data_raw = str(msg.payload)
        # 2
        data_float = preprocessing(data_raw)
        # 3
        filtered_data = butter_lowpass_filter(data_float, cutoff, fs, order)
        print("LPF AccZ : ")
        print(filtered_data)
        
        #vZ = velocityZ
        vZ, positionZ = double_integration_acc(filtered_data)
        vzDevice1 = vZ
        positionZDev1 = positionZ
        print("Velocity X  : ")
        print(vX)
        print("Position X : ")
        print(positionX)
        print("Velocity Z  : ")
        print(vZ)
        print("Position Z : ")
        print(positionZ)

        print("Relative Position : ")
        if (position_null_device1_X > positionX):
            relative_positionX = round(position_null_device1_X - positionX, 3)
        elif (position_null_device1_X < positionX):
            relative_positionX = round(positionX - position_null_device1_X, 3)
        if (position_null_device1_Z > positionZ):
            relative_positionZ = round(position_null_device1_Z - positionZ, 3)
        elif (position_null_device1_Z < positionZ):
            relative_positionZ = round(positionZ - position_null_device1_Z, 3)
        print(" Relative X : {} - Relative Z : {}".format(relative_positionX,relative_positionZ))

        # fuzzy input
        #decision.input['Position Z'] = relative_positionZ
        #decision.input['Position X'] = relative_positionX
        #decision.compute()
        #print("Decision : ")
        #decision_result1 = round(decision.output['Longsor'],3)
        #print('hasil1  : ',format(decision_result1))
        #if(decision_result >= 50):
            #decision_result_str = "Ya Longsor"
        #else:
            #decision_result_str = "Tidak Longsor"
        #print('Value : {} - Status : {}'.format(decision_result,decision_result_str))


        # save to csv
        #saved_csv = []
        #saved_csv.append(int(time.time()))
        #saved_csv.append(positionX)
        #saved_csv.append(positionZ)
        #saved_csv.append(relative_positionX)
        #saved_csv.append(relative_positionZ)
        #saved_csv.append(decision_result1)
        #saved_csv.append(decision_result_str)
        #dataSaved = pd.DataFrame([saved_csv])
        #write_tocsv(device_name,dataSaved)

    # device 2
    if(msg.topic == topic_device_2+topic_accX):
        device_name = msg.topic.split("/")[0]
        print(device_name)
        # receive data
        print(topic_device_2 + " AccX")
        # 1 
        data_raw = str(msg.payload)
        # 2
        data_float = preprocessing(data_raw)
        print("RAW Data ")
        print(data_float)
        # 3
        filtered_data = butter_lowpass_filter(data_float, cutoff, fs, order)
        print("LPF AccX : ")
        print(filtered_data)

        '''
        data_filtered_2 = []
        for val in data_float:
            AxFilter[index_filterx]=alpha * val +(1-alpha) * AxFilter[index_filterx-1]
            AxFilter[index_filterx-1]=AxFilter[index_filterx]
            AxFiltered=AxFilter[index_filterx]
            data_filtered_2.append(AxFiltered)

        print("Data Filtered 2 : ")
        print(data_filtered_2)
        

        velocityX = 0 
        for x in data_filtered_2:
            velocityX += x * dt # integral 
        '''

        # 4 
        #velocity, position = double_integration(data_filtered_2,data_filtered_2,data_filtered_2)
        vX, positionX = double_integration_acc(filtered_data)
        print("Velocity X  : ")
        print(vX)
        vxDevice2 = vX
        positionXDev2 = positionX

    if(msg.topic == topic_device_2+topic_accZ):
        device_name = msg.topic.split("/")[0]
        print(device_name)
        print(topic_device_2 + " AccZ ")
        # 1 
        data_raw = str(msg.payload)
        # 2
        data_float = preprocessing(data_raw)
        print(data_float)
        # 3
        filtered_data = butter_lowpass_filter(data_float, cutoff, fs, order)
        print("LPF AccZ : ")
        print(filtered_data)
        
        #vZ = velocityZ
        vZ, positionZ = double_integration_acc(filtered_data)
        vzDevice2 = vZ
        positionZDev2 = positionZ
        print("Velocity X  : ")
        print(vX)
        print("Position X : ")
        print(positionX)

        print("Velocity Z  : ")
        print(vZ)
        print("Position Z : ")
        print(positionZ)

        print("Relative Position : ")
        if(position_null_device2_X > positionX):
            relative_positionX = round(position_null_device2_X - positionX,3)
        elif(position_null_device2_X < positionX):
            relative_positionX = round(positionX - position_null_device2_X,3)
        if(position_null_device2_Z > positionZ):
            relative_positionZ = round(position_null_device2_Z - positionZ,3)
        elif(position_null_device2_Z < positionZ):
            relative_positionZ = round(positionZ - position_null_device2_Z,3)
        print(" Relative X : {} - Relative Z : {}".format(relative_positionX, relative_positionZ))

        # fuzzy input
        #decision.input['Position Z'] = relative_positionZ
        #decision.input['Position X'] = relative_positionX
        #decision.compute()
        #print("Decision : ")
        #decision_result2 = round(decision.output['Longsor'],3)
        #print('hasil2 : ',format(decision_result2))
        #if(decision_result >= 50):
         #   decision_result_str = "Ya Longsor"
        #else:
        #    decision_result_str = "Tidak Longsor"
        #print('Value : {} - Status : {}'.format(decision_result,decision_result_str))

        # save to csv
        #saved_csv = []
        #saved_csv.append(int(time.time()))
        #saved_csv.append(positionX)
        #saved_csv.append(positionZ)
        #saved_csv.append(relative_positionX)
        #saved_csv.append(relative_positionZ)
        #saved_csv.append(decision_result2)
        #saved_csv.append(decision_result_str)
        #dataSaved = pd.DataFrame([saved_csv])
        #write_tocsv(device_name,dataSaved)

    # device 3
    if(msg.topic == topic_device_3+topic_accX):
        device_name = msg.topic.split("/")[0]
        print(device_name)
        print(topic_device_3 + " AccX")
        # 1 
        data_raw = str(msg.payload)
        # 2
        data_float = preprocessing(data_raw)
        print("RAW Data ")
        print(data_float)
        # 3
        filtered_data = butter_lowpass_filter(data_float, cutoff, fs, order)
        print("LPF AccX : ")
        print(filtered_data)

        '''
        data_filtered_2 = []
        for val in data_float:
            AxFilter[index_filterx]=alpha * val +(1-alpha) * AxFilter[index_filterx-1]
            AxFilter[index_filterx-1]=AxFilter[index_filterx]
            AxFiltered=AxFilter[index_filterx]
            data_filtered_2.append(AxFiltered)

        print("Data Filtered 2 : ")
        print(data_filtered_2)
        

        velocityX = 0 
        for x in data_filtered_2:
            velocityX += x * dt # integral 
        '''
        
        # 4 
        #velocity, position = double_integration(data_filtered_2,data_filtered_2,data_filtered_2)
        vX, positionX = double_integration_acc(filtered_data)
        print("Velocity X  : ")
        print(vX)
        print("Position X : ")
        print(positionX)
        vxDevice3 = vX
        positionXDev3 = positionX
    if(msg.topic == topic_device_3+topic_accZ):
        device_name = msg.topic.split("/")[0]
        print(device_name)
        print(topic_device_3 + " AccZ ")
        # 1
        data_raw = str(msg.payload)
        # 2
        data_float = preprocessing(data_raw)
        # 3
        filtered_data = butter_lowpass_filter(data_float, cutoff, fs, order)
        print("LPF AccZ : ")
        print(filtered_data)

        # vZ = velocityZ
        vZ, positionZ = double_integration_acc(filtered_data)
        vzDevice3 = vZ
        positionZDev3 = positionZ
        print("Velocity X  : ")
        print(vX)
        print("Position X : ")
        print(positionX)

        print("Velocity Z  : ")
        print(vZ)
        print("Position Z : ")
        print(positionZ)

        print("Relative Position : ")
        if (position_null_device3_X > positionX):
            relative_positionX = round(position_null_device3_X - positionX, 3)
        elif (position_null_device3_X < positionX):
            relative_positionX = round(positionX - position_null_device2_X, 3)
        if (position_null_device3_Z > positionZ):
            relative_positionZ = round(position_null_device3_Z - positionZ, 3)
        elif (position_null_device3_Z < positionZ):
            relative_positionZ = round(positionZ - position_null_device3_Z, 3)
        print(" Relative X : {} - Relative Z : {}".format(relative_positionX, relative_positionZ))

        # fuzzy input
        #decision.input['Position Z'] = relative_positionZ
        #decision.input['Position X'] = relative_positionX
        #decision.compute()
        ##print("Decision : ")
        #decision_result3 = round(decision.output['Longsor'],3)
        #print('hasil3 : ',format(decision_result3))

        # fuzzy

        #if (decision_result >= 50):
            #decision_result_str = "Ya Longsor"
        #else:
            #decision_result_str = "Tidak Longsor"
        #print('Value : {} - Status : {}'.format(decision_result, decision_result_str))




    #decision_result = round((decision_result3+decision_result1+decision_result2) / 3,2)
    # print(decision_result1)
    # print('Decision 1 :', format(hasil1))
    #print('Decision Final : ', format(decision_result))
    #print(decision_result1)
    print("----------------Decision --------------")
    rel_positionx_dev1 = 0
    rel_positionz_dev1 = 0
    if (position_null_device1_X > positionXDev1):
        rel_positionx_dev1 = round(position_null_device1_X - positionXDev1, 3)
    elif (position_null_device1_X < positionXDev1):
        rel_positionx_dev1 = round(positionXDev1 - position_null_device1_X, 3)
    if (position_null_device1_Z > positionZDev1):
        rel_positionz_dev1 = round(position_null_device1_Z - positionZDev1, 3)
    elif (position_null_device1_Z < positionZDev1):
        rel_positionz_dev1 = round(positionZDev1 - position_null_device1_Z, 3)

    #rel_positionx_dev1 =round(abs(positionXDev1) - position_null_device1_X,3)
    decision.input['Position X Dev1'] = rel_positionx_dev1
    #rel_positionz_dev1 = round(abs(positionZDev1) - position_null_device1_Z, 3)
    decision.input['Position Z Dev1'] = rel_positionz_dev1
    print("Device 1 - Relative X : {} - Relative Z : {}".format(rel_positionx_dev1, rel_positionz_dev1))

    rel_positionx_dev2 = 0
    rel_positionz_dev2 = 0
    if (position_null_device2_X > positionXDev2):
        rel_positionx_dev2 = round(position_null_device2_X - positionXDev2, 3)
    elif (position_null_device2_X < positionXDev2):
        rel_positionx_dev2 = round(positionXDev2 - position_null_device2_X, 3)
    if (position_null_device2_Z > positionZDev2):
        rel_positionz_dev2 = round(position_null_device2_Z - positionZDev2, 3)
    elif (position_null_device2_Z < positionZDev2):
        rel_positionz_dev2 = round(positionZDev2 - position_null_device2_Z, 3)
    #rel_positionx_dev2 =round(abs(positionXDev2) - position_null_device2_X,3)
    decision.input['Position X Dev2'] = rel_positionx_dev2
    #rel_positionz_dev2 = round(abs(positionZDev2) - position_null_device2_Z, 3)
    decision.input['Position Z Dev2'] = rel_positionz_dev2
    print("Device 2 - Relative X : {} - Relative Z : {}".format(rel_positionx_dev2, rel_positionz_dev2))

    rel_positionx_dev3 = 0
    rel_positionz_dev3 = 0
    if (position_null_device3_X > positionXDev3):
        rel_positionx_dev3 = round(position_null_device3_X - positionXDev3,3)
    elif (position_null_device3_X < positionXDev3):
        rel_positionx_dev3 = round(positionXDev3 - position_null_device3_X, 3)
    if (position_null_device3_Z > positionZDev3):
        rel_positionz_dev3 = round(position_null_device3_Z - positionZDev3, 3)
    elif (position_null_device3_Z < positionZDev3):
        rel_positionz_dev3 = round(positionZDev3 - position_null_device3_Z, 3)

    #rel_positionx_dev3 =round(abs(positionXDev3) - position_null_device3_X,3)
    decision.input['Position X Dev3'] = rel_positionx_dev3
    #rel_positionz_dev3 = round(abs(positionZDev3) - position_null_device3_Z, 3)
    decision.input['Position Z Dev3'] = rel_positionz_dev3
    print("Device 3 - Relative X : {} - Relative Z : {}".format(rel_positionx_dev3, rel_positionz_dev3))

    decision.compute()
    decision_result = round(decision.output['Longsor'],3)

    if (decision_result >= 50):
        decision_result_str = "Ya Longsor"
    else:
        decision_result_str = "Tidak Longsor"
    #print('Status  :', format(decision_status))
    print('Value : {} - Status : {}'.format(decision_result, decision_result_str))

    # save to csv
    saved_csv = []
    saved_csv.append(int(time.time()))
    saved_csv.append(positionXDev1)
    saved_csv.append(positionZDev1)
    saved_csv.append(positionXDev2)
    saved_csv.append(positionZDev2)
    saved_csv.append(positionXDev3)
    saved_csv.append(positionZDev3)
    saved_csv.append(rel_positionx_dev1)
    saved_csv.append(rel_positionz_dev1)
    saved_csv.append(rel_positionx_dev2)
    saved_csv.append(rel_positionz_dev2)
    saved_csv.append(rel_positionx_dev3)
    saved_csv.append(rel_positionz_dev3)
    saved_csv.append(decision_result)
    saved_csv.append(decision_result_str)
    dataSaved = pd.DataFrame([saved_csv])
    write_tocsv('log_file_all_device.csv', dataSaved)


def on_log(mqttc, obj, level, string):
    print(string)


if __name__== '__main__':
    dt = datetime.datetime.now()
    filename = 'result/%s-%s-%s-%s-%s.csv' % ("devicename", dt.day, dt.month, dt.year, dt.hour)
    print(filename)
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    #client.on_log = on_log

    server_broker = "192.168.43.170"
    client.connect(server_broker, 1883, 60)

        # fuuzzy
    '''
    * Antecednets (Inputs)
    - `Velocity X`
        * Universe (ie, crisp value range): on a scale of 0 to 10?
        * Fuzzy set (ie, fuzzy value range): dekat, sedang, jauh
    - `Velocity Z`
        * Universe: How tasty was the food, on a scale of 0 to 10?
        * Fuzzy set: dekat, sedang, jauh
    * Consequents (Outputs)
    - `Longsor`
        * Universe: on scale 0 .. 1
        * Fuzzy set: tidak, ya
    * Rules
    - IF the *service* was good  *or* the *food quality* was good,
        THEN the tip will be high.
    - IF the *service* was average, THEN the tip will be medium.
    - IF the *service* was poor *and* the *food quality* was poor
        THEN the tip will be low.
    * Usage
    - If I tell this controller that I rated:
        * the service as 9.8, and
        * the quality as 6.5,
    - it would recommend I leave:
        * a 20.2% tip.
    '''
    fuzzPositionXDev1 = ctrl.Antecedent(np.arange(0, 6, 1), 'Position X Dev1') # 0 .. 10
    fuzzPositionZDev1 = ctrl.Antecedent(np.arange(0, 15, 1), 'Position Z Dev1') # 0 .. 15
    fuzzPositionXDev2 = ctrl.Antecedent(np.arange(0, 6, 1), 'Position X Dev2')  # 0 .. 10
    fuzzPositionZDev2 = ctrl.Antecedent(np.arange(0, 15, 1), 'Position Z Dev2')  # 0 .. 15
    fuzzPositionXDev3 = ctrl.Antecedent(np.arange(0, 6, 1), 'Position X Dev3')  # 0 .. 10
    fuzzPositionZDev3 = ctrl.Antecedent(np.arange(0, 15, 1), 'Position Z Dev3')  # 0 .. 15
    fuzzLongsor = ctrl.Consequent(np.arange(0,101,1) , 'Longsor') # 0 .. 1

    # membership function position X
    fuzzPositionXDev1['dekat'] = fuzz.trimf(fuzzPositionXDev1.universe , [0,0,2])
    fuzzPositionXDev1['sedang'] = fuzz.trapmf(fuzzPositionXDev1.universe,[0,2,3,5])
    fuzzPositionXDev1['jauh'] = fuzz.trimf(fuzzPositionXDev1.universe, [3,5,5])

    # membership function position Z
    fuzzPositionZDev1['dekat'] = fuzz.trimf(fuzzPositionZDev1.universe , [0,0,4])
    fuzzPositionZDev1['sedang'] = fuzz.trapmf(fuzzPositionZDev1.universe,[2,4,8,10])
    fuzzPositionZDev1['jauh'] = fuzz.trimf(fuzzPositionZDev1.universe, [8,14,14])

    # membership function position X
    fuzzPositionXDev2['dekat'] = fuzz.trimf(fuzzPositionXDev2.universe, [0, 0, 2])
    fuzzPositionXDev2['sedang'] = fuzz.trapmf(fuzzPositionXDev2.universe, [0, 2, 3, 5])
    fuzzPositionXDev2['jauh'] = fuzz.trimf(fuzzPositionXDev2.universe, [3, 5, 5])

    # membership function position Z
    fuzzPositionZDev2['dekat'] = fuzz.trimf(fuzzPositionZDev2.universe, [0, 0, 4])
    fuzzPositionZDev2['sedang'] = fuzz.trapmf(fuzzPositionZDev2.universe, [2, 4, 8, 10])
    fuzzPositionZDev2['jauh'] = fuzz.trimf(fuzzPositionZDev2.universe, [8, 14, 14])

    # membership function position X
    fuzzPositionXDev3['dekat'] = fuzz.trimf(fuzzPositionXDev3.universe, [0, 0, 2])
    fuzzPositionXDev3['sedang'] = fuzz.trapmf(fuzzPositionXDev3.universe, [0, 2, 3, 5])
    fuzzPositionXDev3['jauh'] = fuzz.trimf(fuzzPositionXDev3.universe, [3, 5, 5])

    # membership function position Z
    fuzzPositionZDev3['dekat'] = fuzz.trimf(fuzzPositionZDev3.universe, [0, 0, 4])
    fuzzPositionZDev3['sedang'] = fuzz.trapmf(fuzzPositionZDev3.universe, [2, 4, 8, 10])
    fuzzPositionZDev3['jauh'] = fuzz.trimf(fuzzPositionZDev3.universe, [8, 14, 14])

    # membership function longsor
    fuzzLongsor['tidak'] = fuzz.trapmf(fuzzLongsor.universe, [0,0,45,55])
    fuzzLongsor['ya'] = fuzz.trapmf(fuzzLongsor.universe, [45,55,100,100])

    # show
    fuzzPositionXDev1.view()
    fuzzPositionZDev1.view()
    #fuzzPositionXDev2.view()
    #fuzzPositionZDev2.view()
    #fuzzPositionXDev3.view()
    #fuzzPositionZDev3.view()
    fuzzLongsor.view()
    # rule
    '''
    Fuzzy rules
    -----------

    Now, to make these triangles useful, we define the *fuzzy relationship*
    between input and output variables. For the purposes of our example, consider
    three simple rules:

    1. If the velocityX is dekat OR the dekat, then the tip will be low

    '''
    rule1 = ctrl.Rule(fuzzPositionXDev1['dekat'] & fuzzPositionZDev1['dekat'] & fuzzPositionXDev2['dekat'] & fuzzPositionZDev2['dekat'] & fuzzPositionXDev3['dekat'] & fuzzPositionZDev3['dekat'] , fuzzLongsor['tidak'])
    rule2 = ctrl.Rule(fuzzPositionXDev1['jauh'] & fuzzPositionZDev1['jauh'] & fuzzPositionXDev2['jauh'] & fuzzPositionZDev2['jauh'] & fuzzPositionXDev3['jauh'] & fuzzPositionZDev3['jauh'], fuzzLongsor['ya'])
    #rule3 = ctrl.Rule(fuzzPositionZ['sedang'] | fuzzPositionX['sedang'], fuzzLongsor['ya'])
    #rule4 = ctrl.Rule(fuzzPositionZ['sedang'] & fuzzPositionX['dekat'], fuzzLongsor['tidak'])
    #rule5 = ctrl.Rule(fuzzPositionZ['dekat'] & fuzzPositionX['sedang'], fuzzLongsor['tidak'])

    rule6= ctrl.Rule(fuzzPositionXDev1['dekat'] & fuzzPositionZDev1['jauh'] & fuzzPositionXDev2['dekat'] & fuzzPositionZDev2['jauh'] & fuzzPositionXDev3['dekat'] & fuzzPositionZDev3['jauh'], fuzzLongsor['ya'])
    rule7= ctrl.Rule(fuzzPositionXDev1['dekat'] & fuzzPositionZDev1['sedang'] & fuzzPositionXDev2['dekat'] & fuzzPositionZDev2['sedang'] & fuzzPositionXDev3['dekat'] & fuzzPositionZDev3['sedang'], fuzzLongsor['tidak'])
    rule8= ctrl.Rule(fuzzPositionXDev1['jauh'] & fuzzPositionZDev1['sedang'] & fuzzPositionXDev2['jauh'] & fuzzPositionZDev2['sedang'] & fuzzPositionXDev3['jauh'] & fuzzPositionZDev3['sedang'] , fuzzLongsor['ya'])
    rule9= ctrl.Rule(fuzzPositionXDev1['jauh'] & fuzzPositionZDev1['dekat'] & fuzzPositionXDev2['jauh'] & fuzzPositionZDev2['dekat'] & fuzzPositionXDev3['jauh'] & fuzzPositionZDev3['dekat'] , fuzzLongsor['ya'])
    rule10= ctrl.Rule(fuzzPositionXDev1['sedang'] & fuzzPositionZDev1['sedang'] & fuzzPositionXDev2['sedang'] & fuzzPositionZDev2['sedang'] & fuzzPositionXDev3['sedang'] & fuzzPositionZDev3['sedang'], fuzzLongsor['ya'])
    rule11= ctrl.Rule(fuzzPositionXDev1['sedang'] & fuzzPositionZDev1['jauh'] & fuzzPositionXDev2['sedang'] & fuzzPositionZDev2['jauh'] & fuzzPositionXDev3['sedang'] & fuzzPositionZDev3['jauh'],fuzzLongsor['ya'])
    rule12= ctrl.Rule(fuzzPositionXDev1['sedang'] & fuzzPositionZDev1['dekat'] & fuzzPositionXDev2['sedang'] & fuzzPositionZDev2['dekat'] & fuzzPositionXDev3['sedang'] & fuzzPositionZDev3['dekat'],  fuzzLongsor['tidak'])

    #rule13 = ctrl.Rule(fuzzPositionZ['dekat'] & fuzzPositionX['dekat'], fuzzLongsor['tidak'])
    #rule14= ctrl.Rule(fuzzPositionZ['dekat'] & fuzzPositionX['sedang'], fuzzLongsor['tidak'])
    #rule15 = ctrl.Rule(fuzzPositionZ['dekat'] & fuzzPositionX['jauh'], fuzzLongsor['tidak'])
    #rule16 = ctrl.Rule(fuzzPositionZ['sedang'] & fuzzPositionX['jauh'], fuzzLongsor['ya'])
    #rule17 = ctrl.Rule(fuzzPositionZ['jauh'] & fuzzPositionX['dekat'], fuzzLongsor['ya'])
    #rule18 = ctrl.Rule(fuzzPositionZ['jauh'] & fuzzPositionX['sedang'], fuzzLongsor['ya'])
    #rule19 = ctrl.Rule(fuzzPositionZ['jauh'] & fuzzPositionX['jauh'], fuzzLongsor['ya'])

    longsor_control = ctrl.ControlSystem([rule1, rule2,  rule6 , rule7,rule8,rule9,rule10, rule11,rule12])
    decision = ctrl.ControlSystemSimulation(longsor_control)
    print(decision)
    
    # Blocking call that processes network traffic, dispatches callbacks and
    # handles reconnecting.
    # Other loop*() functions are available that give a threaded interface and a
    # manual interface.
    plt.show()
    client.loop_forever()
    #client.loop()