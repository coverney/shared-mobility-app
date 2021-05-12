(this["webpackJsonpshared-mobility-app"]=this["webpackJsonpshared-mobility-app"]||[]).push([[0],{78:function(e,t,a){},79:function(e,t,a){},85:function(e,t,a){},91:function(e,t,a){},96:function(e,t,a){"use strict";a.r(t);var n=a(1),s=a(0),i=a.n(s),r=a(12),c=a.n(r),l=(a(78),a(79),a(47)),o=a(48),d=a(41),h=a(52),b=a(51),j=a.p+"static/media/upload_icon.1b97cf91.png",u=a(26),p=a(7),m=a(21),x=a(11),O=a(37),g=a(59),f=a.n(g),v=a(42),y=(a(85),a(9)),k=a(68),D=function(e){Object(h.a)(a,e);var t=Object(b.a)(a);function a(e){var n;return Object(l.a)(this,a),(n=t.call(this,e)).state={error:!1,errorMsg:"",redirect:!1,loading:!1,askForInput:!1,probValue:100,distanceValue:400,startTime:null,endTime:null},n.handleUploadData=n.handleUploadData.bind(Object(d.a)(n)),n.checkFiles=n.checkFiles.bind(Object(d.a)(n)),n}return Object(o.a)(a,[{key:"handleUploadData",value:function(e){var t=this;if(e.preventDefault(),null==this.uploadDemand.files[0]&&(null==this.uploadEvents.files[0]||null==this.uploadLocations.files[0]))return console.log("Missing at least one data file"),void this.setState({error:!0,errorMsg:"Missing at least one file, please make sure to upload both events and locations data!"});if(null!=this.uploadDemand.files[0]){console.log("Received demand file"),this.setState({loading:!0});var a=new FormData;a.append("demandFile",this.uploadDemand.files[0]),a.append("demandFilename",this.uploadDemand.files[0].name),fetch("/upload",{method:"POST",body:a}).then((function(e){return e.json()})).then((function(e){console.log(e),t.setState({error:e.error,errorMsg:e.msg}),t.state.error||""===t.state.errorMsg||t.setState({redirect:!0}),t.setState({loading:!1})}))}else{this.setState({loading:!0});var n=new FormData;n.append("eventsFile",this.uploadEvents.files[0]),n.append("eventsFilename",this.uploadEvents.files[0].name),n.append("locationsFile",this.uploadLocations.files[0]),n.append("locationsFilename",this.uploadLocations.files[0].name),n.append("probValue",this.state.probValue),n.append("distanceValue",this.state.distanceValue),null!=this.state.startTime?n.append("startTime",this.state.startTime):n.append("startTime",""),null!=this.state.endTime?n.append("endTime",this.state.endTime):n.append("endTime",""),fetch("/upload",{method:"POST",body:n}).then((function(e){return e.json()})).then((function(e){console.log(e),t.setState({error:e.error,errorMsg:e.msg}),t.state.error||""===t.state.errorMsg||t.setState({redirect:!0}),t.setState({loading:!1})}))}}},{key:"renderRedirect",value:function(){if(this.state.redirect)return Object(n.jsx)(n.Fragment,{children:Object(n.jsx)(y.a,{to:"/data"})})}},{key:"checkFiles",value:function(){null!=this.uploadEvents.files[0]&&null!=this.uploadLocations.files[0]&&this.setState({askForInput:!0})}},{key:"render",value:function(){var e=this,t=this.state.loading;return Object(n.jsxs)(n.Fragment,{children:[Object(n.jsx)("div",{children:t?Object(n.jsxs)("div",{children:[Object(n.jsxs)("header",{className:"App-header",children:[Object(n.jsx)("img",{src:j,className:"App-logo",alt:"logo"}),Object(n.jsx)("p",{children:"Processing Data"})]}),Object(n.jsx)(k.a,{})]}):Object(n.jsxs)("div",{children:[Object(n.jsxs)("header",{className:"App-header",children:[Object(n.jsx)("img",{src:j,className:"App-logo",alt:"logo"}),Object(n.jsx)("p",{children:"Upload Data"})]}),Object(n.jsxs)(p.a,{onSubmit:this.handleUploadData,className:"Upload",children:[Object(n.jsxs)(p.a.Group,{children:[Object(n.jsx)("p",{className:"formText",children:"Input Remix events and locations data"}),Object(n.jsxs)(p.a.Row,{children:[Object(n.jsx)(p.a.Label,{id:"inputTitle",column:!0,children:"Events Data"}),Object(n.jsx)(x.a,{children:Object(n.jsx)(p.a.File,{className:"fileInput",onChange:this.checkFiles,ref:function(t){e.uploadEvents=t},type:"file"})})]}),Object(n.jsx)("br",{}),Object(n.jsxs)(p.a.Row,{id:"userInput2",children:[Object(n.jsx)(p.a.Label,{id:"inputTitle",column:!0,children:"Locations Data"}),Object(n.jsx)(x.a,{children:Object(n.jsx)(p.a.File,{className:"fileInput",onChange:this.checkFiles,ref:function(t){e.uploadLocations=t},type:"file"})})]}),Object(n.jsx)("br",{}),Object(n.jsx)("p",{className:"formText",children:"Or input estimated demand data from last time"}),Object(n.jsxs)(p.a.Row,{id:"userInput3",children:[Object(n.jsx)(p.a.Label,{id:"inputTitle",column:!0,children:"Demand Data"}),Object(n.jsx)(x.a,{children:Object(n.jsx)(p.a.File,{className:"fileInput",onChange:this.checkFiles,ref:function(t){e.uploadDemand=t},type:"file"})})]})]}),Object(n.jsx)(u.a,{variant:"outline-light",type:"submit",id:"submitButton",children:" Upload "})]})]})}),Object(n.jsxs)(m.a,{show:this.state.error,onHide:function(){return e.setState({error:!1,errorMsg:""})},size:"lg","aria-labelledby":"contained-modal-title-vcenter",centered:!0,children:[Object(n.jsx)(m.a.Header,{closeButton:!0,children:Object(n.jsx)(m.a.Title,{id:"contained-modal-title-vcenter",children:"File Upload Error"})}),Object(n.jsx)(m.a.Body,{children:Object(n.jsx)("p",{children:this.state.errorMsg})}),Object(n.jsx)(m.a.Footer,{children:Object(n.jsx)(u.a,{onClick:function(){return e.setState({error:!1,errorMsg:""})},children:"Close"})})]}),Object(n.jsxs)(m.a,{show:this.state.askForInput,onHide:function(){return e.setState({askForInput:!1})},size:"lg","aria-labelledby":"contained-modal-title-vcenter",centered:!0,enforceFocus:!1,scrollable:!0,children:[Object(n.jsx)(m.a.Header,{closeButton:!0,children:Object(n.jsx)(m.a.Title,{id:"contained-modal-title-vcenter",children:"Input Model Parameters"})}),Object(n.jsxs)(m.a.Body,{children:[Object(n.jsxs)("p",{children:[Object(n.jsx)("b",{children:"Disclaimer"}),": unless specified, the first and last times in the events data are taken as the start and end times for data processing"]}),Object(n.jsxs)(O.a,{id:"dateQuestions",children:[Object(n.jsx)(x.a,{xs:"6",children:Object(n.jsxs)("div",{children:[Object(n.jsx)("p",{children:"Start date (optional)"}),Object(n.jsx)(v.a,{onApply:function(t,a){e.setState({startTime:a.startDate.format("M/D/YYYY")}),console.log(a.startDate.format("M/D/YYYY"))},initialSettings:{singleDatePicker:!0,showDropdowns:!0,minYear:2005,maxYear:parseInt((new Date).getFullYear(),10)},children:Object(n.jsx)("button",{type:"button",className:"btn btn-outline-primary",children:"click to set date"})})]})}),Object(n.jsx)(x.a,{xs:"6",children:Object(n.jsxs)("div",{children:[Object(n.jsx)("p",{children:"End date (optional)"}),Object(n.jsx)(v.a,{onApply:function(t,a){e.setState({endTime:a.startDate.format("M/D/YYYY")}),console.log(a.startDate.format("M/D/YYYY"))},initialSettings:{singleDatePicker:!0,showDropdowns:!0,minYear:2005,maxYear:parseInt((new Date).getFullYear(),10)},children:Object(n.jsx)("button",{type:"button",className:"btn btn-outline-primary",children:"click to set date"})})]})})]}),Object(n.jsx)("br",{}),Object(n.jsxs)(p.a,{children:[Object(n.jsx)(p.a.Label,{children:"Dimensions for one grid (in meters)"}),Object(n.jsxs)(p.a.Group,{as:O.a,children:[Object(n.jsx)(x.a,{xs:"9",children:Object(n.jsx)(f.a,{value:this.state.distanceValue,onChange:function(t){return e.setState({distanceValue:t.target.value,probValue:100})},min:100,max:1e3})}),Object(n.jsx)(x.a,{xs:"3",children:Object(n.jsx)(p.a.Control,{value:this.state.distanceValue,onChange:function(t){return e.setState({distanceValue:t.target.value,probValue:100})}})})]})]}),Object(n.jsxs)(p.a,{children:[Object(n.jsx)(p.a.Label,{children:"Probability (%) a user wouldn't consider a scooter that is at least one grid away "}),Object(n.jsxs)(p.a.Group,{as:O.a,children:[Object(n.jsx)(x.a,{xs:"9",children:Object(n.jsx)(f.a,{value:this.state.probValue,onChange:function(t){return e.setState({probValue:t.target.value})},min:Math.ceil(this.state.distanceValue/10+5),max:100,tooltipLabel:function(e){return"".concat(e,"%")}})}),Object(n.jsx)(x.a,{xs:"3",children:Object(n.jsx)(p.a.Control,{value:this.state.probValue,onChange:function(t){return e.setState({probValue:t.target.value})}})})]})]})]}),Object(n.jsx)(m.a.Footer,{children:Object(n.jsx)(u.a,{onClick:function(){return e.setState({askForInput:!1})},children:"Submit"})})]}),Object(n.jsx)("div",{children:this.renderRedirect()})]})}}]),a}(s.Component),T=a(72),C=a(63),F=a(31),S=a(64),_=(a(91),a(102)),w=a(103),M=a(104),N=a(107),Y=a(105),L=a(106),R=function(e){Object(h.a)(a,e);var t=Object(b.a)(a);function a(e){var n;return Object(l.a)(this,a),(n=t.call(this,e)).state={center:[41.82972307181493,-71.41681396120897],demandFilename:"processedGridCellData.csv",rectangles:[],start:null,end:null,mapsToDisplay:[],mapTitles:{avail_count:"Average number of scooters",avail_mins:"Minutes at least one scooter available",prob_scooter_avail:"Probability scooter available",trips:"Number of trips",adj_trips:"Adjusted number of trips",unmet_demand:"Unmet demand"},mapTooltipTitles:{avail_count:"# Scooters",avail_mins:"Minutes Available",prob_scooter_avail:"Prob Available",trips:"# Trips",adj_trips:"Adjusted # Trips",unmet_demand:"Unmet Demand",estimated_demand:"Estimated Demand"},mapInfoText:{avail_count:"Average number of scooters in a day",avail_mins:"Average minutes at least one scooter available in a day",prob_scooter_avail:"Average probability a random user finds a scooter available that they are willing to travel to",trips:"Average number of trips in a day (obtained from events data)",adj_trips:"Average estimated number of trips originating from a grid cell within a day",unmet_demand:"Estimated unmet demand within a day for grid cells with probabilities that significantly differ from 0. Value obtained by first calculating estimated demand (adjusted trips divided by probability scooter available) and then subtracting adjusted trips from it"}},n}return Object(o.a)(a,[{key:"downloadData",value:function(){var e=this;fetch("/return-demand-file").then((function(e){return e})).then((function(e){var t=e.body.getReader();return new ReadableStream({start:function(e){return function a(){return t.read().then((function(t){var n=t.done,s=t.value;return n?(console.log("Stream complete"),void e.close()):(e.enqueue(s),a())}))}()}})})).then((function(e){return new Response(e)})).then((function(e){return e.blob()})).then((function(e){return URL.createObjectURL(e)})).then((function(t){var a=new Date,n=(1e4*a.getFullYear()+100*(a.getMonth()+1)+a.getDate()).toString(),s=document.createElement("a");s.href=t,s.style="visibility:hidden",s.download=n+"_"+e.state.demandFilename,document.body.appendChild(s),s.click(),document.body.removeChild(s)})).catch((function(e){return console.error(e)}))}},{key:"getRectangleData",value:function(e){var t=this;if(null==this.state.start||null==this.state.end)fetch("/return-rectangles",{method:"GET"}).then((function(e){return e})).then((function(e){var t=e.body.getReader();return new ReadableStream({start:function(e){return function a(){return t.read().then((function(t){var n=t.done,s=t.value;return n?(console.log("Stream complete"),void e.close()):(e.enqueue(s),a())}))}()}})})).then((function(e){return new Response(e)})).then((function(e){return e.json()})).then((function(e){t.setState({rectangles:e.data,start:e.start,end:e.end})}));else{var a=new FormData;a.append("start",this.state.start),a.append("end",this.state.end),fetch("/return-rectangles",{method:"POST",body:a}).then((function(e){return e})).then((function(e){var t=e.body.getReader();return new ReadableStream({start:function(e){return function a(){return t.read().then((function(t){var n=t.done,s=t.value;return n?(console.log("Stream complete"),void e.close()):(e.enqueue(s),a())}))}()}})})).then((function(e){return new Response(e)})).then((function(e){return e.json()})).then((function(e){t.setState({rectangles:e.data,start:e.start,end:e.end})}))}}},{key:"componentDidMount",value:function(){this.getRectangleData()}},{key:"setTime",value:function(e,t){var a=e.format("M/D/YYYY"),n=t.format("M/D/YYYY");console.log(a,n),this.setState({start:a,end:n}),this.getRectangleData()}},{key:"handleMapCheckbox",value:function(e){var t=e.target.name,a=e.target.checked;console.log(t,a),a&&!this.state.mapsToDisplay.includes(t)?(this.state.mapsToDisplay.push(t),this.setState({mapsToDisplay:this.state.mapsToDisplay})):!a&&this.state.mapsToDisplay.includes(t)&&this.setState({mapsToDisplay:this.state.mapsToDisplay.filter((function(e){return e!==t}))})}},{key:"render",value:function(){var e=this,t=function(t){var a=t.data,s=t.log,i=t.varName;return Object(n.jsx)("span",{children:a.map((function(t,a){return Object(n.jsx)("div",{children:s?Object(n.jsx)("div",{children:Object(n.jsx)(_.a,{bounds:t.bounds,color:t["log_"+i+"_color"],children:"unmet_demand"===i?Object(n.jsx)(n.Fragment,{children:Object(n.jsxs)(w.a,{sticky:!0,children:["Lat: ",t.lat,", Long: ",t.lng," ",Object(n.jsx)("br",{}),null==t.estimated_demand?Object(n.jsxs)(n.Fragment,{children:["Prob scooter available not ",Object(n.jsx)("br",{})," significantly different than zero"]}):Object(n.jsxs)(n.Fragment,{children:[e.state.mapTooltipTitles.estimated_demand,": ",t.estimated_demand," ",Object(n.jsx)("br",{}),e.state.mapTooltipTitles[i],": ",t[i]]})]})}):Object(n.jsx)(n.Fragment,{children:Object(n.jsxs)(w.a,{sticky:!0,children:["Lat: ",t.lat,", Long: ",t.lng," ",Object(n.jsx)("br",{}),e.state.mapTooltipTitles[i],": ",t[i]]})})},a)}):Object(n.jsx)("div",{children:Object(n.jsx)(_.a,{bounds:t.bounds,color:t[i+"_color"],children:"unmet_demand"===i?Object(n.jsx)(n.Fragment,{children:Object(n.jsxs)(w.a,{sticky:!0,children:["Lat: ",t.lat,", Long: ",t.lng," ",Object(n.jsx)("br",{}),null==t.estimated_demand?Object(n.jsxs)(n.Fragment,{children:["Prob scooter available not ",Object(n.jsx)("br",{})," significantly different than zero"]}):Object(n.jsxs)(n.Fragment,{children:[e.state.mapTooltipTitles.estimated_demand,": ",t.estimated_demand," ",Object(n.jsx)("br",{}),e.state.mapTooltipTitles[i],": ",t[i]]})]})}):Object(n.jsx)(n.Fragment,{children:Object(n.jsxs)(w.a,{sticky:!0,children:["Lat: ",t.lat,", Long: ",t.lng," ",Object(n.jsx)("br",{}),e.state.mapTooltipTitles[i],": ",t[i]]})})},a)})},a)}))})},a=function(a){var s=a.data,i=a.varNames;return Object(n.jsx)("div",{className:"DataVisualization",children:i.map((function(a){return Object(n.jsxs)(n.Fragment,{children:[Object(n.jsxs)("p",{className:"DataVisualization-text",children:[e.state.mapTitles[a],Object(n.jsx)(C.a,{trigger:["hover","focus"],placement:"bottom",overlay:Object(n.jsxs)(F.a,{children:[Object(n.jsx)(F.a.Title,{as:"h1",children:"Variable Info"}),Object(n.jsx)(F.a.Content,{children:e.state.mapInfoText[a]})]}),children:Object(n.jsx)(u.a,{variant:"link",children:Object(n.jsx)(S.a,{className:"react-icons",size:"1em",color:"#5bc0de"})})})]}),Object(n.jsxs)(M.a,{center:e.state.center,zoom:13,scrollWheelZoom:!1,children:[Object(n.jsx)(N.a,{attribution:'\xa9 <a href="http://osm.org/copyright">OpenStreetMap</a> contributors',url:"https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"}),"prob_scooter_avail"===a?Object(n.jsx)(Y.a,{position:"topright",children:Object(n.jsx)(Y.a.Overlay,{checked:!0,name:"Unlogged color scale",children:Object(n.jsx)(L.a,{children:Object(n.jsx)(t,{data:s,log:!1,varName:a})})})}):Object(n.jsxs)(Y.a,{position:"topright",children:[Object(n.jsx)(Y.a.Overlay,{checked:!0,name:"Logged color scale",children:Object(n.jsx)(L.a,{children:Object(n.jsx)(t,{data:s,log:!0,varName:a})})}),Object(n.jsx)(Y.a.Overlay,{name:"Unlogged color scale",children:Object(n.jsx)(L.a,{children:Object(n.jsx)(t,{data:s,log:!1,varName:a})})})]})]})]})}))})},s=Object(n.jsxs)(F.a,{children:[Object(n.jsx)(F.a.Title,{as:"h1",children:"Select variables"}),Object(n.jsx)(F.a.Content,{children:"Maps will be generated for the variables you selected. The values can be obtained by hovering over the grid cells on the map. All variables except for probability scooter available has two layers: one colored by log values and one colored by the original values"})]});return Object(n.jsx)(n.Fragment,{children:Object(n.jsx)(T.a,{fluid:!0,children:Object(n.jsxs)(O.a,{children:[Object(n.jsxs)(x.a,{xs:3,className:"UserDashboard",children:[null!=this.state.end&&null!=this.state.start&&Object(n.jsxs)("div",{children:[Object(n.jsx)("p",{children:"Date Range to Include"}),Object(n.jsx)(v.a,{onCallback:this.setTime.bind(this),initialSettings:{startDate:this.state.start,endDate:this.state.end},children:Object(n.jsx)("input",{type:"text",className:"form-control",id:"dateInput"})})]}),Object(n.jsx)("br",{}),Object(n.jsx)(p.a,{children:Object(n.jsxs)(p.a.Group,{children:[Object(n.jsxs)("p",{id:"mapCheckboxText",children:["Scooter Variable Maps to Display",Object(n.jsx)(C.a,{trigger:["hover","focus"],placement:"right",overlay:s,children:Object(n.jsx)(u.a,{variant:"link",children:Object(n.jsx)(S.a,{className:"react-icons",size:"1em",color:"#5bc0de"})})})]}),Object(n.jsx)(p.a.Check,{type:"checkbox",label:"Average number of scooters",className:"mapCheckbox",name:"avail_count",onChange:this.handleMapCheckbox.bind(this)}),Object(n.jsx)(p.a.Check,{type:"checkbox",label:"Minutes at least one scooter available",className:"mapCheckbox",name:"avail_mins",onChange:this.handleMapCheckbox.bind(this)}),Object(n.jsx)(p.a.Check,{type:"checkbox",label:"Number of trips",className:"mapCheckbox",name:"trips",onChange:this.handleMapCheckbox.bind(this)}),Object(n.jsx)(p.a.Check,{type:"checkbox",label:"Probability scooter available",className:"mapCheckbox",name:"prob_scooter_avail",onChange:this.handleMapCheckbox.bind(this)}),Object(n.jsx)(p.a.Check,{type:"checkbox",label:"Adjusted number of trips",className:"mapCheckbox",name:"adj_trips",onChange:this.handleMapCheckbox.bind(this)}),Object(n.jsx)(p.a.Check,{type:"checkbox",label:"Unmet demand",className:"mapCheckbox",name:"unmet_demand",onChange:this.handleMapCheckbox.bind(this)})]})}),Object(n.jsx)("br",{}),Object(n.jsx)(u.a,{onClick:this.downloadData.bind(this),id:"downloadButton",children:"Download Data"})]}),Object(n.jsx)(x.a,{className:"MapColumn",children:0!==this.state.mapsToDisplay.length&&Object(n.jsx)(a,{data:this.state.rectangles,varNames:this.state.mapsToDisplay})})]})})})}}]),a}(s.Component),V=a(58);var I=function(){return Object(n.jsx)("div",{children:Object(n.jsx)(V.a,{children:Object(n.jsxs)(y.d,{children:[Object(n.jsx)(y.b,{path:"/data",children:Object(n.jsx)(R,{})}),Object(n.jsx)(y.b,{path:"/",children:Object(n.jsx)("div",{className:"App",children:Object(n.jsx)(D,{})})})]})})})},A=function(e){e&&e instanceof Function&&a.e(3).then(a.bind(null,108)).then((function(t){var a=t.getCLS,n=t.getFID,s=t.getFCP,i=t.getLCP,r=t.getTTFB;a(e),n(e),s(e),i(e),r(e)}))};a(93),a(94),a(95);c.a.render(Object(n.jsx)(i.a.StrictMode,{children:Object(n.jsx)(I,{})}),document.getElementById("root")),A()}},[[96,1,2]]]);
//# sourceMappingURL=main.b24fe95e.chunk.js.map