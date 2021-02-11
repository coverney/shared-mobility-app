import React, {Component} from 'react';
import Button from 'react-bootstrap/Button';
import './DataVisualization.css';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet'
// import GeoMercator from './GeoMercator'

class DataVisualization extends Component {
  // create state variable
  constructor(props) {
    super(props);
    this.state = {
        center: [41.82972307181493, -71.41681396120897],
    };
  }

  downloadData() {
    fetch('/return-demand-file').then(res => res).then(data => {
      console.log(data);
    });
  }

  render() {
    return (
      <>
        <div className="DataVisualization">
          <p className="DataVisualization-text">
            Data visualization dashboard goes here!
          </p>
          {/* <GeoMercator width={1000} height={600} events={true}/> */}
          <MapContainer center={this.state.center} zoom={13} scrollWheelZoom={false}>
            <TileLayer
              attribution='&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            <Marker position={this.state.center}>
              <Popup>
                A pretty CSS3 popup. <br /> Easily customizable.
              </Popup>
            </Marker>
          </MapContainer>

          <Button onClick={this.downloadData} id="downloadButton">Download Data</Button>
        </div>
      </>
    );
  }
}

export default DataVisualization;
