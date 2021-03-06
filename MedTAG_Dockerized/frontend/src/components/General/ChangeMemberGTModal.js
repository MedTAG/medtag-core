import React, {Component, useContext, useEffect, useRef, useState} from 'react'
import axios from "axios";
import Button from "react-bootstrap/Button";
import ButtonGroup from "react-bootstrap/ButtonGroup";
import 'bootstrap/dist/css/bootstrap.min.css';
import {Container, Row, Col, OverlayTrigger} from "react-bootstrap";
import './buttons.css';
import './first_row.css';
import FormatAlignLeftIcon from '@material-ui/icons/FormatAlignLeft';
import FormatAlignCenterIcon from '@material-ui/icons/FormatAlignCenter';
import FormatAlignRightIcon from '@material-ui/icons/FormatAlignRight';
import FormatAlignJustifyIcon from '@material-ui/icons/FormatAlignJustify';
import ToggleButton from '@material-ui/lab/ToggleButton';
import ToggleButtonGroup from '@material-ui/lab/ToggleButtonGroup';

import {AppContext} from "../../App";
import {faFileAlt,faRobot,faUser,faUserFriends,faUserEdit} from "@fortawesome/free-solid-svg-icons";
import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";
import Tooltip from "react-bootstrap/Tooltip";


function ChangeMemberGTModal(props){
    const { fieldsToAnn,makereq,userchosen,selectedLang,selectedLanguage,selectedInstitute,selectedUse,selectedbatch,usersListAnnotations,loadingChangeGT,batchNumber,report_type,institute,language,finalcount,username,showmember,showmajority,reached,showautoannotation,reportString,fields,annotation,report,usecase,concepts,semanticArea, disButton,labelsToInsert, selectedconcepts,linkingConcepts, radio, checks,save, userLabels, labelsList, mentionsList, action, reports, index, mentionSingleWord, allMentions, tokens, associations } = useContext(AppContext);

    const [ClickBottomMenu,SetClickBottomMenu] = useState(false)

    const [ShowAutoAnn,SetShowAutoAnn] = showautoannotation;
    const [ShowMemberGt,SetShowMemberGt] =showmember
    const [ShowMajorityGt,SetShowMajorityGt] = showmajority
    const [labels_to_show, setLabels_to_show] = userLabels;

    const [Children,SetChildren] = tokens;

    const [Action, SetAction] = action;

    const [ChangeButton,SetChangeButton] = useState(false)
    const [Username,SetUsername] = username

    const [userGT,SetUserGT] = useState(true)
    // const [UsersList,SetUsersList] = useState([])
    const [RobotPresence,SetRobotPresence] = useState(false)
    const but1 = useRef(null)
    const but2 = useRef()



    const [SelectedLang,SetSelectedLang] = selectedLanguage
    const [SelectedInstitute,SetSelectedInstitute] = selectedInstitute
    const [SelectedUse,SetSelectedUse] = selectedUse
    const [SelectedBatch,SetSelectedBatch] = selectedbatch



    useEffect(()=>{
        // SetMakeReq(true)
        but1.current.className = 'btn btn-outline-primary btn-sm'
        but2.current.className = 'btn btn-outline-primary btn-sm'


    },[])

    useEffect(()=>{
        // SetMakeReq(true)
        but1.current.className = 'btn btn-outline-primary btn-sm'
        but2.current.className = 'btn btn-outline-primary btn-sm'


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
    },[])


    useEffect(()=>{
        // but1.current.focus()
        but1.current.className = 'btn btn-primary btn-sm'
        but2.current.className = 'btn btn-outline-primary btn-sm'

        SetShowMajorityGt(false)
        SetShowAutoAnn(false)
        SetShowMemberGt(false)
        SetClickBottomMenu(false)
        SetChangeButton(false)
    },[props.ind,Action])


    function UserGT() {
        // SetMakeReq(true)
        but1.current.className = 'btn btn-primary btn-sm'
        but2.current.className = 'btn btn-outline-primary btn-sm'
        // if(ShowAutoAnn === true || ShowMemberGt === true){
        //     SetLoadingChangeGT(true)
        //
        // }
        Children.map(child=>{
            child.setAttribute('fontWeight','normal')
        })


        Children.map(child=>{
            child.style.fontWeight = 'normal'
        })
        SetShowAutoAnn(false)
        SetUserGT(true)
        SetShowMemberGt(false)
        SetChangeButton(false)
        SetClickBottomMenu(true)
    }

    function RobotGT(){
        // SetMakeReq(true)
        but1.current.className = 'btn btn-outline-primary btn-sm'
        but2.current.className = 'btn btn-primary btn-sm'
        // if(ShowMemberGt === false && ShowAutoAnn === false){
        //     submit(Action)
        //
        // }
        Children.map(child=>{
            child.setAttribute('fontWeight','normal')
        })

        SetClickBottomMenu(true)
        Children.map(child=>{
            child.style.fontWeight = 'normal'
        })
        SetShowMemberGt(false)
        // SetClickBottomMenu(true)

        SetShowAutoAnn(true)
        SetChangeButton(false)
        SetUserGT(false)

    }






    useEffect(()=>{
        // console.log('userchosen',MakeReq)
        var username_to_call = Username
        console.log('clickbut',ClickBottomMenu)
        //
        // setLabels_to_show([])

        if(ShowAutoAnn){
            username_to_call = Username
            var ns_id = 'Robot'
        }
        else{
            var ns_id = 'Human'
        }

        if(ClickBottomMenu){
            // SetLoadingChangeGT(true)
            axios.get("http://examode.dei.unipd.it/exatag/annotationlabel/user_labels", {params: {language:props.language,ns_id:ns_id,username:username_to_call,report_id: props.reports[props.ind].id_report.toString()}}).then(response => {
                setLabels_to_show(response.data['labels']);


            })


            SetClickBottomMenu(false)
            // SetLoadingChangeGT(false)
        }



    },[ClickBottomMenu,ShowAutoAnn,userGT])



    return(

        <div className="buttongroup">

            <ButtonGroup>
                    <OverlayTrigger
                        key='top'
                        placement='top'
                        overlay={
                            <Tooltip id={`tooltip-top'`}>
                                Your annotation
                            </Tooltip>
                        }
                    >
                    <Button  ref ={but1} onClick={()=>UserGT()} id='current' size = 'sm' variant="secondary">
                        <FontAwesomeIcon icon={faUser} />
                    </Button>
                    </OverlayTrigger>
                    <OverlayTrigger
                        key='top'
                        placement='top'
                        overlay={
                            <Tooltip id={`tooltip-top'`}>
                                Robot's annotation
                            </Tooltip>
                        }
                    >
                        {/*<Button disabled={RobotPresence === false || Annotation === 'Automatic' || Language !== 'English'} ref={but2} onClick={() => RobotGT()} id='robot' size='sm' variant="secondary">*/}
                        <Button disabled={RobotPresence === false || props.robot === true} ref={but2} onClick={() => RobotGT()} id='robot' size='sm' variant="secondary">
                            <FontAwesomeIcon icon={faRobot}/>
                        </Button></OverlayTrigger>

                </ButtonGroup>
        </div>
    );



}

export default ChangeMemberGTModal