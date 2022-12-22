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
import Form from "react-bootstrap/Form";
import './conf.css';

import '../General/first_row.css';

import SelectMenu from "../SelectMenu/SelectMenu";
import {
    faArrowLeft, faDownload,faTimes,faBars
} from "@fortawesome/free-solid-svg-icons";
import SideBar from "../General/SideBar";
import axios from "axios";
import Spinner from "react-bootstrap/Spinner";
import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";
import Modal from "react-bootstrap/Modal";
import {Link,Redirect} from "react-router-dom";
import {ConfigureContext} from "./Configure";

function ConfigureResult() {


    const { errormessage,pubmedusesinserted,message,warningmessage,loadingresponse,usesinserted,fieldsextra } = useContext(ConfigureContext);

    const [OnlyPub,SetOnlyPub] = useState(false)
    const [AutoMedTagReports,SetAutoMedTagReports] = useState(false)
    const [LoadingAnnoResp,SetLoadingAnnoResp] = useState(false)

    const [WarningMessage, SetWarningMessage] = warningmessage
    const [UsesInserted,SetUsesInserted] = usesinserted
    const [PubMedUsesInserted,SetPubMedUsesInserted] = pubmedusesinserted

    const [AutoAnno,SetAutoAnno] = useState(false)

    const [FieldsUseCasesToExtract,SetFieldsUseCasesToExtract] = fieldsextra
    const [Disabled,SetDisabled] = useState(true)
    const [Message, SetMessage] = message
    const [ErrorMessage, SetErrorMessage] = errormessage
    const [AutoAnnoCompleted,SetAutoAnnoCompleted] = useState(false)
    const [LoadingResponse, SetLoadingResponse] = loadingresponse


    const [PubMedMissingAuto,SetPubMedMissingAuto] = useState({})

    const [AutoPub,SetAutoPub] = useState(0)

    const [LoadingPubMedResp,SetLoadingPubMedResp] = useState(false)
    const [AutoPubMedCompleted,SetAutoPubMedCompleted] = useState(false)
    const [AutoMessage,SetAutoMessage] = useState('')
    const [PubMessage,SetPubMessage] = useState('')


    useEffect(()=>{
        if(LoadingResponse === false){
            window.scrollTo(0,0)
        }
    },[LoadingResponse])

    useEffect(()=>{
        if(Message !== ''){
            axios.get('http://0.0.0.0:8000/get_post_fields_for_auto').then(function(response){
                SetFieldsUseCasesToExtract(response.data['total_fields'])

                var empty = true
                Object.keys(response.data['total_fields']).map(key=>{
                    if(response.data['total_fields'][key].length > 0){
                        empty = false
                    }
                })
                if(empty){
                    SetOnlyPub(true)
                }
                else{
                    SetOnlyPub(false)
                }

            }).catch(function(error){
                console.log('error: ',error)
            })
            axios.get("http://0.0.0.0:8000/pubmed_missing_auto").then(response => {
                SetPubMedMissingAuto(response.data);

            }).catch(function (error){console.log(error)})
        }
    },[Message])



    function change_input(){
        var dis = []
        UsesInserted.map((el,ind)=> {
            var elems = Array.from(document.getElementsByName(el))
            var bool = true
            elems.map(input_lab => {
                if (input_lab.checked === true) {
                    bool = false

                }

            })
            dis.push(bool)

        })
        if(dis.every(v => v === false)){
            SetDisabled(false)
            SetAutoMedTagReports(true)

        }
        else{
            SetDisabled(true)
        }


    }


    useEffect(()=>{
        console.log('uses',UsesInserted)
    },[UsesInserted])

    function get_auto_ann(key){
        var selected_obj = {}
        window.scroll(0,0)



        console.log(AutoPub)
        console.log(AutoMedTagReports)
        if (key === 'pubmed'){
            SetLoadingPubMedResp(true)
            PubMedUsesInserted.map(el=>{
                selected_obj[el] = []

                selected_obj[el].push('abstract')
                selected_obj[el].push('title')
            })
            axios.post('http://0.0.0.0:8000/create_auto_annotations',{
                    usecase:PubMedUsesInserted,
                    selected:selected_obj,
                    batch:1,
                    report_type:key
                }
            )
                .then(function(response){
                    console.log(response.data)
                    // setShowModalAuto(false)
                    SetLoadingPubMedResp(false)
                    SetAutoPubMedCompleted(true)
                    SetPubMessage('OK')


                }).catch(function (error) {
                //alert('ATTENTION')
                SetLoadingPubMedResp(false)
                SetAutoPubMedCompleted(false)
                SetPubMessage('ERROR')

                console.log(error);
            });
        }
        else if (key === 'reports'){
            SetLoadingAnnoResp(true)
            key = 'reports'
            UsesInserted.map(el=>{
                selected_obj[el] = []
                var elems = Array.from(document.getElementsByName(el))
                elems.map(elem=>{
                    if(elem.checked === true){
                        selected_obj[el].push(elem.value)
                    }
                })
            })
            axios.post('http://0.0.0.0:8000/create_auto_annotations',{
                    usecase:UsesInserted,
                    selected:selected_obj,
                    batch:1,
                    report_type:key
                }
            )
                .then(function(response){
                    console.log(response.data)
                    // setShowModalAuto(false)
                    SetLoadingAnnoResp(false)
                    SetAutoAnnoCompleted(true)
                    SetAutoMessage('OK')


                }).catch(function (error) {
                //alert('ATTENTION')
                SetLoadingAnnoResp(false)
                SetAutoAnnoCompleted(false)
                SetAutoMessage('ERROR')

                console.log(error);
            });
        }


    }


    useEffect(()=>{
        console.log(UsesInserted)
        console.log(FieldsUseCasesToExtract)
    },[UsesInserted,FieldsUseCasesToExtract])


    return (
        <div className="App">

            {(LoadingResponse === true ) ? <div className='spinnerDiv'><Spinner animation="border" role="status"/></div>:
                <div>

                    {Message !== '' &&
                    <Container fluid>
                        {LoadingResponse === false ?<div>
                            <div>
                                <h2>Your new configuration is ready</h2>
                                <div>{Message}</div>
                                {(PubMedUsesInserted.length > 0 || UsesInserted.length > 0) ? <div><hr/>
                                    <div>
                                        You inserted reports related to the following use cases: {UsesInserted.join(', ')}. For them it is
                                        possible to perform automatic annotation. Click on <i>Auto Annotate</i> if you want to automatically annotate these reports otherwise cick on <i>Login</i>.
                                        If you prefer to automatically annotate them later, please, click on the side bar menu <FontAwesomeIcon icon={faBars}/> and go to: <i>Configure -> Update Configuration -> Get automatic annotations.</i>
                                    </div>
                                    <hr/>
                                    {AutoAnno === false ? <div>
                                        <Row>
                                            <Col md={3}></Col>
                                            <Col md={2}>
                                                <>
                                                    <span><a href="http://0.0.0.0:8000/logout"><Button variant = 'primary'>Login</Button></a></span>
                                                </>
                                            </Col>
                                            <Col md={1}></Col>
                                            <Col md={2}>
                                                <Button onClick={()=>SetAutoAnno(true)} variant='success'>Auto Annotate</Button>
                                            </Col>
                                            <Col md={3}>

                                            </Col>
                                        </Row>

                                    </div> : <div>
                                        <div>
                                            {LoadingAnnoResp === false ?
                                                <>{UsesInserted.length > 0 && Object.keys(FieldsUseCasesToExtract).length > 0 && OnlyPub === false && <>
                                                    <div>Select for each use case the fields you want to automatically annotate</div>
                                                    {UsesInserted.map(opt=>
                                                    <>{FieldsUseCasesToExtract[opt].length > 0 && <div>
                                                        <h5>{opt}</h5>
                                                        <div style={{'margin-bottom':'2%'}}><i>Select <b>at least</b> a field</i></div>

                                                        {AutoAnnoCompleted === false && <div style={{'margin-bottom':'2%'}}>
                                                            {FieldsUseCasesToExtract[opt].map(field=>
                                                                <label>
                                                                    <input name={opt} value={field} onChange={()=>change_input()} type="checkbox" />{' '}
                                                                    {field}&nbsp;&nbsp;&nbsp;&nbsp;
                                                                </label>
                                                            )}

                                                        </div>}

                                                    </div>}</>
                                                )}
                                                    <div style={{'text-align':'center','margin-top':'2%'}}>
                                                        {AutoAnnoCompleted === false ? <div style={{margin:'2%'}}><Button id='commit_extracted' disabled={Disabled} onClick={()=>get_auto_ann('reports')} size='lg' variant='success'>Get the automatic annotations</Button></div> : <b>{AutoMessage}</b>}
                                                    </div></>}

                                                </> : <div className='spinnerDiv'><Spinner animation="border" role="status"/><div>Please wait, the annotation process might take some time</div></div>}
                                        </div>
                                        <hr/>
                                        {LoadingPubMedResp === false ? <> { PubMedMissingAuto['tot'] > 0 && <div>
                                            You inserted PubMed articles' ids for one or more the following use cases: <b>colon, uterine cervix, lung</b>. Do you want to automatically annotate them?
                                            <div style={{'text-align':'center','margin-top':'2%'}}>
                                                {AutoPubMedCompleted === false ? <div style={{margin:'2%'}}><Button id='commit_extracted' onClick={()=>get_auto_ann('pubmed')} size='lg' variant='success'>Get the automatic annotations</Button></div> : <b>{PubMessage}</b>}
                                            </div>


                                        </div>}
                                        </> : <div className='spinnerDiv'><Spinner animation="border" role="status"/><div>Please wait, the annotation process might take some time</div></div>}
                                        <hr/>
                                        <div style={{'text-align':'center','margin-top':'2%'}}>
                                            <div><a href="http://0.0.0.0:8000/logout"><Button variant = 'primary'>Login</Button></a></div>
                                        </div>



                                    </div>}

                                </div> : <div style={{'text-align':'center','margin-top':'2%'}}>
                                    <div><a href="http://0.0.0.0:8000/logout"><Button variant = 'primary'>Login</Button></a></div>
                                </div>}



                            </div>

                        </div> : <div className='spinnerDiv'><Spinner animation="border" role="status"/></div>}

                    </Container>
                    }
                    {ErrorMessage !== '' &&
                    <Container fluid>
                        <div>
                            <h2>An error occurred</h2>
                            <div>{ErrorMessage}</div>
                            <hr/>
                            <div>Please, do the configuration again</div>

                        </div>
                        <div style={{'text-align':'center'}}>
                            <span><Link to="/infoAboutConfiguration"><Button variant='success'>Back to configure</Button></Link></span>&nbsp;&nbsp;
                        </div>
                    </Container>
                    }
                    {WarningMessage !== '' &&
                    <Container fluid>
                        <div>
                            <div>
                                <h2>Your new configuration is ready</h2>
                                <div>{WarningMessage}</div>
                                <hr/>
                                <div>Log in with your credentials.</div>

                            </div>

                        </div>
                        <div style={{'text-align':'center'}}>
                            <span><a href="http://0.0.0.0:8000/logout"><Button variant = 'primary'>Login</Button></a></span>
                        </div>
                    </Container>
                    }


                </div>}


        </div>



    );
}



export default ConfigureResult;


