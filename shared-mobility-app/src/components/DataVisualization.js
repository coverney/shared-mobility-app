import React, {Component} from 'react';
import './DataVisualization.css';
import GeoMercator from './GeoMercator'

class DataVisualization extends Component {
  render() {
    return (
      <>
        <div className="DataVisualization">
          <p className="DataVisualization-text">
            Data visualization dashboard goes here!
          </p>
          <GeoMercator width={1000} height={600} events={true}/>
        </div>
      </>
    );
  }
}

export default DataVisualization;
