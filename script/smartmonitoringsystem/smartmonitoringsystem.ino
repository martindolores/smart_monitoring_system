String tempC;
String lux;
String soil;

int changeTemp(String value)
{
    tempC = value;
    return 1;
}

int changeSoil(String value)
{
    soil = value;
    return 1;
}

int changeLux(String value)
{
    lux = value;
    return 1;
}


bool tempSuccess = Particle.function("changeTemp", changeTemp);
bool soilSuccess = Particle.function("changeSoil", changeSoil);
bool luxSuccess = Particle.function("changeLux", changeLux);


void setup() {
    //No Setup
}        

void loop() {
    Particle.publish("temp", String(tempC));
    Particle.publish("light", String(lux));
    Particle.publish("soil", String(soil));
    delay(10000);
}
