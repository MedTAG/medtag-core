import '../../App.css';
import {AppContext} from '../../App';
import React, {useState, useEffect, useContext, createContext} from "react";
import './compStyle.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'react-bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'react-bootstrap';
import {Container,Row,Col} from "react-bootstrap";
import Button from "react-bootstrap/Button";
import '../General/first_row.css';
import {
    CircularProgressbar,ProgressProvider,
    CircularProgressbarWithChildren,
    buildStyles
} from "react-circular-progressbar";
import "react-circular-progressbar/dist/styles.css";

// import { easeQuadInOut } from "d3-ease";
// import AnimatedProgressProvider from "./AnimatedProgressProvider";
import ChangingProgressProvider from "./ChangingProgressProvider";

import SelectMenu from "../SelectMenu/SelectMenu";

import SideBar from "../General/SideBar";
import ProgressiveComponent from "./ProgressiveComponent";
import axios from "axios";
import Spinner from "react-bootstrap/Spinner";
import Form from "react-bootstrap/Form";
import {Collapse} from "@mui/material";
import {faChevronDown, faChevronUp} from "@fortawesome/free-solid-svg-icons";
import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";

function MyStats() {


    const { showbar,username,usecaseList,annotation,batchNumber,language,institute,reports,languageList,instituteList } = useContext(AppContext);
    const [Annotation,SetAnnotation] = annotation;
    const [UseCaseList,SetUseCaseList] = usecaseList;
    const [LanguageList,SetLanguageList] = languageList;
    const [InstituteList,SetInstituteList] = instituteList;
    const [Aux,SetAux] = useState(false)
    const [ShowBar,SetShowBar] = showbar;
    const [Username,SetUsername] = username;
    const [Reports,SetReports] = reports;
    // const [ShowStats,SetShowStats] = useState(new Array(usecaseList.length+1).fill(false))
    const [StatsArray,SetStatsArray] = useState(false)
    const [StatsArrayPubMed,SetStatsArrayPubMed] = useState(false)
    const [StatsArrayPercent,SetStatsArrayPercent] = useState(false)
    const [StatsArrayPercentPubMed,SetStatsArrayPercentPubMed] = useState(false)
    const [Actions,SetActions] = useState(['labels','mentions','concepts','concept-mention'])
    const [SelectedLang,SetSelectedLang] = useState('')
    const [SelectedInstitute,SetSelectedInstitute] = useState('')
    const [SelectedBatch,SetSelectedBatch] = useState('')
    const [StatsAuto,SetStatsAuto] = useState(0)
    const [ChosenStats,SetChosenStats] = useState('')
    const [UsesExtraxcted,SetUsesExtracted] = useState([])
    const [Language,SetLanguage] = language;
    const [Institute,SetInstitute] = institute;
    const [BatchNumber,SetBatchNumber] = batchNumber;
    const [BatchList,SetBatchList] = useState([]);
    const [ShowOptions,SetShowOptions] = useState(true)

    useEffect(()=>{
        axios.get("get_usecase_inst_lang").then(response => {
            SetUseCaseList(response.data['usecase']);
            SetUsesExtracted(response.data['usecase']);
            SetLanguageList(response.data['language']);
            SetInstituteList(response.data['institute']);

        })
            .catch(function(error){
                console.log('error: ',error)
            })


        var username = window.username
        // console.log('username', username)
        SetUsername(username)
        axios.get('get_presence_robot_user',{params:{username:username}}).then(function(response){
            if(response.data['auto_annotation_count'] > 0){
                SetStatsAuto(true)
            }
            else{
                SetStatsAuto(false)
                SetChosenStats('Human')
            }


        }).catch(function(error){
            console.log('error: ',error)
        })


        axios.get('get_batch_list').then(response=>SetBatchList(response.data['batch_list']))

    },[])

    useEffect(()=>{
        if(SelectedLang === ''){
            SetSelectedLang(Language)
        }
    },[Language])

    useEffect(()=>{
        if(SelectedInstitute === ''){
            SetSelectedInstitute(Institute)
        }
    },[Institute])

    useEffect(()=>{
        if(SelectedBatch === ''){
            SetSelectedBatch(BatchNumber)
        }
    },[BatchNumber])



    useEffect(()=>{
        if(ChosenStats !== '' && SelectedLang !== '' && SelectedInstitute !== '' && SelectedBatch !== ''){
            SetStatsArray(false)
            SetStatsArrayPercent(false)


            axios.get("get_stats_array_per_usecase",{params:{mode:ChosenStats,language:SelectedLang,institute:SelectedInstitute,batch:SelectedBatch}}).then(response => {
                SetStatsArrayPercent(response.data['medtag']['percent'])
                SetStatsArray(response.data['medtag']['original'])
                SetStatsArrayPercentPubMed(response.data['pubmed']['percent'])
                SetStatsArrayPubMed(response.data['pubmed']['original'])
            })
                .catch(function(error){
                    console.log('error: ',error)
                })
        }

    },[ChosenStats,SelectedLang,SelectedInstitute,SelectedBatch])





    function changeStatsChosen(){
        var prev = ChosenStats
        SetChosenStats('')

        if(prev === 'Human'){
            SetChosenStats('Robot')
        }
        else{
            SetChosenStats('Human')
        }
    }
    function handleChangeLangSelected(option){
        console.log('selected_lang',SelectedLang)
        SetSelectedLang(option.target.value)
    }
    function handleChangeInstSelected(option){
        console.log('selected_lang',SelectedLang)
        SetSelectedInstitute(option.target.value)
    }
    function handleChangeBatchSelected(option){
        console.log('selected_lang',SelectedLang)
        SetSelectedBatch(option.target.value)
    }

    return (
        <div className="App">
            <div>
                <Container fluid>
                    {ShowBar && <SideBar />}
                    {(InstituteList.length >= 0 && LanguageList.length >=0 && UseCaseList.length >= 0) && <div><SelectMenu />
                        <hr/></div>}


                    <div style={{'text-align':'center', 'margin-bottom':'3%'}}><h2>MY STATISTICS</h2></div>

                    {/*<div style={{'margin-bottom':'3%'}}>In this section you can check how many reports you have annotated so far for each action and use case.<br/> Click <Button variant='info' size='sm'>here</Button> to check your statistics concerning the automatic annotations.</div>*/}
                    {StatsAuto === true && <div style={{'text-align':'center'}}>
                        {StatsAuto === true && ChosenStats === '' && <div >
                            <div style={{marginBottom:'5%',marginTop:'5%'}}><h5>Select what type of annotations you desire to check the statistics of.</h5></div>
                            <Row>
                                <Col md={2}></Col>
                                <Col md={4}><Button size='lg' variant='success' onClick={()=>SetChosenStats('Human')}><b>Manual</b></Button></Col>
                                <Col md={4}><Button size='lg' variant='primary' onClick={()=>SetChosenStats('Robot')}><b>Automatic</b></Button></Col>
                                <Col md={2}></Col>
                            </Row>
                        </div>}


                    </div>}

                    {(ChosenStats !== '' || StatsAuto === false) && SelectedLang !== '' && <div style={{'text-align':'center'}}>
                        {(StatsArray && StatsArrayPercent && StatsArrayPubMed && StatsArrayPercentPubMed) ? <div>
                            {StatsAuto === true && <div style={{marginTop:'2%',marginBottom:'2%'}}>Check the <Button size = 'sm' variant='info' onClick={()=>changeStatsChosen()}>{ChosenStats === 'Human' ? <b>Automatic</b> : <b>Manual</b>} annotations</Button><hr/></div>}
                            <div style={{textAlign:'center'}}><Button size='sm' onClick={()=>SetShowOptions(prev=>!prev)}>Options <FontAwesomeIcon icon={ShowOptions ? faChevronDown : faChevronUp}/></Button></div>
                            <Collapse in={ShowOptions}>
                                <>
                                    {SelectedLang !== ''  &&
                                    <><div>Select the language of the reports you want to check the statistics of</div>
                                        <Row><Col md={4}></Col>
                                            <Col md={4}><Form.Control style={{'text-align':'center'}} value={SelectedLang} as="select" onChange={(option)=>handleChangeLangSelected(option)} placeholder="Select a language...">
                                                {/*<option value="">Choose a language</option>*/}
                                                {LanguageList.map((language)=>
                                                    <option value={language}>{language}</option>
                                                )}
                                            </Form.Control>
                                            </Col><Col md={4}></Col></Row><hr/></>}
                                    {SelectedInstitute !== ''  &&
                                    <><div>Select the institute of the reports you want to check the statistics of</div>
                                        <Row><Col md={4}></Col>
                                            <Col md={4}><Form.Control style={{'text-align':'center'}} value={SelectedInstitute} as="select" onChange={(option)=>handleChangeInstSelected(option)} placeholder="Select a institute...">
                                                {InstituteList.map((institute)=>
                                                    <option value={institute}>{institute}</option>
                                                )}
                                            </Form.Control>
                                            </Col><Col md={4}></Col></Row><hr/></>}
                                    {SelectedBatch !== ''  && BatchList.length > 1 &&
                                    <><div>Select the batch of the reports you want to check the statistics of</div>
                                        <Row><Col md={4}></Col>
                                            <Col md={4}><Form.Control style={{'text-align':'center'}} value={SelectedBatch} as="select" onChange={(option)=>handleChangeBatchSelected(option)} placeholder="Select a batch...">
                                                {/*<option value="">Choose an institute</option>*/}
                                                {BatchList.map((batch)=>
                                                    <option value={batch}>{batch}</option>
                                                )}
                                            </Form.Control>
                                            </Col><Col md={4}></Col></Row><hr/></>}
                                </>
                            </Collapse>




                            <div>{UsesExtraxcted.map((usecase,ind)=>
                                <div>
                                    {StatsArray && StatsArray[usecase]['all_reports'] > 0 && <div>
                                        <div style={{'font-size':'1.5rem','margin':'5px'}}>USE CASE <span style={{'font-weight':'bold'}}>{usecase}</span>: {StatsArray[usecase]['all_reports']} reports</div>
                                        {<div><b>Language: <i style={{color: 'royalblue'}}>{SelectedLang}</i></b></div>}
                                        {/*{ChosenStats === 'Human' ? <div><b>Language: <i style={{color: 'royalblue'}}>{SelectedLang}</i></b></div> : <div><b>Language: <i style={{color: 'royalblue'}}>english</i></b></div>}*/}
                                        <div><b>Institute: <i style={{color: 'royalblue'}}> {SelectedInstitute}</i></b></div>

                                        <div style={{'text-align':'center'}}>
                                            {SelectedLang !== '' && <Row>
                                                {
                                                    Actions.map((o,indice)=>
                                                        <Col md={3}>
                                                            <ProgressiveComponent stats_array_percent={StatsArrayPercent[usecase]} stats_array={StatsArray[usecase]} action={o} index={indice}/>
                                                        </Col>
                                                    )
                                                }

                                            </Row>}
                                            <hr/></div></div>}

                                </div>
                            )}</div>
                            <div>


                                {UsesExtraxcted.map((usecase,ind)=>
                                    <div>
                                        {StatsArrayPubMed && StatsArrayPubMed[usecase]['all_reports'] > 0 && <div>
                                            <div style={{'font-size':'1.5rem','margin':'5px'}}><span style={{color:'royalblue'}}><b>PUBMED</b></span> - USE CASE <span style={{'font-weight':'bold'}}>{usecase}</span>: {StatsArrayPubMed[usecase]['all_reports']} reports</div>
                                            <div><b>Language: <i style={{color: 'royalblue'}}> english</i></b></div>
                                            <div><b>Institute: <i style={{color: 'royalblue'}}> PUBMED</i></b></div>
                                            <div style={{'text-align':'center'}}>
                                                <Row>
                                                    {
                                                        Actions.map((o,indice)=>
                                                            <Col md={3}>
                                                                <ProgressiveComponent stats_array_percent={StatsArrayPercentPubMed[usecase]} stats_array={StatsArrayPubMed[usecase]} action={o} index={indice}/>
                                                            </Col>
                                                        )
                                                    }

                                                </Row>
                                                <hr/></div></div>}

                                    </div>
                                )}</div>
                        </div> :  <div className='spinnerDiv'><Spinner animation="border" role="status"/></div>}
                    </div>}
                    {(ChosenStats === '' && StatsAuto === 0) && <div className='spinnerDiv'><Spinner animation="border" role="status"/></div>}

                </Container>

            </div>


        </div>



    );
}

export default MyStats;
