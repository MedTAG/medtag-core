import {Col, OverlayTrigger, Row} from "react-bootstrap";
import Button from "react-bootstrap/Button";
import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";
import {faChevronLeft, faChevronRight, faProjectDiagram} from "@fortawesome/free-solid-svg-icons";
import React, {useContext, useEffect, useState} from "react";
import axios from "axios";
import {AppContext} from "../../App";
import { confirm } from '../Dialog/confirm'
import regeneratorRuntime from "regenerator-runtime";
import Tooltip from "react-bootstrap/Tooltip";
import Alert from "react-bootstrap/Alert";

import {
    faRobot,faUsers,faUser
} from '@fortawesome/free-solid-svg-icons';
import ChangeMemberGT from "./ChangeMemberGT";
import ChangeMemberGTModal from "./ChangeMemberGTModal";

function SubmitModal(props){

    const { fieldsToAnn,userchosen,finalcount,language,username,quickannotation,selectedLanguage,selectedInstitute,selectedUse,selectedbatch,showmember,showmajority,reached,showautoannotation,reportString,fields,annotation,report,usecase,concepts,semanticArea, disButton,labelsToInsert, selectedconcepts,linkingConcepts, radio, checks,save, userLabels, labelsList, mentionsList, action, reports, index, mentionSingleWord, allMentions, tokens, associations } = useContext(AppContext);
    const [associations_to_show,SetAssociations_to_show] = associations;
    const [labels, setLabels] = labelsList
    const [Checks, setChecks] = checks;
    const [QuickAnnotation,SetQuickAnnotation] = quickannotation

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
    // const [Reports, setReports] = reports;
    const [Index, setIndex] = index;
    const [UserLabels, SetUserLables] = userLabels;
    const [Action, SetAction] = action;
    const [Disabled,SetDisabled] = useState(true); //PER CLEAR
    const [ExaRobot,SetExaRobot] = useState(false)
    const [Concepts, SetConcepts] = concepts;
    // const [SelectedLang,SetSelectedLang] = selectedLang
    const [Username,SetUsername] = username
    const [SemanticArea, SetSemanticArea] = semanticArea;
    const [UserChosen,SetUserChosen] = userchosen
    const [Language, SetLanguage] = language;
    const [SelectedLang,SetSelectedLang] = selectedLanguage
    const [SelectedInstitute,SetSelectedInstitute] =selectedInstitute
    const [SelectedUse,SetSelectedUse] = selectedUse
    const [SelectedBatch,SetSelectedBatch] = selectedbatch

    const [Success,SetSuccess] = useState(0)

    useEffect(()=>{
        axios.get('http://examode.dei.unipd.it/exatag/get_post_fields_for_auto').then(function(response){
            if(Object.keys(response.data['extract_fields']).indexOf(UseCase) >=0){
                if(response.data['extract_fields'][UseCase].length >0){
                    SetExaRobot(true)
                }

            }


        }).catch(function(error){
            console.log('error: ',error)
        })
    },[UseCase])





    useEffect(()=>{
        if(ShowAutoAnn){
            axios.get("http://examode.dei.unipd.it/exatag/get_fields").then(response => {SetFields(response.data['fields']);SetFieldsToAnn(response.data['fields_to_ann']);})
            SetShowAutoAnn(false)
        }
    },[Report])

    useEffect(()=>{
        SetDisabled(true)
        var conc = false
        SemanticArea.map(area=>{
            if(selectedConcepts[area] !== undefined){
                if(selectedConcepts[area].length > 0){
                    conc = true
                }
            }
        })
        console.log('radio',RadioChecked)
        // console.log('disabledbutt',Disable_Buttons)

        if(Action === 'labels' && RadioChecked){

            SetDisabled(false)

        }
        else if(Action === 'mentions' && (mentions_to_show.length > 0 )){
            SetDisabled(false)
        }
        else if(Action === 'concepts' && conc === true){
            SetDisabled(false)
        }
        else if(Action === 'concept-mention' && (associations_to_show.length > 0)){
            SetDisabled(false)

        }

    },[associations_to_show,mentions_to_show,selectedConcepts,RadioChecked])



    const submit = (event,token) => {
        event.preventDefault();
        // if(Saved === false){
        //     SetSaved(true)
        var ns_id = 'Human'
        if(props.robot === true){
            ns_id = 'Robot'
        }
        if (token.startsWith('annotation')) {
            //const data = new FormData(document.getElementById("annotation-form"));
            // console.log('labtoinsert',LabToInsert)
            axios.post('http://examode.dei.unipd.it/exatag/annotationlabel/insert', {
                //labels: data.getAll('labels'),
                labels: LabToInsert,language:props.language,usecase:SelectedUse,
                report_id: props.reports[props.ind].id_report,ns_modal:ns_id
            })
                .then(function (response) {
                    // console.log(response);
                    SetSuccess(true)
                    // {concepts_list.length > 0 ? SetSavedGT(true) : SetSavedGT(false)}
                    if (LabToInsert.length === 0) {
                        SetRadioChecked(false)

                    }
                    // SetLabToInsert([])


                    SetSavedGT(prevState => !prevState)
                })
                .catch(function (error) {
                    SetSuccess(false)
                    console.log(error);
                });

        }



    }


    useEffect(()=>{
        if(LabToInsert.length === 0){
            SetRadioChecked(false)
        }
        else{
            SetRadioChecked(true)
        }
    },[LabToInsert])

    const ClickForDelete = (event,token)=>{
        event.preventDefault()
        var ns_id = 'Human'
        if(props.robot === true){
            ns_id = 'Robot'
        }
        if(token === 'annotation') {
            axios.post('http://examode.dei.unipd.it/exatag/annotationlabel/delete', {ns_modal:ns_id,language:props.language,report_id: props.reports[props.ind].id_report})
                .then(function (response) {
                    // console.log(response);
                    //SetSavedGT(false)
                    SetRadioChecked(false)
                    SetSavedGT(prevState => !prevState)
                    const newItemsArr = new Array(labels.length).fill(false)
                    setChecks(newItemsArr);
                    SetLabToInsert([]) //added 30082021
                })
                .catch(function (error) {

                    console.log(error);
                });
            // console.log('delete')

        }



    }

    // const ClickForDelete = async (e,token) => {
    //     var confirm_string = ''
    //     if(token === 'annotation'){
    //         confirm_string = 'This action will remove ALL the selected labels. This is irreversible. Are you sure?'
    //     }
    //
    //
    //     if (await confirm({
    //         confirmation: confirm_string
    //     })) {
    //         deleteEntries(e,token)
    //         console.log('yes');
    //     } else {
    //         console.log('no');
    //     }
    // }
    return(

        // <div style={{'position':'absolute', 'width':'100%','padding':'10px','bottom':'0%'}}>
        <div style={{'position':'absolute','text-align':'center', 'width':'100%','padding':'0px','bottom':'0%'}}>
            {Success === true && <Alert  variant='success'>The annotation has been successfully saved.
            </Alert> }
            {Success === false && <Alert variant='danger'>An error occurred saving the annotation.
            </Alert>}
            {/*{Success === 0 && <Alert variant='danger'>An error occurred saving the annotation.*/}
            {/*</Alert>}*/}
            <div className='two_buttons_div' >
                {ShowMemberGt === false && ShowAutoAnn === false && <><span style={{'float': 'left', 'width': '24.5%'}}>
                    <Button size='sm'  style={{'width': '80%'}} className="btn save"
                            onClick={(e) => ClickForDelete(e, props.token)} type="submit"
                            variant="danger">Clear</Button>
                </span>
                    <span style={{'float':'right','width':'24.5%'}}> <Button size='sm' disabled={Disable_Buttons}   style={{'width':'80%'}} className="btn clear" type="submit"  onClick={(e)=>submit(e,props.token)} variant="success">Save</Button>
                    </span></>}

                {QuickAnnotation === true && <ChangeMemberGTModal robot = {props.robot} reports = {props.reports} ind = {props.ind} language = {props.language} />}
            </div>
        </div>


    );
}


export default SubmitModal
