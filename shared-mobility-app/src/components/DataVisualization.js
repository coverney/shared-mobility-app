import React, {Component} from 'react';
import Button from 'react-bootstrap/Button';
import './DataVisualization.css';
import { MapContainer, TileLayer, Rectangle, Tooltip, LayersControl, LayerGroup } from 'react-leaflet'

class DataVisualization extends Component {
  // create state variable
  constructor(props) {
    super(props);
    this.state = {
        center: [41.82972307181493, -71.41681396120897],
        demandFilename: "estimated_demand.csv",
        rectangles: [],
    };
  }

downloadData() {
    fetch('/return-demand-file').then(res => res).then(data => {
      var reader = data.body.getReader();
      return new ReadableStream({
        start(controller) {
          return pump();
          function pump() {
            return reader.read().then(({ done, value }) => {
              // When no more data needs to be consumed, close the stream
              if (done) {
                  console.log("Stream complete");
                  controller.close();
                  return;
              }
              // Enqueue the next data chunk into our target stream
              controller.enqueue(value);
              return pump();
            });
          }
        }
      })
    })
    .then(stream => new Response(stream))
    .then(response => response.blob())
    .then(blob => URL.createObjectURL(blob))
    .then(url => {
      // console.log(url);
      // console.log(this.state.demandFilename);
      var link = document.createElement("a");
      link.href = url;
      link.style = "visibility:hidden";
      link.download = this.state.demandFilename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    })
    .catch(err => console.error(err));
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
    const rectangle = [
      [41.835, -71.4167107905769],
      [41.824999999999996, -71.40329025766712],
    ]
    const blackOptions = { color: 'black' }

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

    const RectangleListTrips = ({ data, log }) => {
      return (
        <span>
          {data.map((item, i) => {
            return (
              <div>
                {log
                  ? <div>
                      <Rectangle key={i} bounds={item.bounds} color={item.log_trips_color}>
                        <Tooltip sticky>
                          Lat: {item.lat}, Long: {item.lng} <br />
                          Mean Trips/Day: {item.trips}
                        </Tooltip>
                      </Rectangle>
                    </div>
                  : <div>
                      <Rectangle key={i} bounds={item.bounds} color={item.trips_color}>
                        <Tooltip sticky>
                          Lat: {item.lat}, Long: {item.lng} <br />
                          Mean Trips/Day: {item.trips}
                        </Tooltip>
                      </Rectangle>
                    </div>
                }
              </div>
            );
          })}
        </span>
      );
    }

    const RectangleListAdjTrips = ({ data, log }) => {
      return (
        <span>
          {data.map((item, i) => {
            return (
              <div>
                {log
                  ? <div>
                      <Rectangle key={i} bounds={item.bounds} color={item.log_adj_trips_color}>
                        <Tooltip sticky>
                          Lat: {item.lat}, Long: {item.lng} <br />
                          Mean Trips/Day: {item.adj_trips}
                        </Tooltip>
                      </Rectangle>
                    </div>
                  : <div>
                      <Rectangle key={i} bounds={item.bounds} color={item.adj_trips_color}>
                        <Tooltip sticky>
                          Lat: {item.lat}, Long: {item.lng} <br />
                          Mean Trips/Day: {item.adj_trips}
                        </Tooltip>
                      </Rectangle>
                    </div>
                }
              </div>
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
          <MapContainer
            center={this.state.center}
            zoom={13}
            scrollWheelZoom={false}
            whenReady={this.getRectangleData.bind(this)}>
            <TileLayer
              attribution='&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            <LayersControl position="topright">
              <LayersControl.Overlay checked name="Logged color scale">
                {/*<Rectangle bounds={rectangle} pathOptions={blackOptions} />*/}
                <LayerGroup>
                  <RectangleListTrips data={this.state.rectangles} log={true} />
                </LayerGroup>
              </LayersControl.Overlay>
              <LayersControl.Overlay name="Unlogged color scale">
                <LayerGroup>
                  <RectangleListTrips data={this.state.rectangles} log={false} />
                </LayerGroup>
              </LayersControl.Overlay>
          </LayersControl>
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
            <LayersControl position="topright">
              <LayersControl.Overlay checked name="Logged color scale">
                {/*<Rectangle bounds={rectangle} pathOptions={blackOptions} />*/}
                <LayerGroup>
                  <RectangleListAdjTrips data={this.state.rectangles} log={true} />
                </LayerGroup>
              </LayersControl.Overlay>
              <LayersControl.Overlay name="Unlogged color scale">
                <LayerGroup>
                  <RectangleListAdjTrips data={this.state.rectangles} log={false} />
                </LayerGroup>
              </LayersControl.Overlay>
            </LayersControl>
          </MapContainer>

          <Button onClick={this.downloadData.bind(this)} id="downloadButton">Download Data</Button>
        </div>
      </>
    );
  }
}

export default DataVisualization;
