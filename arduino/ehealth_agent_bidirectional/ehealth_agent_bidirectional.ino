#include <PinChangeInt.h>
#include <eHealth.h>

void setup() {  
  /*eHealth.readBloodPressureSensor(); delay(100);
  eHealth.readGlucometer(); delay(100);*/

  // Init sensors
  eHealth.initPulsioximeter();
  
  // Attach the inttruptions for using the pulsioximeter.
  PCintPort::attachInterrupt(6, readPulsioximeter, RISING);
  delay(100);

  Serial.begin(115200);

  // Flush the buffer.
  Serial.flush();
  while(1) {
    if (Serial.available()) Serial.read();
    else break;
  }

  delay(200);
}

void loop() {
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');

    if (command.startsWith("MEAS:")) {
      // Extract measurement type.
      String measType = command.substring(5);

      /* 
       * Read the measurement. 
       */
      
      if (measType.startsWith("temperature")) {
        float temperature = eHealth.getTemperature();
        Serial.print(temperature);
      }
      
      else if (measType.startsWith("pulse")) {
        // Print Fromat: Pulse,SpO2
        float pulse = eHealth.getBPM();
        float spo2 = eHealth.getOxygenSaturation();
        Serial.print(pulse); Serial.print(",");
        Serial.print(spo2);
      }
      
      else if (measType.startsWith("gsr")) {
        float conductance = eHealth.getSkinConductance();
        float resistance = eHealth.getSkinResistance();
        int kiloResistance = (int)(resistance/1000);
        float conductanceVol = eHealth.getSkinConductanceVoltage();
        Serial.print(conductance); Serial.print(",");
        Serial.print(resistance); Serial.print(",");
        Serial.print(kiloResistance); Serial.print(",");
        Serial.print(conductanceVol);
      }

      else if (measType.startsWith("ecg")) {
        float ecg = eHealth.getECG();
        Serial.print(ecg);
      }
      
      else if (measType.startsWith("emg")) {
        float emg = eHealth.getEMG();
        Serial.print(emg);
      }
      
      Serial.print("\n");
      Serial.flush();
    }
  }
}

int cont = 0;
void readPulsioximeter() {
  cont ++;
  if (cont == 50) { //Get only of one 50 measures to reduce the latency
    eHealth.readPulsioximeter();
    cont = 0;
  }
}
