#include "esphome.h"
//  //#include "Wire.h"
// //#include <I2CSoilMoistureSensor.h>
//
// //class ChirpCustomSensor : public PollingComponent, public Sensor {
// class ChirpCustomSensor: public Component, public Sensor {
//
//   public: Sensor * capacitance_sensor = new Sensor();
//   Sensor * temperature_sensor = new Sensor();
//   //Sensor *light_sensor = new Sensor();
//   //  I2CSoilMoistureSensor sensor;
//   //ChirpCustomSensor() : PollingComponent(8000) { }
//
//   void setup() override {
//     // Initialize the device here. Usually Wire.begin() will be called in here,
//     // though that call is unnecessary if you have an 'i2c:' entry in your config
//     Wire.setClockStretchLimit(5000); // https://github.com/Miceuz/i2c-moisture-sensor#note-for-esp8266-based-systems
//     Wire.begin();
//     Wire.setClockStretchLimit(5000); // https://github.com/Miceuz/i2c-moisture-sensor#note-for-esp8266-based-systems
//
//     // sensor.begin(); // reset sensor
//     delay(1000); // give some time to boot up
//   }
//
//   void writeI2CRegister8bit(int addr, int value) {
//     Wire.beginTransmission(addr);
//     Wire.write(value);
//     Wire.endTransmission();
//   }
//
//   unsigned int readI2CRegister16bit(int addr, int reg) {
//     delay(1500);
//     Wire.beginTransmission(addr);
//     Wire.write(reg);
//     Wire.endTransmission();
//     delay(1100);
//     Wire.requestFrom(addr, 2);
//     unsigned int t = Wire.read() << 8;
//     t = t | Wire.read();
//     return t;
//     delay(1100);
//   }
//   void loop() override {
//
//     //  void update() override {
//     // This is the actual sensor reading logic.
//     delay(1100);
//     unsigned int capacitance = readI2CRegister16bit(0x20, 0); //read capacitance register
//     capacitance_sensor -> publish_state(capacitance);
//     //    unsigned int capacitance = sensor.getCapacitance(); //read capacitance register
//     //    capacitance_sensor->publish_state(capacitance);
//     delay(5000);
//     // unsigned int temperature = readI2CRegister16bit(0x20, 5); //read temperature register
//     // temperature_sensor - > publish_state(temperature);
//
//     //writeI2CRegister8bit(0x20, 3); //request light measurement
//     //delay(9000);                   //this can take a while
//     //unsigned int light = readI2CRegister16bit(0x20, 4);
//     //light_sensor->publish_state(light);
//   }
// };

class MyCustomSensor : public PollingComponent, public Sensor {
 public:
  // constructor
  MyCustomSensor() : PollingComponent(10000) {}

  void writeI2CRegister8bit(int addr, int value) {
    Wire.beginTransmission(addr);
    Wire.write(value);
    Wire.endTransmission();
  }

  unsigned int readI2CRegister16bit(int addr, int reg) {
    Wire.beginTransmission(addr);
    Wire.write(reg);
    Wire.endTransmission();
    delay(1100);
    Wire.requestFrom(addr, 2);
    unsigned int t = Wire.read() << 8;
    t = t | Wire.read();
    return t;
  }


  void setup() override {
    // This will be called by App.setup()
    Wire.setClockStretchLimit(5000); // https://github.com/Miceuz/i2c-moisture-sensor#note-for-esp8266-based-systems
    Wire.begin();
  }
  void update() override {
    // This will be called every "update_interval" milliseconds.
    unsigned int capacitance = readI2CRegister16bit(0x20, 0); //read capacitance register

    publish_state(capacitance); //read capacitance register
    // writeI2CRegister8bit(0x20, 3); //request light measurement
    // delay(9000);                   //this can take a while
    // Serial.print(", ");
    // Serial.println(readI2CRegister16bit(0x20, 4)); //read light register
    // delay(500);
  }
};
