import React, { useState, useEffect, useRef } from "react";
import CustomChart from "./CustomChart";
import "./Dashboard.css";
import "./App.css";

function Dashboard() {
  const [tempData, setTempData] = useState(null);
  const [lightData, setLightData] = useState(null);
  const [soilData, setSoilData] = useState(null);
  const [tempView, setTempView] = useState(false);
  const [lightView, setLightView] = useState(false);
  const [soilView, setSoilView] = useState(false);
  const [deviceInfo, setDeviceInfo] = useState(null);
  const tempChartRef = useRef(null);
  const lightChartRef = useRef(null);
  const soilChartRef = useRef(null);

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
    const eventSource = new EventSource(
      "https://api.particle.io/v1/devices/events?access_token=0796096240632ac381c0ff9462594a1951a0d25c"
    );

    const fetchDeviceInfo = async () => {
      try {
        const response = await fetch(
          "https://api.particle.io/v1/devices/e00fce689d45860e19261d67?access_token=0796096240632ac381c0ff9462594a1951a0d25c"
        );
        const data = await response.json();
        setDeviceInfo(data);
      } catch (error) {
        console.error("Error fetching device information:", error);
      }
    };

    eventSource.addEventListener("temp", (event) => {
      const data = JSON.parse(event.data);
      setTempData(data);
    });

    eventSource.addEventListener("light", (event) => {
      const data = JSON.parse(event.data);
      setLightData(data);
    });

    eventSource.addEventListener("soil", (event) => {
      const data = JSON.parse(event.data);
      setSoilData(data);
    });

    fetchDeviceInfo();

    return () => {
      eventSource.close();
    };
  }, []);

  return (
    <div>
      <h1 className="title">Smart Watering System Dashboard</h1>
      {deviceInfo && <div className="title">Name: {deviceInfo.name}</div>}
      <div className="container">
        <div className="label">
          Temperature:{" "}
          <button onClick={callParticleTempFunction}>Toggle</button>
        </div>
        <div className="column">
          {tempData && tempView ? (
            <p>
              Value: {tempData.data} | Last Published: {tempData.published_at}
              <CustomChart ref={tempChartRef} channelId="2154381" apiKey="3YY7HM2MSLKY81Z5" />
            </p>
          ) : (
            <div>Disabled</div>
          )}
        </div>
        <div className="label">
          Light Lux: <button onClick={callParticleLightFunction}>Toggle</button>
        </div>
        <div className="column">
          {lightData && lightView ? (
            <p>
              Value: {lightData.data} | Last Published: {lightData.published_at}
              <CustomChart ref={lightChartRef} channelId="2154784" apiKey="ZV2BLURW5LHJXG8L" />
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
              Value: {soilData.data} | Last Published: {soilData.published_at}
              <CustomChart ref={soilChartRef} channelId="2154785" apiKey="VZ95TOSMWEJGII5E" />
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
