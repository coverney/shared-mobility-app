// Initiate via yarn start
import React from 'react';
import './App.css';
import Upload from './components/Upload'
import DataVisualization from './components/DataVisualization'
import {
  BrowserRouter as Router,
  Switch,
  Route
} from "react-router-dom";

function App() {
  return (
    <div>
      <Router>
        <Switch>
          {/* If the current URL is /data, this route is rendered
          while the rest are ignored. */}
          <Route path="/data">
            <DataVisualization />
          </Route>
          {/* If none of the previous routes render anything,
          this route acts as a fallback.

          Important: A route with path="/" will *always* match
          the URL because all URLs begin with a /. So that's
          why we put this one last of all */}
          <Route path="/">
            <div className="App">
              <Upload />
            </div>
          </Route>
        </Switch>
      </Router>
    </div>
  );
}

export default App;
