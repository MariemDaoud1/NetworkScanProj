// frontend/react-frontend/src/App.js
import React, { useState } from 'react';
import './App.css';

function App() {
  const [target, setTarget] = useState('');
  const [ports, setPorts] = useState('1-100');
  const [scanType, setScanType] = useState('-sT');
  const [result, setResult] = useState(null);
  const [info, setInfo] = useState(null);
  const [hosts, setHosts] = useState([]);
  const [error, setError] = useState('');

  const handleScan = async () => {
    setResult(null); setInfo(null); setHosts([]); setError('');
    try {
      const response = await fetch(`http://127.0.0.1:8000/scan/${target}`);
      const data = await response.json();
      data.error ? setError(data.error) : setResult(data);
    } catch (err) {
      setError('Failed to connect to the server.');
    }
  };

  const handleInfo = async () => {
    setResult(null); setInfo(null); setHosts([]); setError('');
    try {
      const response = await fetch(`http://127.0.0.1:8000/info/${target}`);
      const data = await response.json();
      data.error ? setError(data.error) : setInfo(data);
    } catch (err) {
      setError('Failed to connect to the server.');
    }
  };

  const handleCustomScan = async () => {
    setResult(null); setInfo(null); setHosts([]); setError('');
    try {
      const response = await fetch('http://127.0.0.1:8000/custom-scan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ target, ports, scan_type: scanType }),
      });
      const data = await response.json();
      data.error ? setError(data.error) : setResult(data);
    } catch (err) {
      setError('Failed to connect to the server.');
    }
  };

  const handleGetHosts = async () => {
    setResult(null); setInfo(null); setHosts([]); setError('');
    try {
      const response = await fetch('http://127.0.0.1:8000/all-hosts');
      const data = await response.json();
      setHosts(data.scanned_hosts || []);
      if (data.message) setError(data.message);
    } catch (err) {
      setError('Failed to connect to the server.');
    }
  };

  return (
    <div className="App">
      <h1>Simple Network Scanner</h1>
      <input
        type="text"
        placeholder="Enter IP or hostname "
        value={target}
        onChange={(e) => setTarget(e.target.value)}
      />
      <div>
        <input
          type="text"
          placeholder="Port range"
          value={ports}
          onChange={(e) => setPorts(e.target.value)}
        />
        <input
          type="text"
          placeholder="Scan type"
          value={scanType}
          onChange={(e) => setScanType(e.target.value)}
        />
      </div>
      <button onClick={handleScan}>Basic Scan</button>
      <button onClick={handleInfo}>Get Info</button>
      <button onClick={handleCustomScan}>Custom Scan</button>
      <button onClick={handleGetHosts}>Show Scanned Hosts</button>

      {result && (
        <div>
          <h3>Scan Results for {result.host}</h3>
          <p>Status: {result.status}</p>
          <p>Open Ports: {result.open_ports.length > 0 ? result.open_ports.join(', ') : 'None'}</p>
        </div>
      )}

      {info && (
        <div>
          <h3>Info for {info.host}</h3>
          <p>Status: {info.status}</p>
          <p>Hostname: {info.hostname}</p>
        </div>
      )}

      {hosts.length > 0 && (
        <div>
          <h3>Scanned Hosts</h3>
          <p>{hosts.join(', ')}</p>
        </div>
      )}

      {error && <p style={{ color: 'red' }}>Error: {error}</p>}
    </div>
  );
}

export default App;