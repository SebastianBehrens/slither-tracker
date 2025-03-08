import React, {useState} from 'react'
import ReactECharts from 'echarts-for-react';
import ReactEChartsCore from 'echarts-for-react/lib/core';
import * as echarts from 'echarts/core';
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

  const [count, setCount] = useState();
  const [studentId, setStudentId] = useState("");
  const [gradesData, setGradesData] = useState([]);

  const getGradesData = (event) => {
    if (event.key === 'Enter') {
      const url = new URL('http://127.0.0.1:8000/grade_statistics/');
      url.searchParams.append('student_id', event.target.value);
      fetch(url).then(
        response => response.json()
      ).then(
        data => {
          console.log(data)
          setGradesData(data)
          setStudentId()
        }

      )
    }
  }
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: [
      {
        type: 'category',
        data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        axisTick: {
          alignWithLabel: true
        }
      }
    ],
    yAxis: [
      {
        type: 'value'
      }
    ],
    series: [
      {
        name: 'Grades',
        type: 'bar',
        barWidth: '60%',
        data: gradesData
      }
    ]
  }
  return (
    <div className='App'>
      <input
        type='text'
        className='input'
        onChange={e => setStudentId(e.target.value)}
        value={studentId}
        onKeyDown={getGradesData}
      />
      <div>
        {typeof studentId === "undefined" ? (
          <p>Enter a student ID to retrieve grades.</p>
        ) : (
          <div>
            <p>Grades for student {studentId}:</p>
            <ReactECharts
              option={option}
            />
          </div>
        )}
      </div>
    </div>
  )
}

export default App