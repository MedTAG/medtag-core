import React, {Component, useContext, useEffect, useRef, useState} from 'react'
import axios from "axios";
import Button from "react-bootstrap/Button";
import ButtonGroup from "react-bootstrap/ButtonGroup";
import 'bootstrap/dist/css/bootstrap.min.css';
import {Container,Row,Col} from "react-bootstrap";
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


function ChangeMemberGT(props){
    const { fieldsToAnn,userchosen,finalcount,username,showmember,showmajority,reached,showautoannotation,reportString,fields,annotation,report,usecase,concepts,semanticArea, disButton,labelsToInsert, selectedconcepts,linkingConcepts, radio, checks,save, userLabels, labelsList, mentionsList, action, reports, index, mentionSingleWord, allMentions, tokens, associations } = useContext(AppContext);
    const [associations_to_show,SetAssociations_to_show] = associations;
    const [labels, setLabels] = labelsList
    const [Checks, setChecks] = checks;
    const [Fields,SetFields] = fields;
    const [FieldsToAnn,SetFieldsToAnn] = fieldsToAnn;
    const [SavedGT,SetSavedGT] = save;
    const [LabToInsert,SetLabToInsert] = labelsToInsert;
    const [Annotation,SetAnnotation] = annotation
    const [UseCase,SetUseCase] = usecase;
    const [reportsString, setReportsString] = reportString;
    const [FinalCount, SetFinalCount] = finalcount;
    const [FinalCountReached, SetFinalCountReached] = reached;
    const [ShowAutoAnn,SetShowAutoAnn] = showautoannotation;
    const [ShowMemberGt,SetShowMemberGt] =showmember
    const [ShowMajorityGt,SetShowMajorityGt] = showmajority
    const [Disable_Buttons, SetDisable_Buttons] = disButton;
    const [labels_to_show, setLabels_to_show] = userLabels;
    const [RadioChecked, SetRadioChecked] = radio;
    const [selectedConcepts, setSelectedConcepts] = selectedconcepts;
    const [Children,SetChildren] = tokens;
    const [mentions_to_show,SetMentions_to_show] = mentionsList;
    const [WordMention, SetWordMention] = mentionSingleWord;
    const [Report, setReport] = report;
    const [AllMentions, SetAllMentions] = allMentions;
    const [Reports, setReports] = reports;
    const [Index, setIndex] = index;
    const [UserLabels, SetUserLables] = userLabels;
    const [Action, SetAction] = action;
    const [Disabled,SetDisabled] = useState(true); //PER CLEAR
    const [ExaRobot,SetExaRobot] = useState(false)
    const [Concepts, SetConcepts] = concepts;
    const [ChangeButton,SetChangeButton] = useState(false)
    const [Username,SetUsername] = username
    const [SemanticArea, SetSemanticArea] = semanticArea;
    const [UserChosen,SetUserChosen] = userchosen
    const but1 = useRef(null)
    const but2 = useRef()
    const but3 = useRef()

    function order_array(mentions){
        var ordered = []
        var texts = []
        mentions.map((item,i)=>{
            texts.push(item.mention_text)
        })
        texts.sort()
        texts.map((start,ind)=>{
            mentions.map((ment,ind1)=>{
                if(start === ment.mention_text){
                    if(ordered.indexOf(ment) === -1){
                        ordered.push(ment)

                    }
                }
            })
        })
        return ordered
    }

    useEffect(()=>{
        but1.current.focus()
        but1.current.className = 'btn btn-primary btn-sm'
        but2.current.className = 'btn btn-outline-primary btn-sm'
        but3.current.className = 'btn btn-outline-primary btn-sm'
        SetChangeButton(false)
    },[Index,Action])

    function UserGT(){
        but1.current.className = 'btn btn-primary btn-sm'
        but2.current.className = 'btn btn-outline-primary btn-sm'
        but3.current.className = 'btn btn-outline-primary btn-sm'
        SetShowAutoAnn(false)
        SetShowMemberGt(false)
        SetChangeButton(false)

    }
    function RobotGT(){
        but1.current.className = 'btn btn-outline-primary btn-sm'
        but2.current.className = 'btn btn-primary btn-sm'
        but3.current.className = 'btn btn-outline-primary btn-sm'
        SetShowAutoAnn(true)
        SetShowMemberGt(false)
        SetChangeButton(false)

    }
    function MemberGT(){
        but1.current.className = 'btn btn-outline-primary btn-sm'
        but3.current.className = 'btn btn-primary btn-sm'
        but2.current.className = 'btn btn-outline-primary btn-sm'
        SetShowMemberGt(true)
        SetShowAutoAnn(false)
        SetChangeButton(false)

    }

    useEffect(()=>{
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
            if(UserChosen.endsWith('_auto')){
                username_to_call = UserChosen.substring(0,UserChosen.length - 5)
                ns_id = 'Robot'
            }
            else if (UserChosen.endsWith('_manual')){
                username_to_call = UserChosen.substring(0,UserChosen.length - 7)
                ns_id = 'Human'
            }
        }


        axios.get("http://127.0.0.1:8000/report_start_end", {params: {ns_id:ns_id,report_id: Reports[Index].id_report.toString()}}).then(response => {
            SetFinalCount(response.data['final_count']);SetFinalCountReached(false);SetChangeButton(true)
        })
        axios.get("http://127.0.0.1:8000/get_fields",{params:{ns_id:ns_id}}).then(response => {SetFields(response.data['fields']);SetFieldsToAnn(response.data['fields_to_ann']);})

        if(Action === 'labels'){
            axios.get("http://127.0.0.1:8000/annotationlabel/all_labels",{params:{ns_id:ns_id}}).then(response => {setLabels(response.data['labels'])})
            axios.get("http://127.0.0.1:8000/annotationlabel/user_labels", {params: {ns_id:ns_id,username:username_to_call,report_id: Reports[Index].id_report.toString()}}).then(response => {
                setLabels_to_show(response.data[Action.toString()]);
            })
        }
        else if(Action === 'concepts'){
            axios.get("http://127.0.0.1:8000/get_semantic_area",{params: {ns_id:ns_id}}).then(response => SetSemanticArea(response.data['area']))
            axios.get("http://127.0.0.1:8000/conc_view",{params: {ns_id:ns_id}}).then(response => {SetConcepts(response.data['concepts'])})
            axios.get("http://127.0.0.1:8000/contains", {params: {ns_id:ns_id,username:username_to_call,report_id: Reports[Index].id_report.toString()}}).then(response => {setSelectedConcepts(response.data);})

        }

    },[ShowAutoAnn,ShowMemberGt])

    useEffect(()=>{
        var labels = Array.from(document.getElementsByName('labels'))
        // var tokens = Array.from(document.getElementsByClassName('token'))
        // var tokens_not = Array.from(document.getElementsByClassName('notSelected'))
        // var concept_list = document.getElementById('concept_list_id')
        // var sem_area_list = document.getElementById('semanticAreaSelect')
        if(ShowMemberGt === true || ShowAutoAnn === true){
            console.log('è true')
            console.log(reportString)
            //Not modifiable
            labels.map((val,i)=>{
                val.setAttribute('disabled',true)
            })

        }
        else{
            if(Action === 'labels'){
                labels.map((val,i)=>{
                    val.removeAttribute('disabled')
                })
            }

        }

    },[ShowAutoAnn,ShowMemberGt])

    useEffect(()=>{
        if((ShowAutoAnn === true || ShowMemberGt === true) && ChangeButton === true){
            if(Action === 'mentions'){
                axios.get("http://127.0.0.1:8000/mention_insertion", {params: {ns_id:'Robot',report_id: Reports[Index].id_report.toString()}}).then(response => {
                    var mentions = (response.data[Action.toString()])

                    var ordered = order_array(mentions)
                    SetMentions_to_show(ordered);

                })
            }

            else if(Action === 'concept-mention'){
                axios.get("http://127.0.0.1:8000/insert_link/linked", {params: {ns_id:'Robot',report_id: Reports[Index].id_report.toString()}}).then(response => {
                    SetAssociations_to_show(response.data['associations']);
                })
                axios.get("http://127.0.0.1:8000/insert_link/mentions", {params: {ns_id:'Robot',report_id: Reports[Index].id_report.toString()}}).then(response => {
                    var mentions = (response.data['mentions1']);
                    var ordered = order_array(mentions)
                    SetAllMentions(ordered)
                })
            }
        }
        else{
            if(Action === 'mentions'){
                axios.get("http://127.0.0.1:8000/mention_insertion", {params: {report_id: Reports[Index].id_report.toString()}}).then(response => {
                    var mentions = (response.data[Action.toString()])

                    var ordered = order_array(mentions)
                    SetMentions_to_show(ordered);

                })
            }
            else if(Action === 'concept-mention'){
                axios.get("http://127.0.0.1:8000/insert_link/linked", {params: {report_id: Reports[Index].id_report.toString()}}).then(response => {
                    SetAssociations_to_show(response.data['associations']);
                })
                axios.get("http://127.0.0.1:8000/insert_link/mentions", {params: {report_id: Reports[Index].id_report.toString()}}).then(response => {
                    var mentions = (response.data['mentions1']);
                    var ordered = order_array(mentions)
                    SetAllMentions(ordered)
                })
            }
        }
    },[FinalCount,reportString,ChangeButton])

    return(

        <div className="buttongroup">

            <ButtonGroup>
                <Button ref ={but1} onClick={()=>UserGT()} id='current' size = 'sm' variant="secondary">
                    <FontAwesomeIcon icon={faUser} />
                </Button>
                <Button ref = {but2} onClick={()=>RobotGT()} id='robot' size = 'sm' variant="secondary">
                    <FontAwesomeIcon icon={faRobot} />
                </Button>
                <Button ref = {but3} onClick={()=>MemberGT()} id='mate' size = 'sm' variant="secondary">
                    <FontAwesomeIcon icon={faUserFriends} />
                </Button>
            </ButtonGroup>
        </div>
    );



}

export default ChangeMemberGT