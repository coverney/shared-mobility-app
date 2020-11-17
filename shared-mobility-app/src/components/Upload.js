import React, {Component} from 'react'
import Button from 'react-bootstrap/Button';
import Form from 'react-bootstrap/Form'
import './Upload.css';

class Upload extends Component {
  // create state variable and handleUploadData function
  constructor(props) {
    super(props);
    this.state = {
      dataURL: "",
    };
    this.handleUploadData = this.handleUploadData.bind(this);
  }

  handleUploadData(ev) {
    // prevents the default action that belongs to the event from happening
    // we have this because we don't actually want to submit the form
    ev.preventDefault();
    // create a set of key/value pairs to send to the backend
    const data = new FormData();
    data.append('file', this.uploadInput.files[0]);
    data.append('filename', this.uploadInput.files[0].name);
    // send the uploaded data to flask
    fetch('/upload', { method: 'POST', body: data }).then(response => response.json()).then(data => {
      // this.setState({ dataURL: `/${data.file}` });
      console.log('hi');
    });
  }

  render() {
    return (
      <Form onSubmit={this.handleUploadData} className="Upload">
        <Form.Group>
          <Form.File id="userInput"
            ref={(ref) => { this.uploadInput = ref; }}
            type="file"
          />
        </Form.Group>
        <Button variant="outline-light" type="submit" id="submitButton"> Upload </Button>
      </Form>
    );
  }
}

export default Upload;
