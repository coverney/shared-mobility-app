import React from 'react';
import logo from './upload_icon.png';
import './App.css';
import Upload from './components/Upload'

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <p>Upload Data</p>
      </header>
      <Upload />
    </div>
  );
}

export default App;
