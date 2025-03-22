import React, {useState} from 'react'
import ReactECharts from 'echarts-for-react';
import ReactEChartsCore from 'echarts-for-react/lib/core';
import * as echarts from 'echarts/core';
import { motion } from "framer-motion";
import {
  BarChart,
} from 'echarts/charts';
import {
  GridComponent,
  TooltipComponent,
  TitleComponent,
  DatasetComponent
} from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';
import './App.css'

echarts.use(
  [TitleComponent, TooltipComponent, GridComponent, BarChart, CanvasRenderer]
);


function App() {

  const [serverId, setServerId] = useState("");
  const [isHovered, setIsHovered] = useState(false);

  return (
    <div className='App'>
      <input
        type='text'
        className='input'
        onChange={e => setServerId(e.target.value)}
        value={serverId}
        // onKeyDown={getServerId}
      />
      <div>
        {typeof serverId === "undefined" ? (
          <p>Enter a server ID to retrieve data.</p>
        ) : (
          <p>Data for server {serverId}:</p>
        )}
      </div>
      <div className="relative w-64 h-32 bg-blue-500 text-white rounded-lg shadow-lg flex items-center justify-center cursor-pointer"
          onMouseEnter={() => setIsHovered(true)}
          onMouseLeave={() => setIsHovered(false)}>

        <span className="text-xl font-bold">Hover over me</span>

        {isHovered && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
            className="absolute top-full mt-2 w-72 p-4 bg-white text-gray-800 rounded-lg shadow-xl"
          >
            <h3 className="font-semibold text-lg">Detailed Explanation</h3>
            <p className="text-sm">This is a more detailed description that appears when you hover over the title box.</p>
          </motion.div>
        )}
      </div>
    </div>
  )
}

export default App