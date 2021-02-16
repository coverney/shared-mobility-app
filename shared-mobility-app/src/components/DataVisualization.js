import React, {Component} from 'react';
import Button from 'react-bootstrap/Button';
import './DataVisualization.css';
import { MapContainer, TileLayer, Marker, Popup, Rectangle } from 'react-leaflet'
import { CSVLink } from 'react-csv'
// import GeoMercator from './GeoMercator'

class DataVisualization extends Component {
  // create state variable
  constructor(props) {
    super(props);
    this.state = {
        center: [41.82972307181493, -71.41681396120897],
        data: [],
    };
    this.csvLink = React.createRef();
  }

  downloadData() {
    fetch('/return-demand-file').then(res => res).then(data => {
      // console.log(data);
      var a = data.body.getReader();
      a.read().then(({ done, value }) => {
        var raw_data = new TextDecoder("utf-8").decode(value);
        // console.log(raw_data);
        this.setState({data: raw_data});
        // click the CSVLink component to trigger the CSV download
        this.csvLink.current.link.click()
      })
    });
  }

  render() {
    const rectangle = [
      [41.835, -71.415],
      [41.825, -71.405],
    ]
    const blackOptions = { color: 'black' }

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
            <Rectangle bounds={rectangle} pathOptions={blackOptions} />
          </MapContainer>

          <Button onClick={this.downloadData.bind(this)} id="downloadButton">Download Data</Button>

          <CSVLink
            data={this.state.data}
            filename="estimated_demand.csv"
            className="hidden"
            ref={this.csvLink}
            target="_blank"
         />

        </div>
      </>
    );
  }
}

export default DataVisualization;
