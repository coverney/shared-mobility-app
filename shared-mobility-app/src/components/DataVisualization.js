import React, {Component} from 'react';
import Button from 'react-bootstrap/Button';
import './DataVisualization.css';
import { MapContainer, TileLayer, Marker, Popup, Rectangle, Tooltip } from 'react-leaflet'
import { CSVLink } from 'react-csv'
// import GeoMercator from './GeoMercator'

class DataVisualization extends Component {
  // create state variable
  constructor(props) {
    super(props);
    this.state = {
        center: [41.82972307181493, -71.41681396120897],
        data: [],
        rectangles: [],
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

  getRectangleData() {
    fetch('/return-rectangles').then(res => res).then(data => {
      console.log(data);
      var a = data.body.getReader();
      a.read().then(({ done, value }) => {
        var raw_data = new TextDecoder("utf-8").decode(value);
        // console.log(raw_data);
        var rects = JSON.parse(raw_data).data
        this.setState({rectangles: rects});
      })
    });
  }

  render() {
    // const rectangle = [
    //   [41.835, -71.415],
    //   [41.825, -71.405],
    // ]
    // const blackOptions = { color: 'black' }

    // const rectangles = [
    //   {
    //     name: "Rectangle 1",
    //     color: 'black',
    //     bounds: [[41.835, -71.415],[41.825, -71.405]]
    //   },
    //   {
    //     name: "Rectangle 2",
    //     color: 'red',
    //     bounds: [[41.825, -71.415],[41.815, -71.405]]
    //   },
    // ]

    const RectangleListTrips = ({ data }) => {
      return (
        <span>
          {data.map((item, i) => {
            return (
              <Rectangle key={i} bounds={item.bounds} color={item.trips_color}>
                <Tooltip sticky>
                  Lat: {item.lat}, Long: {item.lng} <br />
                  Mean Trips/Day: {item.trips}
                </Tooltip>
              </Rectangle>
            );
          })}
        </span>
      );
    }

    const RectangleListAdjTrips = ({ data }) => {
      return (
        <span>
          {data.map((item, i) => {
            return (
              <Rectangle key={i} bounds={item.bounds} color={item.adj_trips_color}>
                <Tooltip sticky>
                  Lat: {item.lat}, Long: {item.lng} <br />
                  Mean Trips/Day: {item.adj_trips}
                </Tooltip>
              </Rectangle>
            );
          })}
        </span>
      );
    }

    return (
      <>
        <div className="DataVisualization">
          <p className="DataVisualization-text">
            Data visualization dashboard goes here!
          </p>
          <p className="DataVisualization-text">
            Scooter Number of Trips Map
          </p>
          {/* <GeoMercator width={1000} height={600} events={true}/> */}
          <MapContainer
            center={this.state.center}
            zoom={13}
            scrollWheelZoom={false}
            whenReady={this.getRectangleData.bind(this)}>
            <TileLayer
              attribution='&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            {/* <Marker position={this.state.center}>
              <Popup>
                A pretty CSS3 popup. <br /> Easily customizable.
              </Popup>
            </Marker> */}
            {/* <Rectangle bounds={rectangle} pathOptions={blackOptions} /> */}
            <RectangleListTrips data={this.state.rectangles} />
          </MapContainer>
          <p className="DataVisualization-text">
            Scooter Estimated Demand Map
          </p>
          <MapContainer
            center={this.state.center}
            zoom={13}
            scrollWheelZoom={false}>
            <TileLayer
              attribution='&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            <RectangleListAdjTrips data={this.state.rectangles} />
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
