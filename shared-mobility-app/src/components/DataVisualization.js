import React, {Component} from 'react';
import Button from 'react-bootstrap/Button';
import Container from 'react-bootstrap/Container';
import Form from 'react-bootstrap/Form';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import OverlayTrigger from 'react-bootstrap/OverlayTrigger';
import Popover from 'react-bootstrap/Popover';
import DateRangePicker from 'react-bootstrap-daterangepicker';
import { AiOutlineInfoCircle } from 'react-icons/ai';
import './DataVisualization.css';
import { MapContainer, TileLayer, Rectangle, Tooltip, LayersControl, LayerGroup } from 'react-leaflet'

class DataVisualization extends Component {
  // create state variable
  constructor(props) {
    super(props);
    this.state = {
        center: [41.82972307181493, -71.41681396120897],
        demandFilename: "processedGridCellData.csv",
        rectangles: [],
        start: null,
        end: null,
        mapsToDisplay: [],
        mapTitles: {"avail_count":"Average number of scooters", "avail_mins":"Minutes at least one scooter available",
          "prob_scooter_avail":"Probability scooter available", "trips":"Number of trips", "adj_trips":"Adjusted number of trips",
          "unmet_demand":"Unmet demand"},
        mapTooltipTitles: {"avail_count":"# Scooters", "avail_mins":"Minutes Available",
          "prob_scooter_avail":"Prob Available", "trips":"# Trips", "adj_trips":"Adjusted # Trips",
          "unmet_demand":"Unmet Demand", "estimated_demand":"Estimated Demand"},
        mapInfoText: {"avail_count":"Average number of scooters in a day",
          "avail_mins":"Average minutes at least one scooter available in a day",
          "prob_scooter_avail":"Average probability a random user finds a scooter available that they are willing to travel to",
          "trips":"Average number of trips in a day (obtained from events data)",
          "adj_trips":"Average estimated number of trips originating from a grid cell within a day",
          "unmet_demand":"Estimated unmet demand within a day for grid cells with probabilities that significantly differ from 0. Value obtained by first calculating estimated demand (adjusted trips divided by probability scooter available) and then subtracting adjusted trips from it"},
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
      // get the timestamp to add to the filename
      var now = new Date();
      var year = now.getFullYear() * 10000;
      var month = (now.getMonth() + 1) * 100;
      var date = now.getDate();
      var fullDate = (year + month + date).toString();
      var link = document.createElement("a");
      link.href = url;
      link.style = "visibility:hidden";
      link.download = fullDate + "_" + this.state.demandFilename;
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
                        {(varName==="unmet_demand")
                          ? <>
                              <Tooltip sticky>
                                Lat: {item.lat}, Long: {item.lng} <br />
                                {(item["estimated_demand"]==null)
                                  ? <>
                                      Prob scooter available not <br /> significantly different than zero
                                    </>
                                  : <>
                                      {this.state.mapTooltipTitles["estimated_demand"]}: {item["estimated_demand"]} <br />
                                      {this.state.mapTooltipTitles[varName]}: {item[varName]}
                                    </>
                                }
                              </Tooltip>
                            </>
                          : <>
                              <Tooltip sticky>
                                Lat: {item.lat}, Long: {item.lng} <br />
                                {this.state.mapTooltipTitles[varName]}: {item[varName]}
                              </Tooltip>
                            </>
                        }
                      </Rectangle>
                    </div>
                  : <div>
                      <Rectangle key={i} bounds={item.bounds} color={item[varName+"_color"]}>
                        {(varName==="unmet_demand")
                          ? <>
                              <Tooltip sticky>
                                Lat: {item.lat}, Long: {item.lng} <br />
                                {(item["estimated_demand"]==null)
                                  ? <>
                                      Prob scooter available not <br /> significantly different than zero
                                    </>
                                  : <>
                                      {this.state.mapTooltipTitles["estimated_demand"]}: {item["estimated_demand"]} <br />
                                      {this.state.mapTooltipTitles[varName]}: {item[varName]}
                                    </>
                                }
                              </Tooltip>
                            </>
                          : <>
                              <Tooltip sticky>
                                Lat: {item.lat}, Long: {item.lng} <br />
                                {this.state.mapTooltipTitles[varName]}: {item[varName]}
                              </Tooltip>
                            </>
                        }
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
                  <OverlayTrigger trigger={['hover', 'focus']} placement="bottom"
                    overlay={<Popover>
                                <Popover.Title as="h1">Variable Info</Popover.Title>
                                <Popover.Content>
                                  {this.state.mapInfoText[item]}
                                </Popover.Content>
                              </Popover>}>
                    <Button variant="link"><AiOutlineInfoCircle className="react-icons" size="1em" color="#5bc0de"/></Button>
                  </OverlayTrigger>
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

    const checkBoxPopover = (
      <Popover>
        <Popover.Title as="h1">Select variables</Popover.Title>
        <Popover.Content>
          Maps will be generated for the variables you selected. The values
          can be obtained by hovering over the grid cells on the map. All
          variables except for probability scooter available has two layers:
          one colored by log values and one colored by the original values
        </Popover.Content>
      </Popover>
    );

    return (
      <>
        <Container fluid>
          <Row>
            <Col xs={3} className="UserDashboard">
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
                    <p id="mapCheckboxText">
                      Scooter Variable Maps to Display
                      <OverlayTrigger trigger={['hover', 'focus']} placement="right"
                        overlay={checkBoxPopover}>
                        <Button variant="link"><AiOutlineInfoCircle className="react-icons" size="1em" color="#5bc0de"/></Button>
                      </OverlayTrigger>
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
                      label="Number of trips"
                      className="mapCheckbox"
                      name="trips"
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
                      label="Adjusted number of trips"
                      className="mapCheckbox"
                      name="adj_trips"
                      onChange={this.handleMapCheckbox.bind(this)}
                    />
                    <Form.Check
                      type="checkbox"
                      label="Unmet demand"
                      className="mapCheckbox"
                      name="unmet_demand"
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
