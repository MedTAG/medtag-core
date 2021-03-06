import React, {Component, useContext, useEffect, useState} from 'react'
import axios from "axios";
import 'bootstrap/dist/css/bootstrap.min.css';
import {Container,Row,Col} from "react-bootstrap";
import '../../Report/report.css';
import {AppContext, MentionContext} from "../../../App";
import '../tables.css'
import ReportListUpdated from "../../Report/ReportListUpdated";
import ExpandMoreIcon from "@material-ui/icons/ExpandMore";
import IconButton from "@material-ui/core/IconButton";
import Spinner from "react-bootstrap/Spinner";
import Button from "react-bootstrap/Button";
import Collapse from "@material-ui/core/Collapse";
import MentionList from "../../Mentions/MentionList";
import Mention from "../../Mentions/Mention";
import '../AnnotationStats/reportsmodal.css'
import Badge from "react-bootstrap/Badge";
import {Divider} from "@material-ui/core";
import LabelList from "../../Labels/LabelList";
import SubmitButtons from "../../General/SubmitButtons";
// axios.defaults.xsrfCookieName = "csrftoken";
// axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";
import { alpha, styled } from '@mui/material/styles';
import Alert from "react-bootstrap/Alert";
import { pink } from '@mui/material/colors';
// import Switch from '@mui/material/Switch';
import SubmitModal from "../../General/SubmitModal";
// import "react-toggle/style.css"
// import Switch from "react-bootstrap/Switch";
import Form from 'react-bootstrap/Form'


function ModalAnnotation(props) {

    const { checks,index,labelsList,loadingMentions,showautoannotation,selectedbatch,username,radio,selectedUse,labelsToInsert,userLabels,selectedInstitute,selectedLanguage,color,tokens,fields,loadingReport,loadingColors,showannotations,finalcount,fieldsToAnn,reached,orderVar, errorSnack,reports, reportString, insertionTimes } = useContext(AppContext);
    const [Reports,SetReports] = useState([])
    const [ReportString, setReportsString] = reportString;
    //Report sections
    const [RadioChecked, SetRadioChecked] = radio;
    const [ShowAutoAnn,SetShowAutoAnn] = showautoannotation;

    const [Index,SetIndex] = index
    const [LoadingReport, SetLoadingReport] = loadingReport;
    const [SelectedLang,SetSelectedLang] = selectedLanguage
    const [SelectedInstitute,SetSelectedInstitute] =selectedInstitute
    const [SelectedUse,SetSelectedUse] = selectedUse
    const [SelectedBatch,SetSelectedBatch] = selectedbatch
    const [Children,SetChildren] = tokens;
    const [selectedStats,SetSelectedStata] = useState('none')
    const [RobotPresence,SetRobotPresence] = useState(false)
    const [ShowLabelsStats,SetShowLabelsStats] = useState(true)
    const [ShowMentionsStats,SetShowMentionsStats] = useState(false)
    const [ShowConceptsStats,SetShowConceptsStats] = useState(false)
    const [ShowLinkingStats,SetShowLinkingStats] = useState(false)
    const [newInd,SetNewInd] = useState(false)
    const [FinalCountReached, SetFinalCountReached] = reached;
    const [FinalCount, SetFinalCount] = finalcount;
    const [labels, setLabels] = labelsList;
    const [Fields, SetFields] = fields;
    const [Checks, setChecks] = checks;
    const [IsRobot,SetIsRobot] = useState(false)
    const [LabToInsert,SetLabToInsert] =labelsToInsert;
    const [FieldsToAnn, SetFieldsToAnn] = fieldsToAnn;
    const [ShowAnnotationsStats,SetShowAnnotationsStats] = showannotations;
    const [mentions_to_show, SetMentions_to_show] = useState([]);
    const [LoadingMentions, SetLoadingMentions] = loadingMentions;
    const [LoadingMentionsColor, SetLoadingMentionsColor] = loadingColors;
    const [Color, SetColor] = color
    const [EXAPresenceLabels,SetEXAPresenceLabels] = useState(false)
    const [EXAPresenceConcepts,SetEXAPresenceConcepts] = useState(false)
    const [labels_to_show, setLabels_to_show] = userLabels;
    const [Username,SetUsername] = username
    const [Success,SetSuccess] = useState(0)
    useEffect(()=>{
        if(props.row !== false) {
            axios.get("http://examode.dei.unipd.it/exatag/annotationlabel/all_labels",{params:{usecase:SelectedUse}}).then(response => {
                setLabels(response.data['labels'])
            })
            var ns_id = 'Human'
            var username_to_call = Username

            axios.get("http://examode.dei.unipd.it/exatag/check_auto_presence_for_configuration",
                {params: {batch:SelectedBatch,usecase:SelectedUse,institute:SelectedInstitute,language:SelectedLang,report_type:'reports'}})
                .then(response => {
                    if(response.data['count'] > 0){
                        SetRobotPresence(true)
                    }
                    else{
                        SetRobotPresence(false)
                    }})
                .catch(error=>{
                    console.log(error)
                })

        }


    },[props.report,props.language,props.row])

    useEffect(()=>{
        if(props.row !== false){
            var ns_id = 'Human'
            if(IsRobot === true){
                ns_id = 'Robot'
            }
            axios.get("http://examode.dei.unipd.it/exatag/annotationlabel/user_labels", {params: {ns_id:ns_id,username:Username,language:props.language,report_id: props.report}})
                .then(response => {setLabels_to_show(response.data['labels']);
                    // SetLoadingLabels(false);
                })
        }

    },[labels,props.row,IsRobot])

    useEffect(()=>{
        if(labels.length > 0){
            console.log('labels_to_sh',labels_to_show)
            var user_checks = new Array(labels.length).fill(false)
            var array = []
            SetLabToInsert(labels_to_show)
            if(labels_to_show.length>0){
                SetRadioChecked(true)
                labels_to_show.map((lab) => {
                    var ind = labels.indexOf(lab)
                    user_checks[ind] = true
                })

            }
            else{
                SetRadioChecked(false)

            }
            setChecks(user_checks)
        }
    },[labels_to_show]);

    useEffect(()=>{
        console.log('lab',labels_to_show)
    },[labels_to_show])

    useEffect(()=>{
        if(SelectedUse !== '' && SelectedInstitute !== '' && SelectedLang !== '' && SelectedBatch !== ''){
            setReportsString('')
            axios.get("http://examode.dei.unipd.it/exatag/get_reports", {params: {all: 'all',batch:SelectedBatch,usec:SelectedUse,lang:SelectedLang,institute:SelectedInstitute}}).then(response => {
                SetReports(response.data['report']);})
        }


    },[SelectedUse,SelectedInstitute,SelectedLang,SelectedBatch])

    useEffect(()=>{
        setReportsString('')
        SetMentions_to_show([])


        axios.get("http://examode.dei.unipd.it/exatag/check_presence_exa_conc_lab", {params: {id_report:props.report,language:props.language}})
            .then(response => {
                if(response.data['labels'] === true){
                    SetEXAPresenceLabels(true)
                }
                else{
                    SetEXAPresenceLabels(false)

                }
                if(response.data['concepts'] === true){
                    SetEXAPresenceConcepts(true)
                }
                else{
                    SetEXAPresenceConcepts(false)

                }})
            .catch(error=>{
                console.log(error)
            })

    },[])



    useEffect(()=>{
        if(Reports.length > 0){
            SetLoadingReport(true)

            if(newInd >= 0){
                axios.get("http://examode.dei.unipd.it/exatag/report_start_end", {params: {language:SelectedLang,report_id: Reports[newInd].id_report.toString()}}).then(response => {SetFinalCount(response.data['final_count']);
                    setReportsString(response.data['rep_string']); SetFinalCountReached(false);
                })
                axios.get("http://examode.dei.unipd.it/exatag/get_fields",{params:{report:props.id_report}}).then(response => {SetFields(response.data['fields']);SetFieldsToAnn(response.data['fields_to_ann']);SetLoadingReport(false)})

            }

        }


    },[newInd])



    useEffect(()=>{
        if(Reports.length > 0){

            if(props.id_report !== false){
                Reports.map((report,ind)=>{
                    if(report.id_report === props.report){

                        SetNewInd(ind)
                    }

                })
            }
        }



    },[props.report,Reports])




    // const GreenSwitch = styled(Switch)(({ theme }) => ({
    //     '& .MuiSwitch-switchBase.Mui-checked': {
    //         color: pink[600],
    //         '&:hover': {
    //             backgroundColor: alpha(pink[600], theme.palette.action.hoverOpacity),
    //         },
    //     },
    //     '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': {
    //         backgroundColor: pink[600],
    //     },
    // }));



    const label = { inputProps: { 'aria-label': 'Switch demo' } };
    return (
        <div className='container-fluid'>

            {(newInd !== false  && ReportString !== '' && (FieldsToAnn.length > 0 || Fields.length > 0) && Reports.length > 0) ? <Row>


                <Col md={6} style={{fontSize:'1rem'}}>
                    <div className='report_modal'>
                        <ReportListUpdated report_id = {Reports[newInd].id_report} report = {Reports[newInd].report_json} action={selectedStats}/>

                    </div>
                </Col>
                <Col  md={6}>

                    <div className='modalContainer'>
                        {ShowAutoAnn === false && <div>Select an annotation mode:{' '}
                            {/*<label>*/}
                            {/*        <Toggle*/}
                            {/*            checked = {IsRobot}*/}
                            {/*            icons={false}*/}
                            {/*            onChange={()=> {*/}
                            {/*                SetIsRobot(p => !p)*/}
                            {/*            }} />{'  '}*/}
                            {/*    <span>No icons</span>*/}
                            {/*</label>*/}
                            {/*<label>*/}
                            {/*    <span><b>Manual</b></span>{'  '}*/}

                            {/*    <Toggle*/}
                            {/*        checked = {IsRobot}*/}
                            {/*        icons={false}*/}
                            {/*        onChange={()=> {*/}
                            {/*            SetIsRobot(p => !p)*/}
                            {/*        }} />{'  '}*/}
                            {/*    <span><b>Computer-aided</b></span>*/}

                            {/*</label>*/}

                            {/*<span><b>Manual</b></span>*/}
                            <span><b>Manual</b>&nbsp;&nbsp;
                                <label><Form.Check
                                    style={{marginRight:0,verticalAlign:'bottom'}}
                                    type="switch"
                                    id="custom-switch"
                                    inline
                                    disabled={RobotPresence === false}
                                    onChange={() => {
                                        SetIsRobot(p => !p)}}
                                    checked = {IsRobot}
                                /></label>&nbsp;&nbsp;<b>Computer-aided</b>
                            </span>


                            {/*<span>*/}
                            {/*    <label><b>Manual</b></label>*/}
                            {/*      <Form.Check*/}
                            {/*          type="switch"*/}
                            {/*          id="custom-switch"*/}
                            {/*          inline*/}
                            {/*          onChange={() => {*/}
                            {/*              SetIsRobot(p => !p)}}*/}
                            {/*          checked = {IsRobot}*/}
                            {/*      />*/}
                            {/*    <label><b>Computer-aided</b></label>*/}
                            {/*</span>*/}

                            {/*<span><b>Computer-aided</b></span>*/}



                            {/*<span><b>Manual</b></span>*/}
                            {/*<span><Switch size='md' color='pink' onChange={() => {*/}
                            {/*    SetIsRobot(p => !p)*/}
                            {/*}} /></span>*/}
                            {/*<span><b>Computer-aided</b></span>*/}
                        </div>}

                        <LabelList labels={labels} report_id = {props.report} />

                        <SubmitModal row = {props.row} robot = {IsRobot} reports = {Reports} language = {props.language} ind = {newInd} token={'annotation'} token_prev={'annotation_prev'} token_next = {'annotation_next'}/>
                    </div>


                </Col>
            </Row> : <div className='spinnerDiv'><Spinner animation="border" role="status"/></div>}


        </div>
    );
}


export default ModalAnnotation