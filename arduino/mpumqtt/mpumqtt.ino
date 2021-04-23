
#include<Wire.h>
#include <ESP8266WiFi.h>
#include <PubSubClient.h>

#define MQTT_MAX_PACKET_SIZE 1024  // fix for MQTT client dropping messages over 128B ganti MQTT MAX PAKCET SIZE di Arduino/Libraries/PubSubClient/src/PubSubClient.h


//https://howtomechatronics.com/tutorials/arduino/arduino-and-mpu6050-accelerometer-and-gyroscope-tutorial/
const int MPU = 0x68; // MPU6050 I2C address
float AccX, AccY, AccZ;
float GyroX, GyroY, GyroZ;

float accAngleX, accAngleY, gyroAngleX, gyroAngleY, gyroAngleZ;
float roll, pitch, yaw;
float AccErrorX, AccErrorY, GyroErrorX, GyroErrorY, GyroErrorZ;
float elapsedTime, currentTime, previousTime;
int c = 0;

// Wifi And MQTT Configuration
const char* ssid = "Yuhu"; // Enter your WiFi name
const char* password =  "blahblah"; // Enter WiFi password
const char* mqttServer = "192.168.43.56";
const int mqttPort = 1883;

#define device_name "Device2"
 char* topic_name_accX = "Device2/accX";
 char* topic_name_accY = "Device2/accY";
 char* topic_name_accZ = "Device2/accZ";

 unsigned long lastReconnectAttempt = 0;

WiFiClient espClient;
PubSubClient client(espClient);

void setup() {
    Serial.begin(9600);
    Serial.println("MPU MQTT");
    setup_MPU();
    //calculate_IMU_error();
    setup_wifi();
    setup_mqtt();
}

void setup_wifi(){
  delay(10);
  // Connect to WiFi network
  Serial.println();
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(500);
  }
}

void setup_mqtt(){
  client.setServer(mqttServer, mqttPort);

  while (!client.connected()) {
    Serial.println("Connecting to MQTT...");
 
    if (client.connect(device_name)) {
 
      Serial.println("connected");  
 
    } else {
 
      Serial.print("failed with state ");
      Serial.print(client.state());
      delay(2000);
 
    }
  }
}


void setup_MPU(){
   Wire.begin();                      // Initialize comunication
  Wire.beginTransmission(MPU);       // Start communication with MPU6050 // MPU=0x68
  Wire.write(0x6B);                  // Talk to the register 6B
  Wire.write(0x00);                  // Make reset - place a 0 into the 6B register
  Wire.endTransmission(true);        //end the transmission

  calculate_IMU_error();
    /*
   * AccErrorX: -0.04
    AccErrorY: 0.06
    GyroErrorX: 0.01
    GyroErrorY: 0.03
    GyroErrorZ: -0.03
   */
  delay(500);
}

void calculate_IMU_error() {
  // We can call this funtion in the setup section to calculate the accelerometer and gyro data error. From here we will get the error values used in the above equations printed on the Serial Monitor.
  // Note that we should place the IMU flat in order to get the proper values, so that we then can the correct values
  // Read accelerometer values 200 times
  while (c < 200) {
    Wire.beginTransmission(MPU);
    Wire.write(0x3B);
    Wire.endTransmission(false);
    Wire.requestFrom(MPU, 6, true);
    AccX = (Wire.read() << 8 | Wire.read()) / 16384.0 ;
    AccY = (Wire.read() << 8 | Wire.read()) / 16384.0 ;
    AccZ = (Wire.read() << 8 | Wire.read()) / 16384.0 ;
    // Sum all readings
    AccErrorX = AccErrorX + ((atan((AccY) / sqrt(pow((AccX), 2) + pow((AccZ), 2))) * 180 / PI));
    AccErrorY = AccErrorY + ((atan(-1 * (AccX) / sqrt(pow((AccY), 2) + pow((AccZ), 2))) * 180 / PI));
    c++;
  }
  //Divide the sum by 200 to get the error value
  AccErrorX = AccErrorX / 200;
  AccErrorY = AccErrorY / 200;
  c = 0;
  // Read gyro values 200 times
  while (c < 200) {
    Wire.beginTransmission(MPU);
    Wire.write(0x43);
    Wire.endTransmission(false);
    Wire.requestFrom(MPU, 6, true);
    GyroX = Wire.read() << 8 | Wire.read();
    GyroY = Wire.read() << 8 | Wire.read();
    GyroZ = Wire.read() << 8 | Wire.read();
    // Sum all readings
    GyroErrorX = GyroErrorX + (GyroX / 131.0);
    GyroErrorY = GyroErrorY + (GyroY / 131.0);
    GyroErrorZ = GyroErrorZ + (GyroZ / 131.0);
    c++;
  }
  //Divide the sum by 200 to get the error value
  GyroErrorX = GyroErrorX / 200;
  GyroErrorY = GyroErrorY / 200;
  GyroErrorZ = GyroErrorZ / 200;
  // Print the error values on the Serial Monitor
  Serial.print("AccErrorX: ");
  Serial.println(AccErrorX);
  Serial.print("AccErrorY: ");
  Serial.println(AccErrorY);
  Serial.print("GyroErrorX: ");
  Serial.println(GyroErrorX);
  Serial.print("GyroErrorY: ");
  Serial.println(GyroErrorY);
  Serial.print("GyroErrorZ: ");
  Serial.println(GyroErrorZ);
}

void read_acc(){
  // === Read acceleromter data === //
  Wire.beginTransmission(MPU);
  Wire.write(0x3B); // Start with register 0x3B (ACCEL_XOUT_H)
  Wire.endTransmission(false);
  Wire.requestFrom(MPU, 6, true); // Read 6 registers total, each axis value is stored in 2 registers
  //For a range of +-2g, we need to divide the raw values by 16384, according to the datasheet
  AccX = (Wire.read() << 8 | Wire.read()) / 16384.0; // X-axis value
  AccY = (Wire.read() << 8 | Wire.read()) / 16384.0; // Y-axis value
  AccZ = (Wire.read() << 8 | Wire.read()) / 16384.0; // Z-axis value

  // correct accelero
  AccX = AccX - 2.14; // AccErrorX 10.42

  AccY = AccY + 0.92; // AccErrorY -31.51

  
}

String dataAccX,dataAccY,dataAccZ;
int counter = 0;
void tampung_data(){
  if (counter <= 30){
    if (counter <= 29){
      dataAccY = dataAccY + String(AccY,2) + ",";
      dataAccX = dataAccX + String(AccX,2) + ",";
      dataAccZ = dataAccZ + String(AccY,2) + ",";
    } else {
      dataAccY = dataAccY + String(AccY,2);
      dataAccX = dataAccX + String(AccX,2);
      dataAccZ = dataAccZ + String(AccY,2);
    }
  } else {
    send_data();
    counter = 0;
    dataAccY = "";
    dataAccX = "";
    dataAccZ = "";
  }
  counter++;

}

/**
  Publish data to MQTT in easy way
**/
char dataPublish[150];
void publishMQTT(char* topics, String data){
   data.toCharArray(dataPublish, data.length() + 1);
   client.publish(topics, dataPublish);
}

void send_data(){
  publishMQTT(topic_name_accX, dataAccX); 
  publishMQTT(topic_name_accY, dataAccY);
  publishMQTT(topic_name_accZ, dataAccZ);
}

int count_data = 0;
void process_acc(){
  count_data = 0;

  dataAccX = " ";
  dataAccY = " ";
  dataAccZ = " ";


  // wait until 30 times
  while (count_data < 30) {
    read_acc();
    Serial.print("\t MPU : "); Serial.print(AccX,2); 
    Serial.print(","); Serial.print(AccY,2);
    Serial.print(","); Serial.println(AccZ,2);
    
    if(count_data < 29){
      dataAccX += (String(AccX,2)+",");
      dataAccZ += (String(AccZ,2)+",");
      dataAccY += (String(AccY,2)+",");
    } else {
      dataAccX += (String(AccX,2));
      dataAccZ += (String(AccZ,2));
      dataAccY += (String(AccY,2));
    }
    count_data++;
    delay(20);
  }

  // send data to broker
  char buffer_AccX[dataAccX.length()+1];
  dataAccX.toCharArray(buffer_AccX,dataAccX.length()+1);
  client.publish(topic_name_accX,buffer_AccX);

  char buffer_AccY[dataAccY.length()+1];
  dataAccY.toCharArray(buffer_AccY,dataAccY.length()+1);
  client.publish(topic_name_accY,buffer_AccY);

  char buffer_AccZ[dataAccZ.length()+1];
  dataAccZ.toCharArray(buffer_AccZ,dataAccZ.length()+1);
  client.publish(topic_name_accZ,buffer_AccZ);

  
  
}

void callback(char* topic, byte* payload, unsigned int length) {
 
  Serial.print("Message arrived in topic: ");
  Serial.println(topic);
 
  Serial.print("Message:");
  for (int i = 0; i < length; i++) {
    Serial.print((char)payload[i]);
  }
 
  Serial.println();
  Serial.println("-----------------------");
 
}

boolean reconnect() {
  if (client.connect(device_name)) {
    //if (client.connect(device_name,mqtt_user,mqtt_password)) {
    //client.subscribe(mqtt_topic_callibration);
  }
  return client.connected();
}

void loop() {
   // Loop until we're reconnected
  if (!client.connected()) {
    long now = millis();
    if (now - lastReconnectAttempt > 5000) {
      lastReconnectAttempt = now;
      // Attempt to reconnect
      if (reconnect()) {
        lastReconnectAttempt = 0;
      }
    }
    Serial.println("Device not connecting...");
  } else {
    // Client connected
    //Serial.println("MQTT Connect...");

    //read_acc(); // baca mpu with millis
    process_acc();
  
    client.loop();
  }
 
    delay(50);
}
