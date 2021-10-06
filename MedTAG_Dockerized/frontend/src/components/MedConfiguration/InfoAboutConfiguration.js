import '../../App.css';
import {AppContext} from '../../App';
import React, {useState, useEffect, useContext, createContext} from "react";
import '../SideComponents/compStyle.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'react-bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'react-bootstrap';
import {Container,Row,Col} from "react-bootstrap";
import Button from "react-bootstrap/Button";

import '../General/first_row.css';

import SelectMenu from "../SelectMenu/SelectMenu";

import SideBar from "../General/SideBar";
import axios from "axios";
import Spinner from "react-bootstrap/Spinner";
import {faBars, faDownload, faUser} from "@fortawesome/free-solid-svg-icons";
import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";
import Modal from "react-bootstrap/Modal";
import {Link,Redirect} from "react-router-dom";
import ExpandMoreIcon from "@material-ui/icons/ExpandMore";
import IconButton from "@material-ui/core/IconButton";
import Collapse from "@material-ui/core/Collapse";

function InfoAboutConfiguration() {
    const { admin,showbar,username,usecaseList,reports,languageList,instituteList } = useContext(AppContext);

    var FileDownload = require('js-file-download');


    const [Redir, SetRedir] = useState(false);
    const [UpdateConfiguration, SetUpdateConfiguration] = useState(false);
    const [ShowBar,SetShowBar] = showbar;
    const [Admin,SetAdmin] = admin;
    const [Username,SetUsername] = username;
    const [GroundTruthList,SetGroundTruthList] = useState([])
    const [ShowModalSure,SetShowModalSure] = useState(false)
    const [ShowModalMissing,SetShowModalMissing] = useState(false)
    const [ShowGenSection,SetShowGenSection] = useState(false)
    const [ShowCSVSection,SetShowCSVSection] = useState(false)
    const [ShowExSection,SetShowExSection] = useState(false)


    function handleBar(e){
        SetShowBar(prevState => !prevState)
    }
    useEffect(()=>{
        window.scrollTo(0, 0)

    },[])
    function handleCloseMissing(){
        SetShowModalMissing(false)
        SetRedir(true)
    }
    function onSaveExample(e,token){
        e.preventDefault()
        axios.get('http://0.0.0.0:8000/download_examples', {params:{token:token}})
            .then(function (response) {
                if(token === 'reports'){
                    FileDownload((response.data), 'reports_example.csv');
                }
                else if(token === 'concepts'){
                    FileDownload((response.data), 'concepts_example.csv');
                }
                else if(token === 'labels'){
                    FileDownload((response.data), 'labels_example.csv');
                }
                else if(token === 'pubmed'){
                    FileDownload((response.data), 'pubmed_example.csv');
                }


            })
            .catch(function (error) {
                console.log('error message', error);
            });

    }
    function onSaveTemplate(e,token){
        e.preventDefault()
        axios.get('http://0.0.0.0:8000/download_templates', {params:{token:token}})
            .then(function (response) {
                if(token === 'reports'){
                    FileDownload((response.data), 'reports_template.csv');
                }
                else if(token === 'concepts'){
                    FileDownload((response.data), 'concepts_template.csv');
                }
                else if(token === 'labels'){
                    FileDownload((response.data), 'labels_template.csv');
                }
                else if(token === 'pubmed'){
                    FileDownload((response.data), 'pubmed_template.csv');
                }

            })
            .catch(function (error) {
                console.log('error message', error);
            });

    }
    function handleClose(){
        SetShowModalSure(false)
    }
    useEffect(()=>{
        console.log('ALL!!!')
        axios.get('http://0.0.0.0:8000/get_gt_list',{params:{token:'all'}}).then(response => SetGroundTruthList(response.data['ground_truths'])).catch(error =>console.log(error))
    },[])

    function onSaveAll(token){
        // SetShowModalSure(false)
        // console.log('gt_list',GroundTruthList)
        // console.log('gt_list',token)
        if(token === 'save' && GroundTruthList>0){

            axios.get('http://0.0.0.0:8000/download_all_ground_truths')
                .then(function (response) {
                    FileDownload(JSON.stringify(response.data['ground_truth']), 'all_json_ground_truth.json');
                    SetShowModalSure(false)
                    SetShowModalMissing(false)
                    SetRedir(true)

                })
                .catch(function (error) {

                    console.log('error message', error);
                });

        }
        else if(token === 'save' && GroundTruthList === 0){
            SetShowModalMissing(true)
        }
        else if(token === 'skip'){
            SetShowModalMissing(false)
            SetShowModalSure(false)
            SetRedir(true)
        }


    }
    useEffect(()=>{
        // console.log('showmodalmissi',ShowModalMissing)
    },[ShowModalMissing])

    // useEffect(()=>{
    //     if(ShowModalSure === true && GroundTruthList === 0){
    //         onSaveAll('skip')
    //     }
    // },[ShowModalSure])

    return (
        <div className="App">


            <div >
                {/*<div style={{'float':'left','padding':'10px','padding-left':'250px'}}><button className='menuButton' onClick={(e)=>handleBar(e)}><FontAwesomeIcon icon={faBars} size='2x' /></button></div>*/}
                <Container fluid>
                    {ShowBar && <SideBar />}

                    <Row>
                        <Col md={1}>
                            <span> <button className='menuButton' onClick={(e)=>handleBar(e)}><FontAwesomeIcon icon={faBars} size='2x' /></button></span>
                        </Col>
                        <Col md={11}></Col>
                    </Row>
                <div>
                    <h2 style={{'margin-top':'30px','margin-bottom':'30px','text-align':'center'}}>New MedTAG configuration</h2>
                    <div style={{'text-align':'center'}}><div>If you are already running your configuration and you want to add new data, for example a new batch of reports or new concepts, click on <i>Update configuration</i>.
                        {Username === 'Test' && Admin === '' && <div><b>You are in the test mode, this means that you are using a configuration we provided in order to test the application before uploading your data. Once you finished your tests, please, start a new configuration clicking on <i>Configure without saving</i> or on <i>Save the json ground truths and configure.</i></b></div>}
                    </div>
                        <div>
                        <Button variant="success" onClick={(e)=>SetUpdateConfiguration(true)}>
                            Update configuration
                        </Button></div>
                        <hr/>
                    </div>
                    Dear user,<br/> pay attention to the following sections before changing the MedTAG configuration.

                        {/*This type of file is usually used to represent data tables. The first row contains the columns' names separated by a delimiter (usually the comma, but it depends, sometimes it can also be the semicolon). Each one of the other rows instead, contain the data: each row contain as many values as the columns are and these values are separated by the comma.</div>*/}
                    <div style={{'margin-top':'30px'}}>
                        <div><h4 style={{display:'inline-block'}}>General Information about the configuration</h4><IconButton onClick={()=>SetShowGenSection(prev=>!prev)}><ExpandMoreIcon style={{marginLeft:'2px'}} /></IconButton></div>
                        <Collapse style={{marginTop:'0px'}} in={ShowGenSection}>


                        <div>
                        <ul>
                        <li>
                            The new configuration you are going to set will <span style={{'font-weight':'bold'}}>overwrite</span> the current one. This means that all the annotations you performed will be lost (if any) together with the automatic annotations. This action is <span style={{'font-weight':'bold'}}>irreversible</span>. To keep all your data safe, we strongly recommend you to download the ground truths you created, especially if you are not in the test mode - i.e., you are not using the sample of data we provided the very first time you opened the application.
                         </li>
                            <li>
                                If you are in the Test mode and there is no web app administrator yet, you are asked to provide a <span style={{'font-weight':'bold'}}>username</span> and a <span style={{'font-weight':'bold'}}>password</span> that characterize your account. You will be the <span style={{'font-weight':'bold'}}>Admin</span>, which means that you are the only one who can change or update the configuration of the web app. Remember that if you are in the test mode, the test account will be available if some tests on the application need to be performed.
                            </li>
                        <li>
                            You will be asked to provide three CSV files containing the data needed to run MedTAG. After this configuration, you will perform: <i>labels annotation, linking, mentions annotation</i> and <i>concepts identification</i> with the data you provided. We ask you to provide:
                            <ul>

                                <li>
                                    One or more files containing the texts (reports) you want to annotate. A file containing the textual reports is typically characterized by a set of standard columns: a <i>language</i>, the one used to write the report, an <i>institute</i>, which is the hospital, or, more generally, where the report has been produced, the <i>id_report</i>, the identifier of the report and the <i>usecase</i> characterizing the report. A <i>usecase</i> is typically used to categorize the report examined; for example, the set of reports we provided in the test mode describe colon cancer cases. The related use case is "Colon". Instead, another group of columns is decided by you, and they characterize the actual report you want to insert. For example, a report can be described by a <i>diagnosis</i>, the <i>age</i> and the <i>gender</i> of the patient: the <i>age</i>, the <i>gender</i> and the <i>diagnosis</i> will be three different columns of the file. If you have some doubts, you can download the examples in the section below. <span style={{'font-weight':'bold'}}>Please, make sure you do not call multiple columns with the same name. Moreover, if multiple rows contain the same (id_report, language), only one row is kept, the other are discarded.</span></li>

                                <li>Suppose the report file(s) are correct. In that case, you are provided with the list of columns' names characterizing your report (all except for the <i>institute</i>, <i>language</i>, <i>id_report</i> and <i>usecase</i>). You are asked to choose which columns will be displayed, hidden, or annotated. Each choice has a check button, and you are asked to select only one option.</li>
                                <li>One or more files containing the the ids of articles belonging to PubMed you want to annotate. These files must have a column called <i>ID</i> that is the ID of the PubMed article and a column called <i>usecase</i> that is the use case associated to that article. When the articles are uploaded, you can annotate the article's <i>title</i> and <i>abstract</i>.</li>
                                <li>One or more files containing the concepts needed to perform <i>linking</i> or <i>concepts identification</i>. These files must have four columns: a <i>concept_url</i> which is the URL of the concept in the ontology you chose, the <i>concept name</i>, which is the concept related to that URL, the <i>usecase</i> related to the concept and an <i>area</i> which is a category which can be associated to the concept (for example the concept whose <i>concept_name</i> is "Ulcer" can be associated to the <i>usecase</i> "Colon" and to the <i>area</i> "Diagnosis"). If you have some doubts, you can download the examples in the section below. <span style={{'font-weight':'bold'}}>If multiple rows contain the same (concept_url, usecase, area), only one row is kept, the other are discarded.</span></li>
                                <li>One or more files containing the annotation labels needed to perform label annotations. Each label may (or may not) describe the report. Each file containing the labels must have two columns: the <i>usecase</i> of the label and the <i>label</i> itself. If you have some doubts, going ahead with the configuration, you will be able to download the examples. <span style={{'font-weight':'bold'}}>If multiple rows contain the same (label, usecase), only one row is kept, the other are discarded.</span></li>
                            </ul>
                        </li>
                            <li>Automatic annotation is possible for <b>English</b> reports that belong to: <i> Colon, Uterine cervix, Lung</i> use cases. Automatic annotation is based on a set of labels we provided and on concepts belonging to the <a href={'http://examode.dei.unipd.it/ontology/'}>EXAMODE ontology</a>. You can automatically annotate your reports immediately after having configured MedTAG, otherwise you can do it whenever you want going to <i>Update Configuration -> Get Automatic Annotations.</i> Automatic annotations is available also on PubMed articles: <b>if you want to automatically annotate PubMed articles, make sure you upload the PubMed ids associating the correct use cases (colon, uterine cervix, lung).</b> </li>
                        </ul>
                        <div>If you have doubts, please check the <a href={'https://github.com/MedTAG/medtag-core/'}>GitHub page</a>. </div>
                        </div>
                        </Collapse><hr/>
                        <div>
                            <h4 style={{display:'inline-block'}}>The CSV files</h4><IconButton onClick={()=>SetShowCSVSection(prev=>!prev)}><ExpandMoreIcon style={{marginLeft:'2px'}} /></IconButton>
                        </div>
                        <Collapse style={{marginTop:'0px'}} in={ShowCSVSection}>

                        <div>We ask you to provide a set of <span style={{'font-weight':'bold'}}>CSV</span> files, where CSV means <i>Comma Separated Values</i>. Below we give some information about how to create the CSV files to configure MedTAG.
                            <ul>
                                <li>Make sure it is comma-separated. If you create your CSV using Microsoft Excel, the delimiter may be a semicolon instead of a comma.</li>
                                <li>All the columns <span style={{'font-weight':'bold'}}>must</span> have a value associated. If a column has the same value in multiple rows (this is the case of <i>usecase</i> or <i>area</i> columns), that value <span style={{'font-weight':'bold'}}>must always be reported</span>.</li>
                                <li>In the section below, you can download the templates and the examples. The columns' names we provide in the templates (and also in the first row of each example file) <span style={{'font-weight':'bold'}}>must be kept as they are (except for the columns you have to set in the report file)</span>, changing the names of <i>id_report, usecase, area, institute, language, concept_url, concept_name, label</i> columns will make the configuration fail.</li>
                                <li>If you build your CSV manually (not recommended), remember that if a column's value contains the comma in a specific row, that value must be enclosed between double quotes. (As it is done in the example of the concept: in row 3 <i>Rectum, NOS</i> is enclosed between double quotes because there is a comma between <i>Rectum</i> and <i>NOS</i>).</li>
                                <li>Depending on the tool you use to build your CSV files, all the values may be enclosed between double quotes, even if they do not contain any comma. This type of CSV files are accepted so that you can configure MedTAG without problems.</li>
                            </ul>
                        </div>
                        </Collapse><hr/>


                    <div>
                        <div><h4 style={{display:'inline-block'}}>Examples and Templates</h4><IconButton onClick={()=>SetShowExSection(prev=>!prev)}><ExpandMoreIcon style={{marginLeft:'2px'}} /></IconButton></div>
                        <Collapse style={{marginTop:'0px'}} in={ShowExSection}>

                        <div>
                        <ul>
                            <li><Row><Col md={3}>Reports file:</Col><Col md={4}><Button variant='info' size='sm' onClick={(e)=>onSaveExample(e,'reports')}>Download Example</Button>&nbsp;&nbsp;<Button variant='success' size='sm' onClick={(e)=>onSaveTemplate(e,'reports')}>Download Template</Button></Col><Col md={5}>If you use the template file replace <i>your_field_1, your_field_2, your_field_3</i> with the fields which characterize your reports (as many fields as you desire). </Col></Row>
                        </li>
                            <li><Row><Col md={3}>PubMed IDs file:</Col><Col md={4}><Button variant='info' size='sm' onClick={(e)=>onSaveExample(e,'pubmed')}>Download Example</Button>&nbsp;&nbsp;<Button variant='success' size='sm' onClick={(e)=>onSaveTemplate(e,'pubmed')}>Download Template</Button></Col><Col md={5}></Col></Row>
                            </li>
                        <li><Row><Col md={3}>Labels file:</Col><Col md={4}><Button variant='info' size='sm' onClick={(e)=>onSaveExample(e,'labels')}>Download Example</Button>&nbsp;&nbsp;<Button variant='success' size='sm' onClick={(e)=>onSaveTemplate(e,'labels')}>Download Template</Button></Col><Col md={5}></Col></Row>
                        </li>
                        <li><Row><Col md={3}>Concepts file:</Col><Col md={4}><Button variant='info' size='sm' onClick={(e)=>onSaveExample(e,'concepts')}>Download Example</Button>&nbsp;&nbsp;<Button variant='success' size='sm' onClick={(e)=>onSaveTemplate(e,'concepts')}>Download Template</Button></Col><Col md={5}></Col></Row>
                        </li>


                    </ul>
                            </div></Collapse><hr/>
                    </div>
                    <div style={{'margin-bottom':'30px'}}>In the database you have: {GroundTruthList} ground truths: this set includes:
                    <ul>
                        <li>The manually created ground-truths</li>
                        <li>The automatically created ground-truths revised by your team mates (if any)</li>
                        <li>The ground-truths created by the algorithm (if any)</li>
                    </ul></div><hr/>
                    <Button variant="primary" onClick={(e)=>onSaveAll('save')}>
                       Save the JSON ground truths and configure
                    </Button>&nbsp;&nbsp;
                    <Button variant="secondary" onClick={(e)=>SetShowModalSure(true)}>
                        Configure without saving
                    </Button>
                    </div>
                    <hr/>


                    {Redir && <Redirect  to="/configure" />}
                    {UpdateConfiguration && <Redirect  to="/updateConfiguration" />}
                </div></Container>
            </div>

            {ShowModalMissing === true  &&

            <Modal show={ShowModalMissing} onHide={()=>{SetShowModalMissing(false)}}>
                <Modal.Header closeButton>
                    <Modal.Title>Attention</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    <div>You do not have any ground-truth to save.</div>
                </Modal.Body>
                <Modal.Footer>

                    <Button variant="primary" onClick={handleCloseMissing}>
                        Ok
                    </Button>

                </Modal.Footer>
            </Modal>}

            {ShowModalSure === true && GroundTruthList === 0 && <Redirect  to="/configure" /> }
            {ShowModalSure === true && GroundTruthList > 0 && <Modal show={ShowModalSure} onHide={handleClose}>
                <Modal.Header closeButton>
                    <Modal.Title>Attention</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    <div>Are you sure you want to configure without saving the ground-truths?</div>
                </Modal.Body>
                <Modal.Footer>
                    <Button variant="primary" onClick={(e)=>onSaveAll('save')}>
                        No, save
                    </Button>&nbsp;&nbsp;
                    <Button variant="secondary" onClick={(e)=>onSaveAll('skip')}>
                        Yes
                    </Button>

                </Modal.Footer>
            </Modal>}
        </div>



    );
}


export default InfoAboutConfiguration;
