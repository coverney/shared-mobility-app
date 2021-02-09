import logo from './upload_icon.png';
import React, {Component} from 'react';
import Button from 'react-bootstrap/Button';
import Form from 'react-bootstrap/Form';
import Modal from 'react-bootstrap/Modal';
import Col from 'react-bootstrap/Col';
import './Upload.css';
import { Redirect } from 'react-router-dom'
import { Default } from 'react-awesome-spinners'

class Upload extends Component {
  // create state variable and handleUploadData function
  constructor(props) {
    super(props);
    this.state = {
      error: false,
      errorMsg: '',
      redirect: false,
      loading: false,
    };
    this.handleUploadData = this.handleUploadData.bind(this);
  }

  handleUploadData(ev) {
    // prevents the default action that belongs to the event from happening
    // we have this because we don't actually want to submit the form
    ev.preventDefault();
    // make sure there are no missing files
    if (this.uploadEvents.files[0] == null || this.uploadLocations.files[0] == null) {
      console.log('Missing at least one data file')
      this.setState({error: true, errorMsg: "Missing at least one file, please make sure to upload both events and locations data!"});
      return;
    }
    // set loading variable to be true
    this.setState({loading: true});
    // create a set of key/value pairs to send to the backend
    const data = new FormData();
    data.append('eventsFile', this.uploadEvents.files[0]);
    data.append('eventsFilename', this.uploadEvents.files[0].name);
    data.append('locationsFile', this.uploadLocations.files[0]);
    data.append('locationsFilename', this.uploadLocations.files[0].name);
    // send the uploaded data to flask
    fetch('/upload', { method: 'POST', body: data }).then(response => response.json()).then(response => {
      console.log(response);
      this.setState({error: response.error, errorMsg: response.msg});
      if (!this.state.error && this.state.errorMsg !== '') {
        this.setState({redirect: true});
      }
      this.setState({loading: false});
    });
  }

  renderRedirect() {
    if (this.state.redirect) {
      return (
        <>
          <Redirect to="/data" />
        </>
      );
    }
  }

  render() {
    const loading = this.state.loading;
    return (
      <>
        <div>
          {loading
            ? <div>
                <header className="App-header">
                  <img src={logo} className="App-logo" alt="logo" />
                  <p>Processing Data</p>
                </header>
                <Default />
              </div>
            : <div>
                <header className="App-header">
                  <img src={logo} className="App-logo" alt="logo" />
                  <p>Upload Data</p>
                </header>
                <Form onSubmit={this.handleUploadData} className="Upload">
                  <Form.Group>
                    <Form.Row>
                      <Form.Label column>Events Data</Form.Label>
                      <Col>
                        <Form.File id="fileInput"
                          ref={(ref) => { this.uploadEvents = ref; }}
                          type="file"
                        />
                      </Col>
                    </Form.Row>
                    <br />
                    <Form.Row id="userInput2">
                      <Form.Label column>Locations Data</Form.Label>
                      <Col>
                        <Form.File id="fileInput"
                          ref={(ref) => { this.uploadLocations = ref; }}
                          type="file"
                        />
                      </Col>
                    </Form.Row>
                  </Form.Group>
                  <Button variant="outline-light" type="submit" id="submitButton"> Upload </Button>
              </Form>
            </div>
          }
        </div>

        <Modal
          show={this.state.error}
          onHide={() => this.setState({error:false, errorMsg: ''})}
          size="lg"
          aria-labelledby="contained-modal-title-vcenter"
          centered
        >
          <Modal.Header closeButton>
            <Modal.Title id="contained-modal-title-vcenter">
              File Upload Error
            </Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <p>
              { this.state.errorMsg }
            </p>
          </Modal.Body>
          <Modal.Footer>
            <Button onClick={() => this.setState({error: false, errorMsg: ''})}>Close</Button>
          </Modal.Footer>
        </Modal>

        <div>
          {this.renderRedirect()}
        </div>

      </>
    );
  }
}

export default Upload;
