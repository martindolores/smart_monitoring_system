import Chart from 'chart.js/auto';
import { Line } from 'react-chartjs-2';
import { useState, useEffect } from 'react';

const CustomChart = (props) => {
  const [data, setData] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(
          `https://api.thingspeak.com/channels/${props.channelId}/fields/${props.field}.json?api_key=${props.apiKey}&results=1`
        );
        const json = await response.json();
        setData((prevData) => [...prevData, ...json.feeds]);
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

    const interval = setInterval(fetchData, 5000); // Fetch data every 5 seconds

    return () => {
      clearInterval(interval); // Clean up the interval on component unmount
      setData([]);
    };
  }, [props.apiKey, props.channelId, props.field]);

  const chartData = {
    labels: data.map((feed) => feed.entry_id.toString()),
    datasets: [
      {
        label: 'Data',
        data: data.map((feed) => feed[`field${props.field}`]), //need to change field here
        borderColor: 'rgba(75, 192, 192, 1)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
      },
    ],
  };

  return (
    <div className='chart-container'>
      <Line data={chartData} />
    </div>
  );
};

export default CustomChart;
