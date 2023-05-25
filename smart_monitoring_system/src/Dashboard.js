import React, { useState, useEffect, useRef } from "react";
import CustomChart from "./CustomChart";
import "./Dashboard.css";
import "./App.css";

const plantData = [
  {
    id: 1,
    name: "plant 1",
    channelId: "{THINGSPEAK_CHANNELID_ONE}",
    apiKey: "{THINGSPEAK_API_KEY_ONE}"
  },
  {
    id: 2,
    name: "plant 2",
    channelId: "{THINGSPEAK_CHANNELID_TWO}",
    apiKey: "{THINGSPEAK_API_KEY_TWO}"
  },
  {
    id: 3,
    name: "plant 3",
    channelId: "{THINGSPEAK_CHANNELID_THREE}",
    apiKey: "{THINGSPEAK_API_KEY_THREE}"
  }
];

function Dashboard() {
  const [tempData, setTempData] = useState([]);
  const [lightData, setLightData] = useState([]);
  const [soilData, setSoilData] = useState([]);
  const [tempView, setTempView] = useState(false);
  const [lightView, setLightView] = useState(false);
  const [soilView, setSoilView] = useState(false);
  const [selectedPlant, setSelectedPlant] = useState("plant 1");
  const [plant, setPlant] = useState(plantData.find((p) => p.name === selectedPlant))
  const tempChartRef = useRef(null);
  const lightChartRef = useRef(null);
  const soilChartRef = useRef(null);

  const handleChange = (event) => {
    setSelectedPlant(event.target.value);
  }

  useEffect(() => {
    setPlant(plantData.find((p) => p.name === selectedPlant)); 
    setTempData([]);
    setLightData([]);
    setSoilData([]);
    console.log(selectedPlant);
  }, [selectedPlant]);

  const callParticleTempFunction = () => {
    setTempView((prevState) => !prevState);
  };

  const callParticleSoilFunction = () => {
    setSoilView((prevState) => !prevState);
  };

  const callParticleLightFunction = () => {
    setLightView((prevState) => !prevState);
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(
          `https://api.thingspeak.com/channels/${plant.channelId}/feeds.json?api_key=${plant.apiKey}&results=1`
        );
        const json = await response.json();
        console.log(json);
        setTempData([json.feeds[0].field1, json.feeds[0].created_at]);
        setLightData([json.feeds[0].field2, json.feeds[0].created_at]);
        setSoilData([json.feeds[0].field3, json.feeds[0].created_at]);
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };
    const interval = setInterval(fetchData, 5000); // Fetch data every 5 seconds

    return () => {
      clearInterval(interval); // Clean up the interval on component unmount
    };
  }, [plant]);

  return (
    <div>
      <h1 className="title">Smart Monitoring System Dashboard</h1>
      
      <div className="container">
      <select 
        value={selectedPlant}
        onChange={handleChange}
        >
          {plantData.map((plant) => (
            <option key={plant.id} value={plant.name}>
              {plant.name.toUpperCase()}
          </option>
          ))}
        </select>
        <div className="label">
          Temperature:{" "}
          <button onClick={callParticleTempFunction}>Toggle</button>
        </div>
        <div className="column">
          {tempData && tempView ? (
            <p>
              Value: {tempData[0]} | Last Published: {tempData[1]}
              <CustomChart ref={tempChartRef} channelId={plant.channelId} apiKey={plant.apiKey} field="1" />
            </p>
          ) : (
            <div>Disabled</div>
          )}
        </div>
        <div className="label">
          Light Lux: <button onClick={callParticleLightFunction}>Toggle</button>
        </div>
        <div className="column">
          {lightView ? (
            <p>
              Value: {lightData[0]} | Last Published: {lightData[1]}
              <CustomChart ref={lightChartRef} channelId={plant.channelId} apiKey={plant.apiKey} field="2" />
            </p>
          ) : (
            <div>Disabled</div>
          )}
        </div>
        <div className="label">
          Moisture: <button onClick={callParticleSoilFunction}>Toggle</button>
        </div>
        <div className="column">
          {soilData && soilView ? (
            <p>
              Value: {soilData[0]} | Last Published: {soilData[1]}
              <CustomChart ref={soilChartRef} channelId={plant.channelId} apiKey={plant.apiKey} field="3" />
            </p>
          ) : (
            <div>Disabled</div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
