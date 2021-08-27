import logo from './upload_icon.png';
import React, {Component} from 'react';
import Form from 'react-bootstrap/Form';
import Button from 'react-bootstrap/Button';
import Col from 'react-bootstrap/Col';
import ChunkedUploady from "@rpldy/chunked-uploady";
import './ChunkingTest.css';

class ChunkingTest extends Component {

  handleUploadData(ev) {
    console.log('handling upload data');
  }

  render() {
    return (
      <>
        <header className="App-header">
          <img src={logo} className="App-logo" alt="logo" />
          <p>Upload Data</p>
        </header>
        <Form className="DropzoneTest">
            <Form.Group>
              <p className="formText">Input Remix events and locations data</p>
              <Form.Row>
                <Form.Label id="inputTitle" column>Events Data</Form.Label>
                <Col>
                  <Form.File className="fileInput" onChange={this.checkFiles}
                    ref={(ref) => { this.uploadEvents = ref; }}
                    type="file"
                  />
                </Col>
              </Form.Row>
            </Form.Group>
            <ChunkedUploady
               destination={{ url: 'http://127.0.0.1:5000/upload-test' }}
               chunkSize={2142880}>

               <Button variant="outline-light" type="submit" id="submitButton"> Upload </Button>
           </ChunkedUploady>
        </Form>
      </>
    );
  }

}

export default ChunkingTest;
