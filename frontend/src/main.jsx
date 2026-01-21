import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

// 1. Import MantineProvider và file CSS của Mantine
import { MantineProvider } from '@mantine/core';
import '@mantine/core/styles.css';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    {/* 2. Bọc App bằng MantineProvider */}
    <MantineProvider>
      <App />
    </MantineProvider>
  </React.StrictMode>,
)