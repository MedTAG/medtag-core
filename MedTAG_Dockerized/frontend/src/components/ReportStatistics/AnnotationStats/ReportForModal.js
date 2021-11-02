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
import Collapse from "@material-ui/core/Collapse";
import MentionList from "../../Mentions/MentionList";
import Mention from "../../Mentions/Mention";
import './reportsmodal.css'
import Badge from "react-bootstrap/Badge";
import {Divider} from "@material-ui/core";
// axios.defaults.xsrfCookieName = "csrftoken";
// axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";
function ReportForModal(props) {

    const { index,institute,loadingMentions,color,tokens,fields,mentionsList,loadingColors,showannotations,finalcount,fieldsToAnn,reached,orderVar, errorSnack,reports, reportString, insertionTimes } = useContext(AppContext);
    const [Reports,SetReports] = useState([])
    const [ReportString, setReportsString] = reportString;
    //Report sections
    const [Children,SetChildren] = tokens;
    const [selectedStats,SetSelectedStata] = useState('none')
    const [ShowLabelsStats,SetShowLabelsStats] = useState(false)
    const [ShowMentionsStats,SetShowMentionsStats] = useState(false)
    const [ShowConceptsStats,SetShowConceptsStats] = useState(false)
    const [ShowLinkingStats,SetShowLinkingStats] = useState(false)
    const [newInd,SetNewInd] = useState(false)
    const [FinalCountReached, SetFinalCountReached] = reached;
    const [FinalCount, SetFinalCount] = finalcount;
    const [Fields, SetFields] = fields;
    const [FieldsToAnn, SetFieldsToAnn] = fieldsToAnn;
    const [ShowAnnotationsStats,SetShowAnnotationsStats] = showannotations;
    const [mentions_to_show, SetMentions_to_show] = useState([]);
    const [LoadingMentions, SetLoadingMentions] = loadingMentions;
    const [LoadingMentionsColor, SetLoadingMentionsColor] = loadingColors;
    const [Color, SetColor] = color
    const [EXAPresenceLabels,SetEXAPresenceLabels] = useState(false)
    const [EXAPresenceConcepts,SetEXAPresenceConcepts] = useState(false)

    useEffect(()=>{
        if(props.stats !== false){
            var mentions = []
            var json_val = {}
            props.stats['Robot']['mentions']['mentions_list'].map((val,ind)=>{
                json_val['start'] = val.start
                json_val['stop'] = val.stop
                json_val['mention_text'] = val.mention
                if(mentions.indexOf(json_val) < 0){
                    mentions.push(json_val)

                }
            })
            SetMentions_to_show(mentions)
            SetLoadingMentions(false)
        }
    },[props.stats])

    useEffect(()=>{
        setReportsString('')
        SetMentions_to_show([])
        axios.get("http://0.0.0.0:8000/get_reports", {params: {all: 'all'}}).then(response => {
            SetReports(response.data['report']);})

        axios.get("http://0.0.0.0:8000/check_presence_exa_conc_lab", {params: {id_report:props.id_report,language:props.language}})
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
        console.log('REPORT',ReportString)
    },[ReportString])

    useEffect(()=>{
        if(Reports.length > 0){
            console.log(Reports[newInd].id_report)
            console.log(newInd)
            if(newInd >= 0){
                axios.get("http://0.0.0.0:8000/report_start_end", {params: {report_id: Reports[newInd].id_report.toString()}}).then(response => {SetFinalCount(response.data['final_count']);
                    setReportsString(response.data['rep_string']); SetFinalCountReached(false);
                })
                axios.get("http://0.0.0.0:8000/get_fields",{params:{report:props.id_report}}).then(response => {SetFields(response.data['fields']);SetFieldsToAnn(response.data['fields_to_ann']);})

            }
        }


    },[newInd])



    useEffect(()=>{
        if(Reports.length > 0){

            if(props.id_report !== false){
                Reports.map((report,ind)=>{
                    if(report.id_report === props.id_report){

                        SetNewInd(ind)
                    }

                })
            }
        }



    },[props.id_report,Reports])



    useEffect(()=>{
        if(Reports.length>0){
            if(newInd===0){
                console.log('zero',Reports[newInd].id_report)
            }

        }
    },[newInd])




    return (
          <div className='container-fluid'>

            {(newInd !== false  && ReportString !== '' && (FieldsToAnn.length > 0 || Fields.length > 0) && props.stats !== false && ShowAnnotationsStats && Reports.length > 0) ? <Row>

                <Col md={6} style={{fontSize:'1rem'}}>
                    <div className='report_modal'>
                        <ReportListUpdated report_id = {Reports[newInd].id_report} report = {Reports[newInd].report_json} action={selectedStats}/>

                    </div>
                </Col>
                <Col  md={6}>
                    <div className='modalContainer'>
                        <div><h5 style={{display:'inline-block'}}>Labels  </h5><IconButton onClick={()=>{SetShowLabelsStats(prev=>!prev);SetSelectedStata('labels')}}><ExpandMoreIcon style={{marginLeft:'2px'}} /></IconButton></div>
                        <Collapse style={{marginTop:'0px'}} in={ShowLabelsStats}>
                        {EXAPresenceLabels === false ? <div>
                            <i>Below you can find the list of labels; next to each label you can see how many users chose that label for this report out of the total of users who annotated the labels for this report.</i>
                            <br/>
                            {props.stats['Human']['labels']['count'] > 0 &&
                            <div>

                                <h6 style={{textDecoration:'underline'}}>Your labels</h6>
                                <div>Users who annotated the labels for this report: <b>{props.stats['Human']['labels']['count']}  {props.stats['Human']['labels']['count'] > 0 && <i>({props.stats['Human']['labels']['users_list'].join(', ')})</i>}</b></div>

                                <ul>{props.stats['Human']['labels']['labels_list'].map((val,ind)=>

                                    <>{val.count > 0 &&
                                    <li className='annotations_li'>
                                        <div><i>{val.label}</i>
                                        </div>
                                        <div style={{'font-size':'0.9rem'}}><b>{val.count} </b>{val.count === 1 ? <>user</> : <>users</>} annotated this label : <i>{val.users_list.join(', ')}</i></div>
                                        </li>}</>

                                    // <Row>
                                    //     <Col md={9}>{val.label} </Col>
                                    //     <Col md={3}><b>{val.count} {val.count === 1 ? <>user</> : <>users</>}</b></Col>
                                    // </Row>}</>

                                )}</ul>



                            </div>}
                            {props.stats['Robot']['labels']['count'] > 0 && <div>
                                <hr/>
                                <h6 style={{textDecoration:'underline'}}>EXAMODE labels</h6>
                                <i style={{fontSize:'0.8rem'}}>The labels annotated by the algorithm are highlighted in  <span style={{color:'royalblue'}}>blue</span></i><br/>
                                <div>Users who corrected the automatically detected labels: <b>{props.stats['Robot']['labels']['count']-1} {props.stats['Robot']['labels']['count']-1 > 0 && <i>({props.stats['Robot']['labels']['users_list'].filter(name=>name!=='Robot_user').join(', ')})</i>}</b></div>
                               <ul> {props.stats['Robot']['labels']['labels_list'].map((val,ind)=>
                                    <li className='annotations_li'>
                                        <div style={{color:(val.users_list).indexOf('Robot_user') !== -1 ? 'royalblue':'black'}}>{val.label} </div>

                                        {/*{(val.users_list).indexOf('Robot_user') !== -1 && <div style={{color:'royalblue'}}>{val.label} </div>}*/}
                                        {/*{(val.users_list).indexOf('Robot_user') === -1 && val.count > 0 &&<div>{val.label} </div>}*/}

                                        {(val.users_list).indexOf('Robot_user') !== -1 ? <>
                                            {val.count === 0 ? <div style={{'font-size':'0.9rem'}}><i>Only the algorithm annotated this label</i></div> :  <div style={{'font-size':'0.9rem'}}><b>{val.count} </b>{val.count === 1 ? <>user</> : <>users</>} annotated this label : <i>{val.users_list.filter(user=>user!=='Robot_user').join(', ')}</i></div>
                                            }
                                        </> :
                                        <>{val.count > 0 &&  <div style={{'font-size':'0.9rem'}}><b>{val.count} </b>{val.count === 1 ? <>user</> : <>users</>} annotated this label : <i><b>{val.users_list.join(', ')}</b></i></div>
                                        }
                                        </>
                                        }
                                        {/*{(val.users_list).indexOf('Robot_user') !== -1 ? <Col md={7} style={{color:'royalblue'}}>{val.label} </Col>:<Col md={7} >{val.label} </Col>}*/}
                                        {/*{(val.users_list).indexOf('Robot_user') !== -1 && val.count === 0 ? <Col md={5} style={{'font-size':'0.8rem'}}><i>Only the algorithm annotated this label</i></Col> :<Col md={5}><b>{val.count} / {props.stats['Robot']['labels']['count']-1} users ({val.count === 0 ? <>0%</> : <>{val.count * 100 / (props.stats['Robot']['labels']['count']-1)}%</>})</b></Col>}*/}

                                    </li>

                               )}</ul>
                                <div>
                                </div>
                            </div>}
                        </div> :
                            <div>
                                <i>Below you can find the list of EXAMODE labels. Below each label you can see how many users chose that label in <b>manual</b> and <b>automatic</b> annotation respectively.</i>
                                <br/><i style={{fontSize:'0.8rem'}}>The labels annotated by the algorithm are highlighted in  <span style={{color:'royalblue'}}>blue</span></i><br/>
                                <br/>
                                {props.stats['Human_Robot']['labels']['count'] > 0 &&
                                <div>

                                    <div>Users who annotated the labels for this report: <b>{props.stats['Human_Robot']['labels']['count']-1}  {props.stats['Human_Robot']['labels']['count']-1 > 0 && <i>({props.stats['Human_Robot']['labels']['users_list'].filter(name=>name!=='Robot_user').join(', ')})</i>}</b></div>

                                    <ul>{props.stats['Human_Robot']['labels']['labels_list'].map((val,ind)=>


                                        <li className='annotations_li'>
                                            <div style={{color:(val.users_list).indexOf('Robot_user') !== -1 ? 'royalblue':'black'}}>{val.label} </div>
                                            {/*{(val.users_list).indexOf('Robot_user') !== -1 && <div style={{color:'royalblue'}}>{val.label} </div>}*/}
                                            {/*{(val.users_list).indexOf('Robot_user') === -1 && val.count > 0 &&<div>{val.label} </div>}*/}

                                                {(val.users_list).indexOf('Robot_user') !== -1 && val.count -1 === 0 && <div style={{'font-size':'0.9rem'}}><i>Only the algorithm annotated this label</i></div>
                                                }

                                                <>{val.count > 0 &&  <div style={{'font-size':'0.9rem'}}>
                                                    <ul>
                                                        {val.human_users.length > 0 && <li className='annotations_li'>
                                                            <b>{val.human_users.length}</b> manual annotators: <b><i>{val.human_users.join(', ')}</i></b>
                                                        </li>}
                                                         {val.robot_users.indexOf('Robot_user') !== -1 && val.robot_users.length - 1> 0 &&  <li className='annotations_li'>
                                                            <b>{val.robot_users.length-1}</b> automatic annotators: <b><i>{val.robot_users.filter(name=>name!=='Robot_user').join(', ')}</i></b>
                                                        </li>}
                                                        {val.robot_users.indexOf('Robot_user') === -1 && val.robot_users.length > 0 && <li className='annotations_li'>
                                                            <b>{val.robot_users.length}</b> automatic annotators: <b><i>{val.robot_users.filter(name=>name!=='Robot_user').join(', ')}</i></b>
                                                        </li>}
                                                    </ul>
                                                </div>
                                                }
                                                </>

                                        </li>

                                    )}</ul>
                                    <div>
                                    </div>
                                </div>}
                            </div>}
                        </Collapse><hr/>
                        <div><h5 style={{display:'inline-block'}}>Mentions  </h5><IconButton onClick={()=>{SetShowMentionsStats(prev=>!prev);SetSelectedStata('mentions')}}><ExpandMoreIcon style={{marginLeft:'2px'}} /></IconButton></div>
                        <Collapse style={{marginTop:'0px'}} in={ShowMentionsStats}>

                        {EXAPresenceConcepts === false ?<div>
                            <i>Below you can find the list of mentions associated to this report; next to each mention you can see how many users selected that mention for this report out of the total of users who annotated the mentions for this report.</i>
                            <br/><br/>
                            {props.stats['Human']['mentions']['count'] > 0 && <><h6 style={{textDecoration:'underline'}}>Mentions from manual annotation</h6>
                            <div>Users who annotated the mentions for this report: <b>{props.stats['Human']['mentions']['count']}  {props.stats['Human']['mentions']['count']> 0 && <i>({props.stats['Human']['mentions']['users_list'].join(', ')})</i>}</b></div>
                            <ul>{props.stats['Human']['mentions']['mentions_list'].map((mention,index)=>
                                <>{mention.count > 0 && <li className='annotations_li'>
                                    <div><Mention id = {index} index = {index} text={mention['mention']} start={mention['start']}
                                                         stop={mention['stop']} mention_obj = {mention}/><br/></div>
                                    <div style={{'font-size':'0.9rem'}}><b>{mention.count} </b>{mention.count === 1 ? <>user</> : <>users</>} annotated this label : <i>{mention.users_list.join(', ')}</i></div>
                                    </li>}</>)}</ul></>}
                            <hr/>
                            <div>
                                {props.stats['Robot']['mentions']['count'] > 0 && <><h6 style={{textDecoration:'underline'}}>Mentions from automatic annotation</h6>
                                    <i style={{fontSize:'0.8rem'}}>The mentions found by the algorithm are highlighted in  <span style={{color:'royalblue'}}>blue</span></i><br/>
                                    <div>Users who corrected the automatically annotated mentions for this report: <b>{props.stats['Robot']['mentions']['count']-1} {props.stats['Robot']['mentions']['count']-1 > 0 && <i>({props.stats['Robot']['mentions']['users_list'].filter(name=>name!=='Robot_user').join(', ')})</i>}</b></div>


                                <ul>{props.stats['Robot']['mentions']['mentions_list'].map((mention,index)=>
                                    <li className='annotations_li'>
                                        {((mention.users_list).indexOf('Robot_user') !== -1 || mention.count > 0) && <div style={{color:(mention.users_list).indexOf('Robot_user') !== -1 ? 'royalblue':'black'}} ><Mention id = {index} index = {index} text={mention['mention']} start={mention['start']} stop={mention['stop']} mention_obj = {mention}/><br/></div>}

                                        {(mention.users_list).indexOf('Robot_user') !== -1 ? <>
                                                {mention.count === 0 ?
                                                    <div style={{'font-size': '0.9rem'}}><i>Only the algorithm annotated
                                                        this mention</i></div> : <div style={{'font-size': '0.9rem'}}>
                                                        <b>{mention.count} </b>{mention.count === 1 ? <>user</> : <>users</>} annotated
                                                        this mention
                                                        : <i>{mention.users_list.filter(user => user !== 'Robot_user').join(', ')}</i>
                                                    </div>
                                                }
                                            </> :
                                            <>{mention.count > 0 && <div style={{'font-size': '0.9rem'}}>
                                                <b>{mention.count} </b>{mention.count === 1 ? <>user</> : <>users</>} annotated
                                                this mention : <i><b>{mention.users_list.join(', ')}</b></i></div>
                                            }
                                            </>
                                        }
                                        {/*<Col style={(mention.users_list).indexOf('Robot_user') !== -1 && {color:'royalblue'}} md={7}><Mention id = {index} index = {index} text={mention['mention']} start={mention['start']}*/}
                                        {/*                                                                                      stop={mention['stop']} mention_obj = {mention}/></Col>*/}
                                        {/*{(mention.users_list).indexOf('Robot_user') !== -1 && mention.count === 0 ? <Col style={{'font-size':'0.8rem'}} md={5}><i>Only the algorithm annotated this mention</i></Col> :<Col md={5}><b>{mention.count} / {props.stats['Robot']['mentions']['count']-1} users ({mention.count === 0 ? <>0%</> : <>{mention.count * 100 / (props.stats['Robot']['mentions']['count']-1)}%</>})</b></Col>}*/}

                                        </li>)}</ul></>}
                            </div>
                        </div> :
                            <div>
                            <i>Below you can find the list of mentions. Below each mention you can see how many users chose that in <b>manual</b> and <b>automatic</b> annotation respectively.</i>
                            <br/><i style={{fontSize:'0.8rem'}}>The mentions annotated by the algorithm are highlighted in  <span style={{color:'royalblue'}}>blue</span></i><br/>
                            <br/>
                            {props.stats['Human_Robot']['mentions']['count'] > 0 &&
                            <div>

                                <div>Users who annotated the mentions for this report: <b>{props.stats['Human_Robot']['mentions']['count']-1}  {props.stats['Human_Robot']['mentions']['count'] -1 > 0 && <i>({props.stats['Human_Robot']['mentions']['users_list'].filter(name=>name!=='Robot_user').join(', ')})</i>}</b></div>

                                <ul>{props.stats['Human_Robot']['mentions']['mentions_list'].map((val,ind)=>


                                    <li className='annotations_li'>
                                        <div style={{color: (val.users_list).indexOf('Robot_user') !== -1 ? 'royalblue':'black'}} ><Mention id = {index} index = {index} text={val['mention']} start={val['start']} stop={val['stop']} mention_obj = {val}/><br/></div>

                                        {(val.users_list).indexOf('Robot_user') !== -1 && val.count - 1 === 0 && <div style={{'font-size':'0.9rem'}}><i>Only the algorithm annotated this mention</i></div>
                                        }

                                        <>{val.count > 0 &&  <div style={{'font-size':'0.9rem'}}>
                                            <ul>
                                                {val.human_users.length > 0 && <li className='annotations_li'>
                                                    <b>{val.human_users.length}</b> manual annotators: <b><i>{val.human_users.join(', ')}</i></b>
                                                </li>}
                                                {val.robot_users.indexOf('Robot_user') !== -1 && val.robot_users.length - 1> 0 && <li className='annotations_li'>
                                                    <b>{val.robot_users.length-1}</b> automatic annotators: <b><i>{val.robot_users.filter(name=>name!=='Robot_user').join(', ')}</i></b>
                                                </li>}
                                                {val.robot_users.indexOf('Robot_user') === -1 && val.robot_users.length > 0 && <li className='annotations_li'>
                                                    <b>{val.robot_users.length}</b> automatic annotators: <b><i>{val.robot_users.filter(name=>name!=='Robot_user').join(', ')}</i></b>
                                                </li>}
                                            </ul>
                                        </div>
                                        }
                                        </>

                                    </li>

                                )}</ul>
                                <div>
                                </div>
                            </div>}
                        </div>}
                        </Collapse><hr/>


                        <div><h5 style={{display:'inline-block'}}>Concepts  </h5><IconButton onClick={()=>{SetShowConceptsStats(prev=>!prev);SetSelectedStata('concepts')}}><ExpandMoreIcon style={{marginLeft:'2px'}} /></IconButton></div>
                        <Collapse style={{marginTop:'0px'}} in={ShowConceptsStats}>
                        {EXAPresenceConcepts === false ? <div>
                            <i>Below you can find the list of concepts found for the report; next to each concept you can see how many users chose that concept for this report out of the total of users who annotated the concepts for this report.</i>
                            <br/><br/>
                            {props.stats['Human']['concepts']['count'] > 0 && <div>

                                <h6 style={{textDecoration:'underline'}}>Concepts from manual annotation</h6>
                                <div>Users who annotated the concepts for this report: <b>{props.stats['Human']['concepts']['count']} {props.stats['Human']['concepts']['count'] > 0 && <i>({props.stats['Human']['concepts']['users_list'].join(', ')})</i>}</b></div>
                                <ul>{props.stats['Human']['concepts']['concepts_list'].map((val,ind)=>
                                    <>{val.count > 0 && <li className='annotations_li'>
                                        <div>
                                        {val.concept_name} - <span style={{color:'black',fontSize:'0.9rem'}}><i><b>URL</b> {val.concept_url}</i></span>
                                        </div>
                                        <div style={{'font-size':'0.9rem'}}><b>{val.count} </b>{val.count === 1 ? <>user</> : <>users</>} annotated this concept : <i>{val.users_list.join(', ')}</i></div>
                                    </li>}</>)}</ul>

                            </div>}
                            {props.stats['Robot']['concepts']['count'] > 0 &&
                            <div><hr/>
                                <h6 style={{textDecoration:'underline'}}>Concepts from automatic annotation</h6>
                                <i style={{fontSize:'0.8rem'}}>The concepts found by the algorithm are highlighted in  <span style={{color:'royalblue'}}>blue</span></i>

                                <div>Users who corrected the automatically annotated concepts for this report: <b>{props.stats['Robot']['concepts']['count']-1} {props.stats['Robot']['concepts']['count']-1 > 0 && <i>({props.stats['Robot']['concepts']['users_list'].filter(name=>name!=='Robot_user').join(', ')})</i>}</b></div>
                                <ul>{props.stats['Robot']['concepts']['concepts_list'].map((val,ind)=>
                                    <li className='annotations_li'>
                                        {((val.users_list).indexOf('Robot_user') !== -1 || val.count > 0) && <div style={{color: (val.users_list).indexOf('Robot_user') !== -1 ? 'royalblue':'black'}}>
                                            {val.concept_name} - <span style={{color:'black',fontSize:'0.9rem'}}><i><b>URL</b> {val.concept_url}</i></span>
                                        </div>}
                                        {(val.users_list).indexOf('Robot_user') !== -1 ? <>
                                                {val.count === 0 ? <div style={{'font-size':'0.9rem'}}><i>Only the algorithm annotated this concept</i></div> :  <div style={{'font-size':'0.9rem'}}><b>{val.count} </b>{val.count === 1 ? <>user</> : <>users</>} annotated this label : <i>{val.users_list.filter(user=>user!=='Robot_user').join(', ')}</i><br/></div>
                                                }
                                            </> :
                                            <>{val.count > 0 &&  <div style={{'font-size':'0.9rem'}}><b>{val.count} </b>{val.count === 1 ? <>user</> : <>users</>} annotated this concept : <i><b>{val.users_list.join(', ')}</b></i><br/></div>
                                            }
                                            </>
                                        }

                                    </li>)}</ul>

                            </div>}
                        </div> :
                            <div>
                                <i>Below you can find the list of concepts. Below each concept you can see how many users chose that in <b>manual</b> and <b>automatic</b> annotation respectively.</i>
                                <br/><i style={{fontSize:'0.8rem'}}>The concepts annotated by the algorithm are highlighted in  <span style={{color:'royalblue'}}>blue</span></i><br/>
                                <br/>
                                {props.stats['Human_Robot']['concepts']['count'] > 0 &&
                                <div>

                                    <div>Users who annotated the concepts for this report: <b>{props.stats['Human_Robot']['concepts']['count'] - 1 }  {props.stats['Human_Robot']['concepts']['count'] -1 > 0 && <i>({props.stats['Human_Robot']['concepts']['users_list'].filter(name=>name!=='Robot_user').join(', ')})</i>}</b></div>

                                    <ul>{props.stats['Human_Robot']['concepts']['concepts_list'].map((val,ind)=>


                                        <li className='annotations_li'>
                                            <div style={{color: (val.users_list).indexOf('Robot_user') !== -1 ? 'royalblue':'black'}}>
                                                {val.concept_name} - <span style={{color:'black',fontSize:'0.9rem'}}><i><b>URL</b> {val.concept_url}</i></span>
                                            </div>
                                            {(val.users_list).indexOf('Robot_user') !== -1 && val.count - 1 === 0 && <div style={{'font-size':'0.9rem'}}><i>Only the algorithm annotated this concept</i></div>
                                            }

                                            <>{val.count > 0 &&  <div style={{'font-size':'0.9rem'}}>
                                                <ul>
                                                    {val.human_users.length > 0 && <li className='annotations_li'>
                                                        <b>{val.human_users.length}</b> manual annotators: <b><i>{val.human_users.join(', ')}</i></b>
                                                    </li>}
                                                    {val.robot_users.indexOf('Robot_user') !== -1 && val.robot_users.length - 1> 0 && <li className='annotations_li'>
                                                        <b>{val.robot_users.length-1}</b> automatic annotators: <b><i>{val.robot_users.filter(name=>name!=='Robot_user').join(', ')}</i></b>
                                                    </li>}
                                                    {val.robot_users.indexOf('Robot_user') === -1 && val.robot_users.length > 0 && <li className='annotations_li'>
                                                        <b>{val.robot_users.length}</b> automatic annotators: <b><i>{val.robot_users.filter(name=>name!=='Robot_user').join(', ')}</i></b>
                                                    </li>}
                                                </ul>
                                            </div>
                                            }
                                            </>

                                        </li>

                                    )}</ul>

                                </div>}
                            </div>}
                        </Collapse><hr/>
                        <div><h5 style={{display:'inline-block'}}>Linking  </h5><IconButton onClick={()=>{SetShowLinkingStats(prev=>!prev);SetSelectedStata('concept-mention')}}><ExpandMoreIcon style={{marginLeft:'2px'}} /></IconButton></div>
                        <Collapse style={{marginTop:'0px'}} in={ShowLinkingStats}>
                            {EXAPresenceConcepts === false ? <div>
                            <i>Below you can find the list of associations mention-concept found for this report; next to each association mention-concept you can see how many users chose that association for this report out of the total of users who annotated the associations for this report.</i>
                            <br/><br/>
                            {props.stats['Human']['linking']['count'] > 0 && <div>

                                <h6 style={{textDecoration:'underline'}}>Associations from manual annotation</h6>
                                <div>Users performed linking for this report: <b>{props.stats['Human']['linking']['count']} {props.stats['Human']['linking']['count'] > 0 && <i>({props.stats['Human']['linking']['users_list'].join(', ')})</i>}</b> </div>
                                <ul>{props.stats['Human']['linking']['linking_list'].map((val,ind)=>
                                    <>{val.count > 0 && <li className='annotations_li'>
                                        <div><div><Mention id = {index} index = {index} text={val['mention']} start={val['start']}
                                                                  stop={val['stop']} mention_obj = {val}/></div>
                                            <br/><div>
                                                <Badge pill variant="dark" >
                                                    {val.concept_name}
                                                </Badge> - <span style={{color:'black',fontSize:'0.9rem'}}><i><b>URL</b> {val.concept_url}</i></span>
                                            </div>
                                        </div>
                                        <div style={{'font-size':'0.9rem'}}><b>{val.count} </b>{val.count === 1 ? <>user</> : <>users</>} annotated this association : <i>{val.users_list.join(', ')}</i></div><br/>
                                    </li>}</>)}

                            </ul></div>}
                            {props.stats['Robot']['linking']['count'] > 0 &&
                            <div><hr/>
                                <h6 style={{textDecoration:'underline'}}>Associations from automatic annotation</h6>
                                <i style={{fontSize:'0.8rem'}}>The associations found by the algorithm are highlighted in  <span style={{color:'royalblue'}}>blue</span></i><br/>
                                <div>Users who corrected the automatically linked concepts for this report: <b>{props.stats['Robot']['linking']['count']-1} {props.stats['Robot']['linking']['count']-1>0 && <i>({props.stats['Robot']['linking']['users_list'].filter(name=>name!== 'Robot_user').join(', ')})</i>}</b></div>
                                <ul>{props.stats['Robot']['linking']['linking_list'].map((val,ind)=>
                                    <li className='annotations_li'>
                                        <div style={{color: (val.users_list).indexOf('Robot_user') !== -1 ?'royalblue':'black'}}><div><Mention id = {index} index = {index} text={val['mention']} start={val['start']}
                                                                                                                               stop={val['stop']} mention_obj = {val}/></div>
                                            <div>
                                                <br/><Badge pill variant="dark" >
                                                {val.concept_name}
                                            </Badge> - <span style={{color:'black',fontSize:'0.9rem'}}><i><b>URL</b> {val.concept_url}</i></span>
                                            </div>
                                        </div>
                                        {(val.users_list).indexOf('Robot_user') !== -1 ? <>
                                                {val.count === 0 ? <div style={{'font-size':'0.9rem'}}><i>Only the algorithm annotated this association</i></div> :  <div style={{'font-size':'0.9rem'}}><b>{val.count} </b>{val.count === 1 ? <>user</> : <>users</>} annotated this label : <i>{val.users_list.filter(user=>user!=='Robot_user').join(', ')}</i><br/></div>
                                                }
                                            </> :
                                            <>{val.count > 0 &&  <div style={{'font-size':'0.9rem'}}><b>{val.count} </b>{val.count === 1 ? <>user</> : <>users</>} annotated this label : <i><b>{val.users_list.join(', ')}</b></i><br/></div>
                                            }
                                            </>
                                        }

                                    </li>)}
                                </ul>
                            </div>}
                        </div> :
                                <div>
                                    <i>Below you can find the list of concepts. Below each association you can see how many users chose that in <b>manual</b> and <b>automatic</b> annotation respectively.</i>
                                    <br/><i style={{fontSize:'0.8rem'}}>The concepts annotated by the algorithm are highlighted in  <span style={{color:'royalblue'}}>blue</span></i><br/>
                                    <br/>
                                    {props.stats['Human_Robot']['linking']['count'] > 0 &&
                                    <div>

                                        <div>Users who annotated the associations for this report: <b>{props.stats['Human_Robot']['linking']['count'] - 1 }  {props.stats['Human_Robot']['linking']['count'] - 1 > 0 && <i>({props.stats['Human_Robot']['linking']['users_list'].filter(name=>name!=='Robot_user').join(', ')})</i>}</b></div>

                                        <ul>{props.stats['Human_Robot']['linking']['linking_list'].map((val,ind)=>


                                            <li className='annotations_li'>
                                                <div style={{color: (val.users_list).indexOf('Robot_user') !== -1 ?'royalblue':'black'}}><div><Mention id = {index} index = {index} text={val['mention']} start={val['start']}
                                                                                                                                                       stop={val['stop']} mention_obj = {val}/></div>
                                                    <div>
                                                        <br/><Badge pill variant="dark" >
                                                        {val.concept_name}
                                                    </Badge> - <span style={{color:'black',fontSize:'0.9rem'}}><i><b>URL</b> {val.concept_url}</i></span>
                                                    </div>
                                                </div>
                                                {(val.users_list).indexOf('Robot_user') !== -1 && val.count - 1 === 0 && <div style={{'font-size':'0.9rem'}}><i>Only the algorithm annotated this concept</i></div>
                                                }

                                                <>{val.count > 0 &&  <div style={{'font-size':'0.9rem'}}>
                                                    <ul>
                                                        {val.human_users.length > 0 && <li className='annotations_li'>
                                                            <b>{val.human_users.length}</b> manual annotators: <b><i>{val.human_users.join(', ')}</i></b>
                                                        </li>}
                                                        {val.robot_users.indexOf('Robot_user') !== -1 && val.robot_users.length - 1> 0 && <li className='annotations_li'>
                                                            <b>{val.robot_users.length-1}</b> automatic annotators: <b><i>{val.robot_users.filter(name=>name!=='Robot_user').join(', ')}</i></b>
                                                        </li>}
                                                        {val.robot_users.indexOf('Robot_user') === -1 && val.robot_users.length > 0 && <li className='annotations_li'>
                                                            <b>{val.robot_users.length}</b> automatic annotators: <b><i>{val.robot_users.filter(name=>name!=='Robot_user').join(', ')}</i></b>
                                                        </li>}
                                                    </ul>
                                                </div>
                                                }
                                                </>

                                            </li>

                                        )}</ul>

                                    </div>}
                                </div>}
                        </Collapse>
                    </div>


                </Col>
            </Row> : <div className='spinnerDiv'><Spinner animation="border" role="status"/></div>}


        </div>
    );
}


export default ReportForModal