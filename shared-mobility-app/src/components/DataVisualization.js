import React, {Component} from 'react';
import Button from 'react-bootstrap/Button';
import Container from 'react-bootstrap/Container';
import Form from 'react-bootstrap/Form';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import DateRangePicker from 'react-bootstrap-daterangepicker';
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
        start: null,
        end: null,
        mapsToDisplay: [],
        mapTitles: {"avail_count":"Average number of scooters", "avail_mins":"Minutes at least one scooter available",
          "prob_scooter_avail":"Probability scooter available", "trips":"Number of trips", "adj_trips":"Adjusted number of trips"},
        mapTooltipTitles: {"avail_count":"# Scooters", "avail_mins":"Minutes Available",
          "prob_scooter_avail":"Prob Available", "trips":"# Trips", "adj_trips":"Adjusted # Trips"},
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

  getRectangleData(method) {
    if (this.state.start == null || this.state.end == null) {
      // in beginning just get rectangles and the initial start and end
      fetch('/return-rectangles', { method: 'GET' }).then(res => res).then(data => {
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
      .then(response => response.json())
      .then(json => {
        // console.log("from get");
        // console.log(json.data[0]);
        // console.log(json.start);
        // console.log(json.end);
        this.setState({rectangles: json.data, start: json.start, end: json.end});
      })
    } else {
      // post request with user inputted start and end
      const data = new FormData();
      data.append('start', this.state.start);
      data.append('end', this.state.end);
      // get the rectangles from within the time range
      fetch('/return-rectangles', { method: 'POST', body: data }).then(res => res).then(data => {
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
      .then(response => response.json())
      .then(json => {
        // console.log("from post");
        // console.log(json.data[0]);
        // console.log(json.start);
        // console.log(json.end);
        this.setState({rectangles: json.data, start: json.start, end: json.end});
      })
    }
  }

  componentDidMount() {
    this.getRectangleData();
  }

  setTime(start, end) {
    const startString = start.format('M/D/YYYY');
    const endString = end.format('M/D/YYYY');
    console.log(startString, endString);
    this.setState({start: startString, end: endString});
    // call rectangles
    this.getRectangleData();
  }

  handleMapCheckbox(event) {
    const varName = event.target.name;
    const isChecked = event.target.checked;
    console.log(varName, isChecked);
    if (isChecked && !(this.state.mapsToDisplay.includes(varName))) {
      // add variable to mapsToDisplay
      this.state.mapsToDisplay.push(varName);
      this.setState({mapsToDisplay: this.state.mapsToDisplay});
    } else if (!isChecked && (this.state.mapsToDisplay.includes(varName))) {
      // remove variable from mapsToDisplay
      this.setState({mapsToDisplay: this.state.mapsToDisplay.filter(item => item !== varName)});
    }
  }

  render() {
    const RectangleList = ({ data, log, varName }) => {
      return (
        <span>
          {data.map((item, i) => {
            return (
              <div key={i}>
                {log
                  ? <div>
                      <Rectangle key={i} bounds={item.bounds} color={item["log_"+varName+"_color"]}>
                        <Tooltip sticky>
                          Lat: {item.lat}, Long: {item.lng} <br />
                          {this.state.mapTooltipTitles[varName]}: {item["log_"+varName]}
                        </Tooltip>
                      </Rectangle>
                    </div>
                  : <div>
                      <Rectangle key={i} bounds={item.bounds} color={item[varName+"_color"]}>
                        <Tooltip sticky>
                          Lat: {item.lat}, Long: {item.lng} <br />
                          {this.state.mapTooltipTitles[varName]}: {item[varName]}
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

    const Maps = ({ data, varNames }) => {
      return (
        <div className="DataVisualization">
          {varNames.map(item => {
            return (
              <>
                <p className="DataVisualization-text">
                  {this.state.mapTitles[item]}
                </p>
                <MapContainer
                  center={this.state.center}
                  zoom={13}
                  scrollWheelZoom={false}>
                  <TileLayer
                    attribution='&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                  />
                  {(item === "prob_scooter_avail")
                    ? <LayersControl position="topright">
                        <LayersControl.Overlay checked name="Unlogged color scale">
                          <LayerGroup>
                            <RectangleList data={data} log={false} varName={item} />
                          </LayerGroup>
                        </LayersControl.Overlay>
                      </LayersControl>
                    : <LayersControl position="topright">
                        <LayersControl.Overlay checked name="Logged color scale">
                          <LayerGroup>
                            <RectangleList data={data} log={true} varName={item} />
                          </LayerGroup>
                        </LayersControl.Overlay>
                        <LayersControl.Overlay name="Unlogged color scale">
                          <LayerGroup>
                            <RectangleList data={data} log={false} varName={item} />
                          </LayerGroup>
                        </LayersControl.Overlay>
                      </LayersControl>
                  }
                </MapContainer>
              </>
            );
          })}
        </div>
      );
    }

    return (
      <>
        <Container fluid>
          <Row>
            <Col xs={2} className="UserDashboard">
                {(this.state.end != null) && (this.state.start != null) &&
                  <div>
                    <p>
                      Date Range to Include
                    </p>
                    <DateRangePicker
                      onCallback = {this.setTime.bind(this)}
                      initialSettings={{ startDate: this.state.start, endDate: this.state.end }}
                    >
                      <input type="text" className="form-control" id="dateInput" />
                    </DateRangePicker>
                  </div>
                }
              <br />
              <Form>
                <Form.Group>
                    <p>
                      Scooter Variable Maps to Display
                    </p>
                    <Form.Check
                      type="checkbox"
                      label="Average number of scooters"
                      className="mapCheckbox"
                      name="avail_count"
                      onChange={this.handleMapCheckbox.bind(this)}
                    />
                    <Form.Check
                      type="checkbox"
                      label="Minutes at least one scooter available"
                      className="mapCheckbox"
                      name="avail_mins"
                      onChange={this.handleMapCheckbox.bind(this)}
                    />
                    <Form.Check
                      type="checkbox"
                      label="Probability scooter available"
                      className="mapCheckbox"
                      name="prob_scooter_avail"
                      onChange={this.handleMapCheckbox.bind(this)}
                    />
                    <Form.Check
                      type="checkbox"
                      label="Number of trips"
                      className="mapCheckbox"
                      name="trips"
                      onChange={this.handleMapCheckbox.bind(this)}
                    />
                    <Form.Check
                      type="checkbox"
                      label="Adjusted number of trips"
                      className="mapCheckbox"
                      name="adj_trips"
                      onChange={this.handleMapCheckbox.bind(this)}
                    />
                </Form.Group>
              </Form>
              <br />
              <Button onClick={this.downloadData.bind(this)} id="downloadButton">Download Data</Button>
            </Col>
            <Col className="MapColumn">
                {(this.state.mapsToDisplay.length !== 0) &&
                    <Maps data={this.state.rectangles} varNames={this.state.mapsToDisplay} />
                }
            </Col>
          </Row>
        </Container>
      </>
    );
  }
}

export default DataVisualization;
