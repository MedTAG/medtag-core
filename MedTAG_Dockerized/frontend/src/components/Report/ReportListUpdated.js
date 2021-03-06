import React, {Component, useContext, useEffect, useState} from 'react'
import axios from "axios";
import 'bootstrap/dist/css/bootstrap.min.css';
import {Container, Row, Col, OverlayTrigger} from "react-bootstrap";
import './report.css';
import {AppContext, MentionContext} from "../../App";
import Button from "react-bootstrap/Button";
import {faTimesCircle, faPencilAlt, faAngleRight, faSignOutAlt} from '@fortawesome/free-solid-svg-icons';
import Badge from "react-bootstrap/Badge";
import ReportSection from "./ReportSection";
import ReportSelection from "./ReportSelection";
import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";
import ErrorSnack from "./ErrorSnack";
import Spinner from "react-bootstrap/Spinner";
import Tooltip from "react-bootstrap/Tooltip";
// axios.defaults.xsrfCookieName = "csrftoken";
// axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";
function ReportListUpdated(props) {

    const { selectedLang,save,loadingReport,tokens,showautoannotation,finalcount,reached,userchosen,report_type,showmajoritymodal,showmajoritygt,annotation,action,language,showmember,username,showmajority,report,index,institute,showannotations,showreporttext,fields,fieldsToAnn,orderVar, errorSnack,reports, reportString, insertionTimes } = useContext(AppContext);
    const [Fields,SetFields] = fields;
    const [Username,SetUsername] = username
    const [ShowMajorityModal,SetshowMajorityModal] = showmajoritymodal
    const [ReportType, SetReportType] = report_type
    const [ShowAutoAnn,SetShowAutoAnn] = showautoannotation;
    const [ShowMemberGt,SetShowMemberGt] =showmember
    const [ShowMajorityGt,SetShowMajorityGt] = showmajority
    const [Report, setReport] = report;
    const [Language,SetLanguage] = language;
    const [Action,SetAction] = action
    const [Children,SetChildren] = tokens;
    const [LoadingReport, SetLoadingReport] = loadingReport;
    const [FieldsToAnn,SetFieldsToAnn] = fieldsToAnn;
    const [FinalCount, SetFinalCount] = finalcount;
    const [FinalCountReached, SetFinalCountReached] = reached;
    // const [ShowErrorSnack, SetShowErrorSnack] = errorSnack;
    // const [Reports,SetReports] = reports
    // const [Institute,SetInstitute] = institute
    const [Index,SetIndex] = index
    const [ShowMajorityGroundTruth,SetShowMajorityGroundTruth] = showmajoritygt
    const [ReportString, SetReportString] = reportString;
    const [ArrayInsertionTimes,SetArrayInsertionTimes] = insertionTimes
    //Report sections
    const [CurTime, SetCurTime] = useState(false)
    const [Translation, SetTranslation] = useState(false)
    const [OrderVar,SetOrderVar] = orderVar;
    const [ShowAnnotationsStats,SetShowAnnotationsStats] = showannotations
    const [showReportText,SetshowReportText] = showreporttext;
    const [Annotation,SetAnnotation] = annotation
    const [UserChosen,SetUserChosen] = userchosen
    const [Reports,SetReports] = reports
    const [ReportTranslation,SetReportTranslation] = useState([])
    const [ExtractFields,SetExtractFields] = useState([])
    const pubmed_fields_to_ann = ['title','abstract']
    const pubmed_fields = ['authors','journal','volume','year']
    const [SelectedLang,SetSelectedLang] = selectedLang
    const [SavedGT,SetSavedGT] = save;
    const [ReportText,SetReportText] = useState(false)
    const [ShowErrorSnack, SetShowErrorSnack] = errorSnack;
    const [Institute,SetInstitute] = institute
    //Report sections
    const [Age, SetAge] = useState('')
    const [Gender, SetGender] = useState('')
    const [Diagnosis, SetDiagnosis] = useState('')
    const [Outcomes, SetOutcomes] = useState([])
    const [Error,SetError] = useState(0)

    useEffect(()=>{
        if(Translation === false && ReportString !== false && ReportString !== ''&& ReportString !== undefined){
            SetReportText(ReportString)
        }
        if (Translation !== false){
            SetReportText(Translation)
        }

    },[ReportString,Translation])

    useEffect(()=>{
        console.log('ccc',ReportString)
    },[ReportString,Translation])






    useEffect(()=>{
        var new_arr = []
        if(ShowAnnotationsStats === true || ShowMajorityModal === true){
            axios.get('http://0.0.0.0:8000/get_post_fields_for_auto').then(response=>{
                Object.keys(response.data['extract_fields']).map(val=>{


                    response.data['extract_fields'][val].map(el=>{
                        new_arr.push(el)

                    })
                })
                SetExtractFields(new_arr)
            })

        }


    },[ShowAnnotationsStats,ShowMajorityModal])


    function setOrder(e){
        e.preventDefault()
        SetOrderVar('lexic')
    }


    function setOrder1(e){
        e.preventDefault()
        SetOrderVar('annotation')
    }

    useEffect(()=>{
        // console.log('AUTOANN',Report)
        var username_to_call = Username

        if (Annotation === 'Automatic'){
            var ns_id = 'Robot'
        }
        else{
            var ns_id = 'Human'
        }
        if(ShowAutoAnn){
            username_to_call = Username
            ns_id = 'Robot'

        }
        else if(ShowMemberGt){

            username_to_call = UserChosen

        }

        if(Report !== undefined && Action !== 'none'){
            // console.log('AUTOANN',ShowAutoAnn)
            // console.log('AUTOANN',Report)
            if((ShowAutoAnn || ShowMemberGt)){
                console.log('AXIOS')
                axios.get('http://0.0.0.0:8000/get_insertion_time_record',
                    {params:{ns_id:ns_id,username:username_to_call,rep:Reports[Index]['id_report'],language:SelectedLang,action:Action}})
                    .then(response=>{
                        if(response.data['date'] !== ''){
                            var data = response.data['date'].toString()
                            console.log('salvo!')

                            var date = data.split('T')
                            var hour = date[1].toString().split('.')
                            var temp = 'date: ' + date[0] + '  time: '+ hour[0] + '(GMT+1)'
                            SetCurTime(temp)
                        }
                        else{
                            SetCurTime('')

                        }

                    })
            }

        }
        else{
            SetCurTime(false)

        }
    },[ShowAutoAnn,ShowMemberGt,UserChosen,Report])



    useEffect(()=>{
        console.log('REPORT',ReportString)

        if(ShowAnnotationsStats === false && showReportText === false && ShowMajorityModal === false){
            if(OrderVar === 'lexic' && ReportString !== null){
                var el = document.getElementById('lexic')
                var el1 = document.getElementById('annot')
                el.style.fontWeight = 'bold';
                el1.style.fontWeight = 'normal';
            }
            else if(OrderVar === 'annotation' && ReportString !== null){
                var el1 = document.getElementById('lexic')
                var el = document.getElementById('annot')
                el.style.fontWeight = 'bold';
                el1.style.fontWeight = 'normal';
            }
        }

    },[OrderVar,ReportString])

    function ticketFunc(event){
        SetShowErrorSnack(true)
        event.preventDefault()
        axios.post('http://0.0.0.0:8000/signals_malfunctions',{
            report_id_hashed: ReportString.report_id_hashed.text,report_id: ReportString.report_id.text, target_diagnosis: ReportString.target_diagnosis.text, internalid: ReportString.internalid.text, raw_diagnoses:ReportString.raw_diagnoses.text
        }).then(function (response) {
            SetShowErrorSnack(true)
            SetError(false)
        })
            .catch(function (error) {
                SetShowErrorSnack(true)
                SetError(true)

            });
    }

    useEffect(()=>{

        if(ReportString !== undefined && ShowAnnotationsStats === false && ShowMajorityModal === false && showReportText === false){
            axios.get('http://0.0.0.0:8000/get_report_translations',{params:{id_report:Reports[Index].id_report}}).then(response=>{
                SetReportTranslation(response.data['languages'])
                // console.log('respp',response.data['languages'])
            })
        }
    },[ReportString])


    function get_trans(rep){

        if(rep !== Language){
            // SetLoadingReport(true)
            axios.get("http://0.0.0.0:8000/report_start_end", {params: {language:rep,report_id: Reports[Index].id_report.toString()}}).then(response => {
                SetTranslation(response.data['rep_string']); SetFinalCount(response.data['final_count']);SetFinalCountReached(false);SetSelectedLang(rep)
                // SetLoadingReport(false)
            })
        }
        else{

            axios.get("http://0.0.0.0:8000/report_start_end", {params: {language:Language,report_id: Reports[Index].id_report.toString()}}).then(response => {
                SetFinalCount(response.data['final_count']);SetFinalCountReached(false);SetTranslation(false);SetSelectedLang(rep)
                // SetLoadingReport(false)
            })
        }

    }

    // useEffect(()=>{
    //     console.log('report',Reports[Index])
    // },[ShowMajorityModal,showReportText,Reports,Index])

    useEffect(()=>{

        if(SelectedLang !== '' && ReportTranslation.length > 0) {

            var l = Array.from(document.getElementsByClassName('lang_span'))

            l.map(el=>{

                if(el.id === SelectedLang){

                    el.style.fontWeight = 'bold'
                }
                else{
                    el.style.fontWeight = 'normal'

                }
            })

        }
    },[SelectedLang,ReportTranslation])

    return (
        <div>
            {ReportString !== undefined && ShowAnnotationsStats === false  && ShowMajorityModal === false && showReportText === false  && <div>
                <Row>
                    <Col md={4} className="titles no-click">
                        <div>Reports' order:</div>
                    </Col>
                    <Col md={8}><div><Button size='sm' id='lexic' style={{'margin-top':'5px'}} onClick={(e)=>setOrder(e)}>Lexicographical</Button>&nbsp;&nbsp;<Button id='annot' style={{'margin-top':'5px'}} onClick={(e)=>setOrder1(e)} size='sm' >Annotated reports</Button></div></Col>
                    <Col md={4} className="titles no-click">
                        <div>last update:</div>
                    </Col>
                    {((ShowAutoAnn === true || ShowMemberGt === true || SelectedLang !== Language) && CurTime !== false) ? <Col md={8}><div>{CurTime}</div></Col> :
                        <>{ArrayInsertionTimes[Index] !== 0 ? <Col md={8}><div>{ArrayInsertionTimes[Index]}</div></Col> : <Col md={8}></Col>}</>}


                    <Col md={4} className="titles no-click">
                        {ReportType === 'reports' && <div>ID:</div>}
                        {ReportType === 'pubmed' && <div>PUBMED ID:</div>}
                    </Col>
                    <Col md={8}>
                        {ReportType === 'reports' && <div>{props.report_id.toString()}</div>}
                        {ReportType === 'pubmed' && <div>{props.report_id.split('PUBMED_')[1]}</div>}
                    </Col>

                    {ReportTranslation.length > 1 && <><Col md={4} className="titles no-click">
                        <div>Available versions:</div>
                    </Col>
                        <Col md={8}>
                            {ReportTranslation.map(rep=>
                                <>{rep !== Language &&
                                //onMouseDown={()=>get_trans(rep)} onMouseUp={()=>get_trans(Language)}
                                <OverlayTrigger
                                    key='right'
                                    placement='right'
                                    overlay={
                                        <Tooltip id={`tooltip-top'`}>
                                            Keep pressed to see the translation
                                        </Tooltip>
                                    }
                                >
                                    <button className='button_translation'
                                            onMouseDown={()=>{document.getElementsByClassName('button_pressed')[0].style.background = 'orange';get_trans(rep)}} onMouseUp={()=>{document.getElementsByClassName('button_pressed')[0].style.background = '#007bff';get_trans(Language)}}
                                            type='button' ><Badge className='button_pressed' pill variant="primary">
                                        {rep}</Badge>
                                    </button></OverlayTrigger>

                                }&nbsp;&nbsp;</>
                            )}
                        </Col></>}



                </Row>
                <hr/></div>}

            <div>
                {(LoadingReport) ? <Spinner animation="border" role="status"/> : <div>
                    {ReportText !== false  &&  <div>
                        {FieldsToAnn.length > 0 && <>
                            {FieldsToAnn.map((field,ind)=><div>
                                    {ReportText[field] !== undefined && ReportText[field] !== null  && <Row>
                                        {((props.action === 'mentions' || props.action === 'concept-mention') && (ShowAnnotationsStats === false && ShowMajorityModal === false && Translation === false)) ? <Col md={4} className="titles no-click"><div><FontAwesomeIcon style={{'width':'0.8rem'}} icon={faPencilAlt}/> {field}:</div></Col> : <Col md={4} className="titles no-click"><div>{field}:</div></Col>}
                                        {ShowAnnotationsStats === false && ShowMajorityModal === false && Translation === false && <Col md={8}><ReportSection action={props.action} stop={ReportText[field].stop} start={ReportText[field].start} text={ReportText[field].text}  report = {props.report}/></Col>}
                                        {(ShowAnnotationsStats === true || ShowMajorityModal === true || Translation !== false) && <Col md={8}><ReportSection action='noAction' stop={ReportText[field].stop} start={ReportText[field].start} text={ReportText[field].text}  report = {props.report}/></Col>}
                                    </Row>}
                                </div>
                            )}
                        </>}

                        {(ShowAnnotationsStats === true || ShowMajorityModal === true ) && ExtractFields.length > 0 && <div>
                            {ExtractFields.length > 0 && <>
                                {ExtractFields.map((field,ind)=><div>
                                        {ReportText[field] !== undefined && FieldsToAnn.indexOf(field) === -1 && Fields.indexOf(field) === -1 &&  ReportText[field] !== null  && <Row>
                                            {((props.action === 'mentions' || props.action === 'concept-mention') && (ShowAnnotationsStats === false && ShowMajorityModal === false)) ? <Col md={4} className="titles no-click"><div><FontAwesomeIcon style={{'width':'0.8rem'}} icon={faPencilAlt}/> {field}:</div></Col> : <Col md={4} className="titles no-click"><div>{field}:</div></Col>}
                                            {ShowAnnotationsStats === false && ShowMajorityModal === false && <Col md={8}><ReportSection action={props.action} stop={ReportText[field].stop} start={ReportText[field].start} text={ReportText[field].text}  report = {props.report}/></Col>}
                                            {(ShowAnnotationsStats === true || ShowMajorityModal === true ) && <Col md={8}><ReportSection action='noAction' stop={ReportText[field].stop} start={ReportText[field].start} text={ReportText[field].text}  report = {props.report}/></Col>}
                                        </Row>}
                                    </div>
                                )}
                            </>}

                        </div>}
                        {Fields.length > 0 && <>
                            {Fields.map((field,ind)=><div>
                                    {ReportText[field] !== undefined && ReportText[field] !== null  && <Row>

                                        <Col md={4} className="titles no-click"><div>{field}:</div></Col>
                                        <Col md={8}><ReportSection action='noAction' stop={ReportText[field].stop} start={ReportText[field].start} text={ReportText[field].text} report = {props.report}/></Col>

                                    </Row>}
                                </div>
                            )}
                        </>}





                    </div>}

                </div>}
                {/*{Translation !== false && <div>*/}
                {/*    {FieldsToAnn.map((field,ind)=><div>*/}
                {/*            {Translation[field] !== undefined && Translation[field] !== null  && <Row>*/}
                {/*                <Col md={8}><ReportSection action='noAction' stop={Translation[field].stop} start={Translation[field].start} text={ReportString[field].text}  report = {props.report}/></Col>*/}
                {/*            </Row>}*/}
                {/*        </div>*/}
                {/*    )}*/}
                {/*   */}
                {/*    {Fields.map((field,ind)=><div>*/}
                {/*            {Translation[field] !== undefined && Translation[field] !== null  && FieldsToAnn.indexOf(field) === -1 && <Row>*/}

                {/*                <Col md={4} className="titles no-click"><div>{field}:</div></Col>*/}
                {/*                <Col md={8}><ReportSection action='noAction' stop={ReportString[field].stop} start={ReportString[field].start} text={ReportString[field].text} report = {props.report}/></Col>*/}

                {/*            </Row>}*/}
                {/*        </div>*/}
                {/*    )}*/}

                {/*</div>}*/}


                {/*{ReportString !== undefined  &&  <div>*/}

                {/*    {FieldsToAnn.map((field,ind)=><div>*/}
                {/*            {ReportString[field] !== undefined && ReportString[field] !== null  && <Row>*/}
                {/*                {((props.action === 'mentions' || props.action === 'concept-mention') && (ShowAnnotationsStats === false && ShowMajorityModal === false)) ? <Col md={4} className="titles no-click"><div><FontAwesomeIcon style={{'width':'0.8rem'}} icon={faPencilAlt}/> {field}:</div></Col> : <Col md={4} className="titles no-click"><div>{field}:</div></Col>}*/}
                {/*                {ShowAnnotationsStats === false && ShowMajorityModal === false && <Col md={8}><ReportSection action={props.action} stop={ReportString[field].stop} start={ReportString[field].start} text={ReportString[field].text}  report = {props.report}/></Col>}*/}
                {/*                {(ShowAnnotationsStats === true || ShowMajorityModal === true) && <Col md={8}><ReportSection action='noAction' stop={ReportString[field].stop} start={ReportString[field].start} text={ReportString[field].text}  report = {props.report}/></Col>}*/}
                {/*            </Row>}*/}
                {/*        </div>*/}
                {/*    )}*/}
                {/*    {(ShowAnnotationsStats === true || ShowMajorityModal === true ) && ExtractFields.length > 0 && <div>*/}
                {/*        {ExtractFields.map((field,ind)=><div>*/}
                {/*                {ReportString[field] !== undefined && FieldsToAnn.indexOf(field) === -1 && Fields.indexOf(field) === -1 &&  ReportString[field] !== null  && <Row>*/}
                {/*                    {((props.action === 'mentions' || props.action === 'concept-mention') && (ShowAnnotationsStats === false && ShowMajorityModal === false)) ? <Col md={4} className="titles no-click"><div><FontAwesomeIcon style={{'width':'0.8rem'}} icon={faPencilAlt}/> {field}:</div></Col> : <Col md={4} className="titles no-click"><div>{field}:</div></Col>}*/}
                {/*                    {ShowAnnotationsStats === false && ShowMajorityModal === false && <Col md={8}><ReportSection action={props.action} stop={ReportString[field].stop} start={ReportString[field].start} text={ReportString[field].text}  report = {props.report}/></Col>}*/}
                {/*                    {(ShowAnnotationsStats === true || ShowMajorityModal === true) && <Col md={8}><ReportSection action='noAction' stop={ReportString[field].stop} start={ReportString[field].start} text={ReportString[field].text}  report = {props.report}/></Col>}*/}
                {/*                </Row>}*/}
                {/*            </div>*/}
                {/*        )}*/}
                {/*    </div>}*/}
                {/*    {Fields.map((field,ind)=><div>*/}
                {/*            {ReportString[field] !== undefined && ReportString[field] !== null  && FieldsToAnn.indexOf(field) === -1 && <Row>*/}

                {/*                <Col md={4} className="titles no-click"><div>{field}:</div></Col>*/}
                {/*                <Col md={8}><ReportSection action='noAction' stop={ReportString[field].stop} start={ReportString[field].start} text={ReportString[field].text} report = {props.report}/></Col>*/}

                {/*            </Row>}*/}
                {/*        </div>*/}
                {/*    )}*/}




                {/*</div>}*/}
            </div>
            {/*}*/}
        </div>

    );

}


export default ReportListUpdated