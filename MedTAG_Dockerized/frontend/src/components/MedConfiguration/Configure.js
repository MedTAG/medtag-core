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
import {
    BrowserRouter as Router,
    Switch,
    useRouteMatch,
    Route,
    Link,
    Redirect
} from "react-router-dom";
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
import ConfigureResult from "./ConfigureResult";


export const ConfigureContext = createContext('')

function Configure() {


    const { admin,showbar,username,usecaseList,reports,languageList,instituteList } = useContext(AppContext);
    const [AutoUses,SetAutoUses] = useState([])
    const [ShowModalToComplete,SetShowModalToComplete] = useState(false)
    const [Username,SetUsername] = username;
    const [Reports,SetReports] = reports;
    const [Admin,SetAdmin] = admin;
    const [OnlyPub,SetOnlyPub] = useState(false)
    const [AutoMedTagReports,SetAutoMedTagReports] = useState(false)
    const [LoadingAnnoResp,SetLoadingAnnoResp] = useState(false)
    const [UsesInserted,SetUsesInserted] = useState([])
    const [PubMedUsesInserted,SetPubMedUsesInserted] = useState([])
    const [BackClick, SetBackClick] = useState(false)
    const [Keys, SetKeys] = useState([])
    const [WarningMessage, SetWarningMessage] = useState('')
    const [DisConfirm,SetDisConfirm] = useState(true)
    const [ShowModalAuto,SetShowModalAuto] = useState(false)
    const [CheckUsername,SetCheckUsername] = useState(0)
    const [CheckReport,SetCheckReport] = useState(0)
    const [CheckLabels,SetCheckLabels] = useState(0)
    const [CheckConcept,SetCheckConcept] = useState(0)
    const [CheckPubMed,SetCheckPubMed] = useState(0)
    const [CheckJsonDisp,SetCheckJsonDisp] = useState(0)
    const [CheckJsonAnn,SetCheckJsonAnn] = useState(0)
    const [LoadExaConcepts,SetLoadExaConcepts] = useState(false)
    const [AutoAnno,SetAutoAnno] = useState(false)
    // const [ShowExaConcepts,SetShowExaConcepts] = useState(true)
    // const [ShowExaLabels,SetShowExaLabels] = useState(true)
    const [FieldsUseCasesToExtract,SetFieldsUseCasesToExtract] = useState(false)
    const [LoadExaLabels,SetLoadExaLabels] = useState(false)
    const [Disabled,SetDisabled] = useState(true)
    const [Message, SetMessage] = useState('')
    const [ErrorMessage, SetErrorMessage] = useState('')
    const [AutoAnnoCompleted,SetAutoAnnoCompleted] = useState(false)
    const [LoadingResponse, SetLoadingResponse] = useState(false)
    const [SaveData, SetSaveData] = useState(false)
    const [ShowConfirm, SetShowConfirm] = useState(false)
    const [Missing,SetMissing] = useState('')
    const [FormToSend,SetFormToSend] = useState('')
    const [ShowConceptExample,SetShowConceptExample] = useState(false)
    const [ShowReportExample,SetShowReportExample] = useState(false)
    const [ShowLabelExample,SetShowLabelExample] = useState(false)
    const [ShowPubMedExample,SetShowPubMedExample] = useState(false)
    const [ShowDeletePubMed,SetShowDeletePubMed] = useState(false)
    const [PubMedMissingAuto,SetPubMedMissingAuto] = useState({})
    const [WarningReport,SetWarningReport] = useState(0)
    const [WarningPubMed,SetWarningPubMed] = useState(0)
    const [WarningLabels,SetWarningLabels] = useState(0)
    const [WarningConcept,SetWarningConcept] = useState(0)
    const [WarningJsonDisp,SetWarningJsonDisp] = useState('')
    const [WarningJsonAnn,SetWarningJsonAnn] = useState(0)
    const [AutoPub,SetAutoPub] = useState(0)
    const [ShowDeleteReports,SetShowDeleteReports] = useState(false)
    const [ShowDeleteLabels,SetShowDeleteLabels] = useState(false)
    const [ShowDeleteConcepts,SetShowDeleteConcepts] = useState(false)
    const [GeneralMessage,SetGeneralMessage] = useState('')
    const [FinalMessage,SetFinalMessage] = useState('')
    const [LoadingPubMedResp,SetLoadingPubMedResp] = useState(false)
    const [AutoPubMedCompleted,SetAutoPubMedCompleted] = useState(false)
    const [AutoMessage,SetAutoMessage] = useState('')
    const [PubMessage,SetPubMessage] = useState('')
    const [ErrorAutoMessage,SetErrorAutoMessage] = useState('')
    const [ErrorPubMessage,SetErrorPubMessage] = useState('')
    var FileDownload = require('js-file-download');


    function handleCloseToComplete(){
        SetShowModalToComplete(false)
        SetFinalMessage('')
        SetWarningReport(0)
        SetWarningPubMed(0)
        SetWarningLabels(0)
        SetWarningConcept(0)
        SetWarningJsonDisp('')
        SetGeneralMessage('')
        SetCheckJsonAnn(0)
        SetCheckJsonDisp(0)
        SetCheckLabels(0)
        SetCheckPubMed(0)
        SetCheckConcept(0)
        SetCheckUsername(0)
        SetWarningJsonAnn(0)

        SetCheckReport(0)
    }
    useEffect(()=>{
        if(LoadingResponse === false){
            window.scrollTo(0,0)
        }
    },[LoadingResponse])

    useEffect(()=>{
        window.scrollTo(0, 0)
        SetCheckReport(0)
        SetCheckUsername(0)

        SetCheckPubMed(0)
        SetCheckLabels(0)
        SetCheckConcept(0)
        SetMissing('')
        SetCheckJsonDisp(0)
        SetCheckJsonAnn(0)
        if(Admin !== '' && Username !== 'Test'){
            SetCheckUsername(true)
        }
    },[])

    function onCheckAll(e){
        e.preventDefault()
        SetGeneralMessage('')
        SetFinalMessage('')
        var input = ''
        var formData = new FormData();

        if(Admin === '' && Username === 'Test') {
            input = document.getElementById('formBasicUsername');
            // console.log('test input', input.value)
            var username = input.value
            formData.append('username', username);

            input = document.getElementById('formBasicPassword');
            // console.log('test input', input.value)
            var password = input.value
            formData.append('password', password);
        }

        input = document.getElementById('exampleFormControlFile0');
        // console.log('test input',input.files)
        if(input.files[0] !== undefined || input.files[0] !== null) {
            for (let ind = 0; ind < input.files.length; ind++) {
                var name = 'reports' + ind.toString()
                formData.append(name, input.files[ind]);
            }
        }
        input = document.getElementById('exampleFormControlFile5');
        // console.log('test input',input.files)
        if(input.files[0] !== undefined || input.files[0] !== null) {
            for (let ind = 0; ind < input.files.length; ind++) {
                var name = 'pubmed' + ind.toString()
                formData.append(name, input.files[ind]);
            }
        }

        input = document.getElementById('exampleFormControlFile2');
        // if(ShowExaConcepts === false){
        if(input.files[0] !== undefined || input.files[0] !== null) {

            for (let ind = 0; ind < input.files.length; ind++) {
                var name = 'concepts' + ind.toString()
                formData.append(name, input.files[ind]);
            }
        }

        // }

       input = document.getElementById('exampleFormControlFile4');
        // if(ShowExaLabels === false){
        if(input.files[0] !== undefined || input.files[0] !== null) {
            for (let ind=0; ind<input.files.length; ind++) {
                var name = 'labels' + ind.toString()
                formData.append(name, input.files[ind]);
            }
            // }
        }

        // SetCheckJsonDisp(0)
        // SetCheckJsonAnn(0)
        var displayed = []
        var annotate = []
        Keys.map(key=>{

            var radios = document.getElementsByName(key);
            for(let i = 0; i < radios.length; i++ ) {
                if( radios[i].checked ) {
                    // console.log('value',radios[i].value)

                    if(radios[i].value === 'display'){
                        displayed.push(key)
                    }
                    else if(radios[i].value === 'both'){
                        annotate.push(key)

                    }
                }
            }

        })
        // console.log('disp',displayed)
        // console.log('disp',annotate)
        formData.append('json_disp', displayed);
        formData.append('json_ann', annotate);
        if(LoadExaConcepts === true){
            formData.append('exa_concepts', [...new Set(UsesInserted.concat(PubMedUsesInserted))]);
        }
        if(LoadExaLabels === true){
            formData.append('exa_labels', [...new Set(UsesInserted.concat(PubMedUsesInserted))]);
        }

        axios({
            method: "post",
            url: "http://0.0.0.0:8000/check_input_files",
            data: formData,
            headers: { "Content-Type": "multipart/form-data" },
        })

            .then(function (response) {
                var error = ''
                var err = false
                var gen = false
                var pub = false
                // console.log('message', response.data);
                // console.log('general_message',response.data['general_message'])
                if(!response.data['general_message'].startsWith('PUBMED') && (response.data['general_message'] !== '' && response.data['general_message'] !== 'Ok')){
                    SetFinalMessage(response.data['general_message'])
                    gen = true
                }

                if (response.data['general_message'].startsWith('PUBMED')){
                    pub = true
                }

                if (response.data['pubmed_message'] === 'Ok'  ) {
                    SetCheckPubMed(true)
                }
                else if (response.data['pubmed_message']===''){
                    SetCheckPubMed(0)
                }
                else if(response.data['pubmed_message'].includes('WARNING')){
                    SetWarningPubMed(response.data['pubmed_message'])
                }
                else {
                    error = response.data['pubmed_message']
                    SetCheckPubMed(error)
                    err = true
                    input = document.getElementById('exampleFormControlFile5');
                    if (input.files[0] !== undefined && input.files[0] !== null) {
                        input.value = null
                        SetShowDeletePubMed(false)
                        SetPubMedUsesInserted([])

                    }
                }
                if (response.data['report_message'] === 'Ok') {
                    SetCheckReport(true)

                }
                else if (response.data['report_message'] === ''){
                    SetCheckReport(0)
                }
                else if(response.data['report_message'].includes('WARNING')){
                    SetWarningReport(response.data['report_message'])
                }
                else {
                    error = response.data['report_message']
                    SetCheckReport(error)
                    err = true
                    input = document.getElementById('exampleFormControlFile0');
                    if (input.files[0] !== undefined && input.files[0] !== null) {
                        input.value = null
                        SetShowDeleteReports(false)
                        SetKeys([])
                        SetUsesInserted([])
                    }
                }
                if (response.data['username_message'] === 'Ok') {
                    SetCheckUsername(true)

                }
                else {
                    error = response.data['username_message']
                    SetCheckUsername(error)
                    err = true
                }

                if (response.data['concept_message'] === 'Ok') {
                    SetCheckConcept(true)
                }
                else if(response.data['concept_message'].includes('WARNING')){
                    SetWarningConcept(response.data['concept_message'])
                }
                else if (response.data['concept_message'] === '') {
                    SetCheckConcept(0)

                }
                else {
                    error = response.data['concept_message']
                    SetCheckConcept(error)
                    err = true
                    input = document.getElementById('exampleFormControlFile2');
                    // if(ShowExaConcepts === false){
                    if(input.files[0] !== undefined && input.files[0] !== null) {
                        input.value = null
                        SetShowDeleteConcepts(false)

                    }
                    // }

                }

                if (response.data['label_message'] === 'Ok') {
                    SetCheckLabels(true)

                }
                else if (response.data['label_message'] === '') {
                    SetCheckLabels(0)

                }
                else if(response.data['label_message'].includes('WARNING')){
                    // console.log('warninglabels')
                    SetWarningLabels(response.data['label_message'])
                }
                else {
                    error = response.data['label_message']
                    input = document.getElementById('exampleFormControlFile4');
                    // if(ShowExaLabels === false){
                    if(input.files[0] !== undefined && input.files[0] !== null) {
                        input.value = null
                        SetShowDeleteLabels(false)
                        // }
                    }




                    // console.log('ERRORE LABELS')
                    SetCheckLabels(error)
                    err = true
                }
                if (response.data['fields_message'] === 'Ok') {
                    SetWarningJsonDisp('')
                    SetWarningJsonAnn('')
                    SetCheckJsonDisp(true)
                    if (annotate.length > 0) {
                        SetCheckJsonAnn(true)

                    }
                } else if (response.data['fields_message'].includes('WARNING')) {
                    // if(token === 'json_fields'){
                    SetWarningJsonDisp(response.data['fields_message'])
                    // }
                } else if (response.data['fields_message']==='') {
                    SetCheckJsonDisp(0)
                    SetCheckJsonAnn(0)
                } else {
                    error = response.data['fields_message']
                    SetCheckJsonDisp(error)
                    SetCheckJsonAnn(error)
                    SetWarningJsonAnn('')
                    SetWarningJsonDisp('')
                    err = true
                }
                console.log('gen',gen)
                console.log('err',err)
                console.log('pub',pub)
                if(err === false && gen === false && pub === false){
                    SetFinalMessage('OK. All the files uploaded are compliant to the required format. You can proceed and confirm.')
                }
                else if(err === false && gen === false && pub === true){
                    SetFinalMessage('OK. You inserted PubMED files without concepts and labels. Keep in mind that only mention annotation will be available. You can proceed and confirm.')

                }

                else if((gen === false && err === true) || (gen === true && err === false)){
                    SetFinalMessage('ERROR. An error occurred. Check the message below the files you have inserted.')

                }


            })
            .catch(function (error) {
                console.log('error message', error);
            });



    }



    useEffect(()=>{
        if(FinalMessage === '' || !FinalMessage.includes('OK')){
            SetDisConfirm(true)
        }
        else{
            SetDisConfirm(false)
        }


    },[CheckUsername,CheckConcept,CheckLabels,CheckReport,CheckPubMed,CheckJsonAnn,CheckJsonDisp,FinalMessage])



    function onAdd(e){
        e.preventDefault()
        if(DisConfirm === true){
            SetShowModalToComplete(true)
        }

        else{
            // console.log('trying to add')
            var input = ''
            var input1 = ''
            var reports = ''
            var labels = ''
            var concepts = ''
            var usecase = ''
            var areas = ''
            var json_disp = ''
            var json_ann = ''
            var miss_files = []
            var miss_json = []
            var formData = new FormData();
            if(Admin === '' && Username === 'Test'){
                input = document.getElementById('formBasicUsername');
                // console.log('test input',input.value)
                var username = input.value
                formData.append('username', username);
                // if(username === null || username === undefined || username === ''){
                //     miss_json.push('USERNAME')
                //     //SetMissing('REPORT FILE')
                // }
                input = document.getElementById('formBasicPassword');
                // console.log('test input',input.value)
                var password = input.value
                // if(password === null || password === undefined || password === ''){
                //     miss_json.push('PASSWORD')
                //     //SetMissing('REPORT FILE')
                // }
                formData.append('password', password);
            }
            input = document.getElementById('exampleFormControlFile0');
            // console.log('test input',input.files)
            for (let ind=0; ind<input.files.length; ind++) {
                var name = 'reports' + ind.toString()
                formData.append(name, input.files[ind]);

            }
            input1 = document.getElementById('exampleFormControlFile5');
            // console.log('test input',input.files)
            for (let ind=0; ind<input1.files.length; ind++) {
                var name = 'pubmed' + ind.toString()
                formData.append(name, input1.files[ind]);

            }
            if(input.files[0] === undefined || input.files[0] === null){
                miss_files.push('Reports')
            }
            if(input1.files[0] === undefined || input1.files[0] === null){
                miss_files.push('PubMed')
            }


            input = document.getElementById('exampleFormControlFile2');
            for (let ind=0; ind<input.files.length; ind++) {
                var name = 'concepts' + ind.toString()
                formData.append(name, input.files[ind]);
            }
            if(LoadExaConcepts===false){

                if(input.files[0] === undefined || input.files[0] === null){
                    miss_files.push('Concepts')
                }
            }



            input = document.getElementById('exampleFormControlFile4');

            for (let ind=0; ind<input.files.length; ind++) {
                var name = 'labels' + ind.toString()
                formData.append(name, input.files[ind]);
            }
            if(LoadExaLabels===false){
                if(input.files[0] === undefined || input.files[0] === null){
                    miss_files.push('Labels')
                    //SetMissing('REPORT FILE')
                }
            }

            // console.log('input files', input.files)



            var displayed = []
            var annotate = []
            var hide = []
            Keys.map(key=>{
                hide.push(key)
                var radios = document.getElementsByName(key);
                for(let i = 0; i < radios.length; i++ ) {
                    if( radios[i].checked ) {
                        if(radios[i].value === 'display'){
                            displayed.push(key)
                        }
                        else if(radios[i].value === 'both'){
                            annotate.push(key)

                        }
                    }
                }

            })
            if(displayed.length === 0){
                miss_json.push('fields to display')
            }
            if(annotate.length === 0){
                miss_json.push('fields to annotate')
            }
            // console.log('disp',displayed)
            // console.log('disp',annotate)
            formData.append('json_disp', displayed);
            formData.append('json_ann', annotate);
            formData.append('json_all', hide);
            if(LoadExaConcepts ===true){
                formData.append('exa_concepts', [...new Set(UsesInserted.concat(PubMedUsesInserted))])
            }
            if(LoadExaLabels===true){
                formData.append('exa_labels', [...new Set(UsesInserted.concat(PubMedUsesInserted))])
            }
            SetFormToSend(formData)


            if(miss_json.length > 0 && miss_files.length>0){
                var new_json = miss_json.join(", ")
                var new_files = miss_files.join(", ")
                SetMissing('You did not inserted the: ' + new_json + ' and the: ' + new_files + ' files.')
                // SetMissing('You did not inserted the: ' + new_json + ' fields and the: ' + new_files + ' files.')
            }
            else if(miss_json.length > 0){
                var new_json = miss_json.join(", ")
                SetMissing('You did not inserted the: ' + new_json + ' files.')
            }
            else if(miss_files.length >0){
                var new_files = miss_files.join(", ")
                SetMissing('You did not inserted the: ' + new_files + ' files.')
                // SetMissing('You did not inserted the: ' + new_files + ' files.')
            }
            else if(miss_json.length === 0 && miss_files.length === 0){
                SetMissing(false)
            }


            if(miss_json.length > 0 || miss_files.length > 0){
                SetShowConfirm(true)

            }
            else if(miss_json.length === 0 && miss_files.length === 0){
                SetSaveData(true)
                SetShowConfirm(false)
            }

        }

    }

    function handleClose(){
        // console.log('logmissing',Missing)
        // console.log('logmissing',FormToSend)
        SetShowConfirm(false)
        SetFinalMessage('')
        SetWarningReport(0)
        SetWarningPubMed(0)
        SetWarningLabels(0)
        SetWarningConcept(0)
        SetWarningJsonDisp('')
        SetWarningJsonAnn(0)
        SetGeneralMessage('')
        SetCheckJsonAnn(0)
        SetCheckPubMed(0)
        SetCheckJsonDisp(0)
        SetCheckLabels(0)
        SetCheckConcept(0)
        SetCheckUsername(0)
        SetCheckReport(0)
    }


    useEffect(()=>{
        window.scroll(0,0)
        if(SaveData === true && DisConfirm === true ){
            SetShowModalToComplete(true)
        }
        else if(SaveData === true && FormToSend !== ''){
            SetLoadingResponse(true)

            axios({
                method: "post",
                url: "http://0.0.0.0:8000/configure_db",
                data: FormToSend,
                headers: { "Content-Type": "multipart/form-data" },
            })
                .then(function (response) {
                    // console.log(response)
                    if(response.data['message'] !== undefined){
                        SetLoadingResponse(false)
                        SetMessage('MedTAG has been correctly configured.')
                        axios.get("http://0.0.0.0:8000/get_usecase_inst_lang").then(response => {
                            var arr = []
                            response.data['usecase'].map(use=>{
                                if(use.toLowerCase() === 'colon' || use.toLowerCase() === 'lung' || use.toLowerCase().includes('uterine') || use.toLowerCase().includes('cervix')){
                                    arr.push(use)
                                }
                            });
                            if(arr.length>0){
                                SetShowModalAuto(true)
                                SetAutoUses(arr)
                            }


                        })

                    }
                    else if(response.data['warning'] !== undefined) {
                        SetLoadingResponse(false)
                        SetWarningMessage(response.data['warning'])
                    }

                    else if(response.data['error'] !== undefined){
                        SetLoadingResponse(false)
                        var message = response.data['error'] + ' If you checked the files and were correct, the problem might be related to the database; check that all the mandatory fields are correctly inserted. Check that all the use cases and semantic areas are correctly written in all the files which include them.'
                        SetErrorMessage(message)

                    }

                })
                .catch(function (error) {
                    console.log(error);


                });

        }
    },[SaveData])



    function onSaveExample(e,token){
        e.preventDefault()
        axios.get('http://0.0.0.0:8000/download_examples', {params:{token:token}})
                .then(function (response) {

                    if(token === 'reports'){
                        FileDownload((response.data), 'reports_example.csv');
                    }
                    else if(token === 'pubmed'){
                        FileDownload((response.data), 'pubmed_example.csv');
                    }
                    else if(token === 'concepts'){
                        FileDownload((response.data), 'concepts_example.csv');
                    }
                    else if(token === 'labels'){
                        FileDownload((response.data), 'labels_example.csv');
                    }


                })
                .catch(function (error) {
                    console.log('error message', error);
                });

        }

    function deleteInput(e,token){
        e.preventDefault()
        SetGeneralMessage('')
        SetFinalMessage('')
        var input = ''
        if(token === 'concepts'){
            SetCheckConcept(0);
            input = document.getElementById('exampleFormControlFile2');
            // console.log('current',input)
            // if(ShowExaConcepts===false){
            if(input.files[0] !== undefined && input.files[0] !== null){
                input.value = null
                SetWarningConcept(0)

                SetShowDeleteConcepts(false)
                // SetShowExaConcepts(true)
                // console.log('current',input)

            }
            // }
        }

        else if(token === 'labels'){
            SetCheckLabels(0);
            input = document.getElementById('exampleFormControlFile4');
            // console.log('current',input)
            // if(ShowExaLabels===false){
            if(input.files[0] !== undefined && input.files[0] !== null){
                input.value = null
                SetWarningLabels(0)

                SetShowDeleteLabels(false)
                // SetShowExaLabels(true)
                // console.log('current',input)

            }
            // }
        }
        else if(token === 'reports'){
            SetCheckReport(0);
            input = document.getElementById('exampleFormControlFile0');
            // console.log('current',input)

            if(input.files[0] !== undefined && input.files[0] !== null){
                input.value = null
                // console.log('current',input)
                SetShowDeleteReports(false)
                SetKeys([])
                SetCheckJsonAnn(0)
                SetCheckJsonDisp(0)
                SetWarningJsonDisp('')
                SetWarningJsonAnn(0)
                SetWarningReport(0)
                SetUsesInserted([])
            }

        }

        else if(token === 'pubmed'){
            SetCheckPubMed(0);
            input = document.getElementById('exampleFormControlFile5');
            // console.log('current',input)

            if(input.files[0] !== undefined && input.files[0] !== null){
                input.value = null
                // console.log('current',input)
                SetShowDeletePubMed(false)

                SetWarningPubMed(0)
                SetPubMedUsesInserted([])
            }

        }



    }

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

    function showKeys(){
        var formData = new FormData()
        var input = document.getElementById('exampleFormControlFile0');
        // console.log('current',input)
        for (let ind=0; ind<input.files.length; ind++) {
            var name = 'reports' + ind.toString()
            formData.append(name, input.files[ind]);

        }
        axios({
            method: "post",
            url: "http://0.0.0.0:8000/get_keys_and_uses_from_csv",
            data: formData,
            headers: { "Content-Type": "multipart/form-data" },
        })
            .then(function (response) {
                // console.log(response)
                SetKeys(response.data['keys'])
                SetUsesInserted(response.data['uses'])

            })
            .catch(function (error) {
                console.log('error message', error);
            });

    }

    function get_uses_pubmed(){
        var formData = new FormData()
        var input = document.getElementById('exampleFormControlFile5');
        // console.log('current',input)
        for (let ind=0; ind<input.files.length; ind++) {
            var name = 'pubmed' + ind.toString()
            formData.append(name, input.files[ind]);

        }
        axios({
            method: "post",
            url: "http://0.0.0.0:8000/get_keys_and_uses_from_csv",
            data: formData,
            headers: { "Content-Type": "multipart/form-data" },
        })
            .then(function (response) {
                // console.log(response)
                SetPubMedUsesInserted(response.data['uses'])

            })
            .catch(function (error) {
                console.log('error message', error);
            });

    }

    function showDelete(event,token){
        event.preventDefault()
        if(token === 'reports'){
            var input = document.getElementById('exampleFormControlFile0');
            if(input.files[0] !== undefined && input.files[0] !== null){
                SetShowDeleteReports(true)
                SetCheckConcept(0)
                SetCheckLabels(0)
                SetWarningLabels(0)
                SetWarningConcept(0)
                SetWarningReport(0)
            }
        }
        else if(token === 'concepts'){
            var input = document.getElementById('exampleFormControlFile2');
            // if(ShowExaConcepts === false){
            if(input.files[0] !== undefined && input.files[0] !== null){
                SetShowDeleteConcepts(true)
                SetWarningConcept(0)

            }
            // }

        }
        else if(token === 'labels'){
            var input = document.getElementById('exampleFormControlFile4');
            // if(ShowExaLabels===false){
            if(input.files[0] !== undefined && input.files[0] !== null){
                SetShowDeleteLabels(true)
                SetWarningLabels(0)
            }
            // }

        }
        else if(token === 'pubmed'){
            var input = document.getElementById('exampleFormControlFile5');
            if(input.files[0] !== undefined && input.files[0] !== null){
                SetShowDeletePubMed(true)
                SetCheckConcept(0)
                SetCheckLabels(0)
                SetWarningLabels(0)
                SetWarningConcept(0)
                SetWarningReport(0)
            }

        }
    }

    // function change_input(){
    //     var dis = []
    //     UsesInserted.map((el,ind)=> {
    //         var elems = Array.from(document.getElementsByName(el))
    //         var bool = true
    //         elems.map(input_lab => {
    //             if (input_lab.checked === true) {
    //                 bool = false
    //
    //             }
    //
    //         })
    //         dis.push(bool)
    //
    //     })
    //     if(dis.every(v => v === false)){
    //         SetDisabled(false)
    //         SetAutoMedTagReports(true)
    //
    //     }
    //     else{
    //         SetDisabled(true)
    //     }
    //
    //
    // }
    // useEffect(()=>{
    //     console.log('fields',FieldsUseCasesToExtract)
    //     console.log('fields',UsesInserted)
    // },[FieldsUseCasesToExtract])
    //
    //
    //
    // function get_auto_ann(key){
    //     var selected_obj = {}
    //     window.scroll(0,0)
    //
    //
    //
    //     console.log(AutoPub)
    //     console.log(AutoMedTagReports)
    //     if (key === 'pubmed'){
    //         SetLoadingPubMedResp(true)
    //         UsesInserted.map(el=>{
    //             selected_obj[el] = []
    //
    //             selected_obj[el].push('abstract')
    //             selected_obj[el].push('title')
    //         })
    //         axios.post('http://0.0.0.0:8000/create_auto_annotations',{
    //                 usecase:UsesInserted,
    //                 selected:selected_obj,
    //                 report_type:key
    //             }
    //         )
    //             .then(function(response){
    //                 console.log(response.data)
    //                 // setShowModalAuto(false)
    //                 SetLoadingPubMedResp(false)
    //                 SetAutoPubMedCompleted(true)
    //                 SetPubMessage('OK')
    //
    //
    //             }).catch(function (error) {
    //             //alert('ATTENTION')
    //             SetLoadingPubMedResp(false)
    //             SetAutoPubMedCompleted(false)
    //             SetPubMessage('ERROR')
    //
    //             console.log(error);
    //         });
    //     }
    //     else if (key === 'reports'){
    //         SetLoadingAnnoResp(true)
    //         key = 'reports'
    //         UsesInserted.map(el=>{
    //             selected_obj[el] = []
    //             var elems = Array.from(document.getElementsByName(el))
    //             elems.map(elem=>{
    //                 if(elem.checked === true){
    //                     selected_obj[el].push(elem.value)
    //                 }
    //             })
    //         })
    //         axios.post('http://0.0.0.0:8000/create_auto_annotations',{
    //                 usecase:UsesInserted,
    //                 selected:selected_obj,
    //                 report_type:key
    //             }
    //         )
    //             .then(function(response){
    //                 console.log(response.data)
    //                 // setShowModalAuto(false)
    //                 SetLoadingAnnoResp(false)
    //                 SetAutoAnnoCompleted(true)
    //                 SetAutoMessage('OK')
    //
    //
    //             }).catch(function (error) {
    //             //alert('ATTENTION')
    //             SetLoadingAnnoResp(false)
    //             SetAutoAnnoCompleted(false)
    //             SetAutoMessage('ERROR')
    //
    //             console.log(error);
    //         });
    //     }
    //
    //
    // }



    // useEffect(()=>{
    //     console.log('AUTOANN',AutoAnno)
    // },[AutoAnno])


    return (
        <div className="App">

            {Username !== Admin ?
                <div><h1>FORBIDDEN</h1>
                    <div>
                        <a href="http://0.0.0.0:8000/index">
                            Back
                        </a>
                    </div>
                </div>:

                <div>
            <ConfigureContext.Provider value={{pubmedusesinserted:[PubMedUsesInserted,SetPubMedUsesInserted],fieldsextra:[FieldsUseCasesToExtract,SetFieldsUseCasesToExtract],usesinserted:[UsesInserted,SetUsesInserted],errormessage:[ErrorMessage,SetErrorMessage],message:[Message,SetMessage],loadingresponse:[LoadingResponse,SetLoadingResponse],warningmessage:[WarningMessage,SetWarningMessage]}}
            >
            {/*{(LoadingResponse === true ) ? <div className='spinnerDiv'><Spinner animation="border" role="status"/></div>:*/}
            {/*    <div>*/}

            {/*        {Message !== '' &&*/}
            {/*        <Container fluid>*/}
            {/*            {LoadingAnnoResp === false ?<div>*/}
            {/*                <div>*/}
            {/*                    <h2>Your new configuration is ready</h2>*/}
            {/*                    <div>{Message}</div>*/}
            {/*                    {(UsesInserted.length > 0) ? <div><hr/>*/}
            {/*                    <div>*/}
            {/*                    You inserted reports related to the following use cases: {UsesInserted.join(', ')}. For them it is*/}
            {/*                        possible to perform automatic annotation. Click on <i>Auto Annotate</i> if you want to automatically annotate these reports otherwise cick on <i>Login</i>.*/}
            {/*                        If you prefer to automatically annotate them later, please, click on the side bar menu <FontAwesomeIcon icon={faBars}/> and go to: <i>Configure -> Update Configuration -> Get automatic annotations.</i>*/}
            {/*                    </div>*/}
            {/*                    <hr/>*/}
            {/*                        {AutoAnno === false ? <div>*/}
            {/*                            <Row>*/}
            {/*                            <Col md={3}></Col>*/}
            {/*                            <Col md={2}>*/}
            {/*                                <>*/}
            {/*                                    <span><a href="http://0.0.0.0:8000/logout"><Button variant = 'primary'>Login</Button></a></span>*/}
            {/*                                </>*/}
            {/*                            </Col>*/}
            {/*                            <Col md={1}></Col>*/}
            {/*                            <Col md={2}>*/}
            {/*                                <Button onClick={()=>SetAutoAnno(true)} variant='success'>Auto Annotate</Button>*/}
            {/*                            </Col>*/}
            {/*                            <Col md={3}>*/}

            {/*                            </Col>*/}
            {/*                        </Row>*/}

            {/*                    </div> : <div>*/}
            {/*                            <div>*/}
            {/*                                {LoadingResponse === false ?*/}
            {/*                                    <>{UsesInserted.length > 0 && OnlyPub === false && <> {UsesInserted.map(opt=>*/}
            {/*                                            <>{FieldsUseCasesToExtract[opt].length > 0 && <div>*/}
            {/*                                                <h5>{opt}</h5>*/}
            {/*                                                <div style={{'margin-bottom':'2%'}}><i>Select <b>at least</b> a field</i></div>*/}

            {/*                                                <div style={{'margin-bottom':'2%'}}>*/}
            {/*                                                    {FieldsUseCasesToExtract[opt].map(field=>*/}
            {/*                                                        <label>*/}
            {/*                                                            <input name={opt} value={field} onChange={()=>change_input()} type="checkbox" />{' '}*/}
            {/*                                                            {field}&nbsp;&nbsp;&nbsp;&nbsp;*/}
            {/*                                                        </label>*/}
            {/*                                                    )}*/}

            {/*                                                </div>*/}
            {/*                                            <hr/>*/}

            {/*                                            </div>}</>*/}
            {/*                                        )}*/}
            {/*                                        <div style={{'text-align':'center','margin-top':'2%'}}>*/}
            {/*                                            {AutoAnnoCompleted === false ? <div style={{margin:'2%'}}><Button id='commit_extracted' disabled={Disabled} onClick={()=>get_auto_ann('reports')} size='lg' variant='success'>Get the automatic annotations</Button></div> : <b>{AutoMessage}</b>}*/}
            {/*                                        </div></>}*/}

            {/*                                </> : <div className='spinnerDiv'><Spinner animation="border" role="status"/></div>}*/}
            {/*                                    </div>*/}
            {/*                            <hr/>*/}
            {/*                            {LoadingPubMedResp === false ? <> { PubMedMissingAuto['tot'] > 0 && <div>*/}
            {/*                                You inserted PubMed articles' ids for one or more the following use cases: <b>colon, uterine cervix, lung</b>. Do you want to automatically annotate them?*/}
            {/*                                <div style={{'text-align':'center','margin-top':'2%'}}>*/}
            {/*                                    {AutoPubMedCompleted === false ? <div style={{margin:'2%'}}><Button id='commit_extracted' onClick={()=>get_auto_ann('pubmed')} size='lg' variant='success'>Get the automatic annotations</Button></div> : <b>{PubMessage}</b>}*/}
            {/*                                </div>*/}

            {/*                                /!*<div>*!/*/}
            {/*                                /!*    <label>*!/*/}
            {/*                                /!*        <input name='pubmed' value='yes' onChange={()=>SetAutoPub(true)} type="radio" />{' '}*!/*/}
            {/*                                /!*        Yes&nbsp;&nbsp;&nbsp;&nbsp;*!/*/}
            {/*                                /!*    </label>*!/*/}
            {/*                                /!*    <label>*!/*/}
            {/*                                /!*    <input name='pubmed' value='no' onChange={()=>SetAutoPub(false)} type="radio" />{' '}*!/*/}
            {/*                                /!*    No&nbsp;&nbsp;&nbsp;&nbsp;*!/*/}
            {/*                                /!*</label>*!/*/}
            {/*                                /!*</div>*!/*/}
            {/*                            </div>}*/}
            {/*                            </> : <div className='spinnerDiv'><Spinner animation="border" role="status"/></div>}*/}
            {/*                            <hr/>*/}
            {/*                            <div style={{'text-align':'center','margin-top':'2%'}}>*/}
            {/*                                <div><a href="http://0.0.0.0:8000/logout"><Button variant = 'primary'>Login</Button></a></div>*/}
            {/*                            </div>*/}



            {/*                            </div>}*/}

            {/*                        </div> : <div style={{'text-align':'center','margin-top':'2%'}}>*/}
            {/*                        <div><a href="http://0.0.0.0:8000/logout"><Button variant = 'primary'>Login</Button></a></div>*/}
            {/*                    </div>}*/}
            {/*                    /!*{AutoAnnoCompleted === true && <div>All the reports have been correctly automatically annotated.<hr/></div>}*!/*/}
            {/*                    /!*{AutoAnnoCompleted === false && <div><b>An error occurred during automatic annotation.</b> Please contact us, or try to automatically annotate in <i>Configure -> Update Configuration -> Get Automatic annotations</i>.<hr/></div>}*!/*/}
            {/*                    /!*{(UsesInserted.length === 0 || AutoAnnoCompleted !== 0) && <><div>Log in with your credentials</div><div style={{'text-align':'center'}}>*!/*/}
            {/*                    /!*    <span><a href="http://0.0.0.0:8000/logout"><Button variant = 'primary'>Login</Button></a></span>*!/*/}
            {/*                    /!*    </div></>}*!/*/}


            {/*                </div>*/}

            {/*            </div> : <div className='spinnerDiv'><Spinner animation="border" role="status"/></div>}*/}

            {/*        </Container>*/}
            {/*        }*/}
            {/*        {ErrorMessage !== '' &&*/}
            {/*        <Container fluid>*/}
            {/*            <div>*/}
            {/*                <h2>An error occurred</h2>*/}
            {/*                <div>{ErrorMessage}</div>*/}
            {/*                <hr/>*/}
            {/*                <div>Please, do the configuration again</div>*/}

            {/*            </div>*/}
            {/*            <div style={{'text-align':'center'}}>*/}
            {/*                <span><Link to="/infoAboutConfiguration"><Button variant='success'>Back to configure</Button></Link></span>&nbsp;&nbsp;*/}
            {/*            </div>*/}
            {/*        </Container>*/}
            {/*        }*/}
            {/*        {WarningMessage !== '' &&*/}
            {/*        <Container fluid>*/}
            {/*            <div>*/}
            {/*                <div>*/}
            {/*                    <h2>Your new configuration is ready</h2>*/}
            {/*                    <div>{WarningMessage}</div>*/}
            {/*                    <hr/>*/}
            {/*                    <div>Log in with your credentials.</div>*/}

            {/*                </div>*/}

            {/*            </div>*/}
            {/*            <div style={{'text-align':'center'}}>*/}
            {/*                <span><a href="http://0.0.0.0:8000/logout"><Button variant = 'primary'>Login</Button></a></span>*/}
            {/*            </div>*/}
            {/*        </Container>*/}
            {/*        }*/}


            {/*    </div>}*/}
            {/*{ <div >*/}

            {(LoadingResponse === false && Message === '' && ErrorMessage === '' && WarningMessage === '') ? <div >
                <Container fluid>
                    <Row>
                        <Col md={4}>
                            <Button className='back-button' onClick={(e)=>SetBackClick(true)}><FontAwesomeIcon icon={faArrowLeft} />Back to info</Button>
                        </Col>
                        <Col md={8}></Col>
                    </Row>
                    <div>
                    <h2 style={{'margin-top':'30px','margin-bottom':'30px','text-align':'center'}}>Configure MedTAG with your data</h2>
                    <div>
                        Please, provide us with all the files and information required to customize the application. <br/>
                        Follow these instructions:
                        <ul>
                            <li>Click on <span><Button variant="info" size='sm'>Example</Button></span> to see an example of a file accepted by the database.</li>
                            <li>Add the files required. You can add multiple files at once if they are in the same folder.</li>
                            <li>Click on <span><Button variant="primary" size='sm'>Check</Button></span> to control if the file (or information) you provided complies with the requirements.</li>
                            <li>Once you have checked all the files and information you want to insert, it will be displayed an “OK” under each file you provided if they are correct, or a warning, if there is something you should pay attention to. Click on <span><Button variant="success" size='sm'>Confirm</Button></span> to insert the data into the database. If some errors occurred, you will be informed. In this case, you have to correct the errors before confirm. <span style={{'font-weight':'bold'}}>If you did not insert the <i>Reports</i>, <i>Basic information</i> (if required) and one between the labels file, the concepts file, or one field to annotate, you will not be able to confirm.</span></li>

                        </ul>
                        <div>It is possible to automatically annotate <b>English</b> reports with concepts belonging to EXAMODE ontology and a set of predefined labels. At the moment, automatic annotation is possible on reports whose use cases are: <b>Colon, Lung, Uterine cervix</b> and whose language is <b>english</b>. If you plan to use automatic annotations please, <b>make sure your that in your csv the <i>language</i> fields are <i>"english"</i> and <i>usecase</i> fields are:</b>
                        <ul>
                            <li><i>Colon</i> (or <i>colon</i>) for reports regarding colon cancer cases </li>
                            <li><i>Uterine cervix</i> (or <i>uterine cervix</i>) for reports regarding uterus cancer cases</li>
                            <li><i>Lung</i> (or <i>lung</i>) for reports regarding lung cancer cases </li>

                        </ul>
                        </div>
                        <hr/>

                        <div>
                            <Form>
                                {Admin === '' && Username === 'Test' && <div><Form.Group controlId="formBasicUsername">
                                    <div>
                                        <h3>Basic information</h3>
                                        <div>Select a username and a password, once you selected a username check it in order to see if it is available. </div>
                                    </div>
                                    <div>Username</div>
                                    <Form.Control type="text" placeholder="Select a username..." />
                                </Form.Group>
                                    <Form.Group controlId="formBasicPassword">
                                        <div>Password</div>
                                        <Form.Control type="password" placeholder="Select a password..." />
                                    </Form.Group>

                                    <div>You are the admin, this means that you are the only one who can change configuration files. </div>
                                    {CheckUsername !== 0 && <div>
                                        {(CheckUsername === true && CheckUsername !== 0) ? <div style={{'color':'green'}}>The username and password are OK</div> : <div style={{'color':'red'}}><span>The username and/or the password contain some errors: </span><span>{CheckUsername}</span></div>}

                                    </div>}<hr/></div>}





                                <div><h3>PubMED IDs <i style={{'font-size':'1rem'}}>(Mandatory one between PubMED and reports files)</i></h3></div>
                                <Form.Group style={{'margin-top':'20px','margin-bottom':'20px'}}>
                                    <div><span>Insert here the .CSV file with the PubMED IDs of the articles you want to annotate. <i>Abstract</i> and <i>Title</i> sections will be annotable. <b>Three articles per second are inserted in the database, the more articles you add the more the entire process will take to finish. </b></span><div className='conf-div'><Button onClick={()=>SetShowPubMedExample(prev=>!prev)} variant="info" size='sm'>Example</Button></div></div>
                                    <Form.File id="exampleFormControlFile5" onClick={(e) => {(e.target.value = null);SetGeneralMessage('');SetFinalMessage('');SetShowDeletePubMed(false);SetCheckPubMed(0);SetWarningPubMed(0);SetLoadExaConcepts(false);SetLoadExaLabels(false);SetPubMedUsesInserted([]);}} onChange={(e)=>{get_uses_pubmed();showDelete(e,'pubmed');}} multiple/>
                                    {ShowDeletePubMed === true && <div><Button className='delete-button' onClick={(e)=>deleteInput(e,'pubmed')}><FontAwesomeIcon icon={faTimes} />Delete file</Button></div>}
                                </Form.Group>
                                {CheckPubMed !== 0 && <div>
                                    {(CheckPubMed === true ) ? <div style={{'color':'green'}}>OK</div> : <div style={{'color':'red'}}><span>The file contains some errors: </span><span>{CheckPubMed}</span></div>}
                                </div>}
                                {WarningReport !== 0 && <div style={{'color':'orange'}}>{WarningReport}</div>}
                                {ShowPubMedExample && <div style={{'text-align':'center'}}>This is an example of file with PubMED IDs.<br/> Your file must contain the header row (the one in boldface) containing the name of each column. <br/> <span style={{'font-weight':'bold'}}>Null values are not allowed for ID and usecase. </span>.
                                    <br/><br/>
                                    <div>If you prefer you can download the csv file.
                                        <span> <Button size='sm' onClick={(e)=>onSaveExample(e,'pubmed')} variant='warning'> <FontAwesomeIcon icon={faDownload} /> Download</Button></span>
                                    </div>
                                    <hr/>
                                    <div className='examples'>
                                        <div style={{'display':'flex','justify-content':'center'}}>
                                            <div>
                                                <span style={{'font-weight':'bold'}}>ID,usecase</span><br/>
                                                29691659,Colon<br/>
                                                20138539,Colon<br/>
                                                25918287,Colon<br/>

                                            </div>
                                        </div>
                                    </div>

                                </div>}



                                <hr/>

                                <div><h3>Reports <i style={{'font-size':'1rem'}}>(Mandatory one between PubMED and reports files)</i></h3></div>

                                <Form.Group style={{'margin-top':'20px','margin-bottom':'20px'}}>
                                    <div><span>Insert here the .CSV file with the reports to annotate.</span>
                                        <div className='conf-div'><Button onClick={()=>SetShowReportExample(prev=>!prev)} variant="info" size='sm'>Example</Button></div></div>
                                    <div style={{marginBottom:'2%',fontSize:'0.9rem'}}><i>Please, make sure the ids of the reports you insert do not start with "pubmed" and the institutes you insert are different from "pubmed".</i></div>
                                    <Form.File id="exampleFormControlFile0" onClick={(e) => {(e.target.value = null);SetGeneralMessage('');SetFinalMessage('');SetShowDeleteReports(false);SetCheckReport(0);SetCheckJsonAnn(0);SetWarningReport(0);SetCheckJsonDisp(0);SetWarningJsonDisp('');SetLoadExaConcepts(false);SetLoadExaLabels(false);SetCheckPubMed(0);SetUsesInserted([]);SetKeys([])}} onChange={(e)=>{showKeys();showDelete(e,'reports');}} multiple/>
                                    {ShowDeleteReports === true && <div><Button className='delete-button' onClick={(e)=>deleteInput(e,'reports')}><FontAwesomeIcon icon={faTimes} />Delete file</Button></div>}

                                </Form.Group>
                                {CheckReport !== 0 && <div>
                                    {(CheckReport === true ) ? <div style={{'color':'green'}}>OK</div> : <div style={{'color':'red'}}><span>The file contains some errors: </span><span>{CheckReport}</span></div>}

                                </div>}
                                {WarningReport !== 0 && <div style={{'color':'orange'}}>{WarningReport}</div>}
                                {ShowReportExample && <div style={{'text-align':'center'}}>This is an example of reports file.<br/> Your file must contain the header row (the one in boldface) containing the name of each column. <br/> <span style={{'font-weight':'bold'}}>Null values are not allowed for id_report, usecase, institute, language. </span>.
                                    <br/><br/>
                                    <div>If you prefer you can download the csv file.
                                        <span> <Button size='sm' onClick={(e)=>onSaveExample(e,'reports')} variant='warning'> <FontAwesomeIcon icon={faDownload} /> Download</Button></span>
                                    </div>
                                    <hr/>
                                    <div className='examples'>
                                        <div >
                                            <span style={{'font-weight':'bold'}}>id_report,language,institute,usecase,age,target_diagnosis</span><br/>
                                            024904af0078ed89be428dd5868803ce,English,default_hospital,Colon,63,right colon polyps: tubular adenoma with mild dysplasia glandular epithelium.<br/>
                                            d857a9f16b239c8b0321e0f3245809ec,English,default_hospital,Colon65,villous adenoma tubule with moderate dysplasia glandular epithelium. pseudoinvasione axis.<br/>
                                            369093624905afbb0ef2d5b530ca210e,English,default_hospital,Colon59,"adenoma tightened with mild dysplasia. the lesion spread over hemorrhoidal nodule."<br/>
                                            fc4988c5312da8c65282fdf7f1999af6,English,default_hospital,Colon68,right colon polyps: tubular adenomas with mild dysplasia glandular epithelium.<br/>

                                    </div></div>

                                </div>}
                                <hr />
                                {Keys.length > 0 && <div><h5>Reports' fields <i style={{'font-size':'1rem'}}>(It is mandatory to set at least one field to display. It is optional to set at least one field to annotate )</i></h5>
                                    <div style={{'margin-bottom':'20px'}}>Below you can find all the fields which characterize your reports. For each key, you have to decide if you want to display, hide, or display and annotate the value corresponding to that key. Remember that to perform mentions annotation, you must select at least one field checking the button <i>Display and Annotate</i></div>
                                    {Keys.map((key,ind)=>
                                        <Row><Col md = {4}>
                                            {key}</Col>
                                            <Col md={8}>
                                                <label><input
                                                    value='hide'
                                                    type="radio"
                                                    name={key}
                                                    onChange={()=>{SetFinalMessage('');SetWarningJsonDisp('');SetCheckJsonDisp(0);SetCheckJsonAnn(0)}}

                                                />&nbsp;
                                                Hide</label>&nbsp;&nbsp;&nbsp;&nbsp;
                                                <label><input
                                                    value='display'
                                                    type="radio"
                                                    name={key}
                                                    onChange={()=>{SetFinalMessage('');SetCheckJsonDisp(0);SetWarningJsonDisp('');SetCheckJsonAnn(0)}}
                                                    defaultChecked={true}
                                                />&nbsp;
                                                Display</label>&nbsp;&nbsp;&nbsp;&nbsp;
                                                <label><input
                                                    name={key}
                                                    type="radio"
                                                    value='both'
                                                    onChange={()=>{SetFinalMessage('');SetCheckJsonDisp(0);SetCheckJsonAnn(0);SetWarningJsonDisp('');}}

                                                />&nbsp;
                                                Display and Annotate</label>

                                            </Col>

                                        </Row>
                                    )}
                                    {CheckJsonDisp !== 0 && WarningJsonDisp === '' && <div>
                                        {(CheckJsonDisp === true ) ? <div style={{'color':'green'}}>The fields are OK</div> : <div style={{'color':'red'}}><span>The fields contain some errors: </span><span>{CheckJsonDisp}</span></div>}

                                    </div>}
                                    {WarningJsonDisp !== '' && <div style={{'color':'orange'}}>JSON FIELDS - {WarningJsonDisp}</div>}


                                </div>}


                                <hr />
                                <div><h3>Files for CONCEPTS IDENTIFICATION AND LINKING <i style={{'font-size':'1rem'}}>(Optional)</i></h3>If you want to perform concepts identification and linking you must provide the concepts.</div>
                                {([...new Set(UsesInserted.concat(PubMedUsesInserted))].length > 0)  &&<div>
                                    <hr/>

                                        <div>
                                            You inserted reports for: <b>{[...new Set(UsesInserted.concat(PubMedUsesInserted))].join(', ')}</b>; EXAMODE ontology is available for these secases. <b>You can use the EXAMODE ontology concepts OR upload your own ones.</b>&nbsp;&nbsp;
                                            {LoadExaConcepts === false ? <Button variant='primary' size = 'sm' onClick={()=>{SetCheckConcept(0);SetGeneralMessage('');SetFinalMessage('');SetWarningConcept(0);SetLoadExaConcepts(true)}}>Get EXAMODE concepts</Button> : <div style={{fontWeight:'bold',color:'royalblue'}}>You decided to add concepts of EXAMODE ontology <Button className='delete-button' onClick={()=>{SetCheckConcept(0);SetGeneralMessage('');SetFinalMessage('');SetWarningConcept(0);SetLoadExaConcepts(false)}}><FontAwesomeIcon icon={faTimes} /></Button></div>}
                                        </div>
                                    <hr/>
                                </div>}
                                <Form.Group style={{'margin-top':'20px','margin-bottom':'20px'}}>
                                    <div><span>Insert here the .CSV file with the concepts.</span><div className='conf-div'><Button onClick={()=>SetShowConceptExample(prev=>!prev)} variant="info" size='sm'>Example</Button></div></div>
                                    <Form.File id="exampleFormControlFile2" onClick={(e) => {SetShowDeleteConcepts(false);SetGeneralMessage('');SetFinalMessage('');SetWarningConcept(0);SetCheckConcept(0);(e.target.value = null)}} onChange={(e)=>{showDelete(e,'concepts');}}  multiple/>
                                    {ShowDeleteConcepts === true && <div><Button className='delete-button' onClick={(e)=>deleteInput(e,'concepts')}><FontAwesomeIcon icon={faTimes} />Delete file</Button></div>}
                                </Form.Group>

                                {CheckConcept !== 0 && WarningConcept === 0 &&  <div>
                                    {(CheckConcept === true && CheckConcept !== 0) ? <div style={{'color':'green'}}>OK</div> : <div style={{'color':'red'}}><span>The file contains some errors: </span><span>{CheckConcept}</span></div>}

                                </div>}
                                {WarningConcept !== 0 && <div style={{'color':'orange'}}>{WarningConcept}</div>}

                                {ShowConceptExample && <div style={{'text-align':'center'}}>This is an example of concepts file. <br/> Your file must contain the header row (the one in boldface) containing the name of each column. In each row the values must be comma separated.<br/> <span style={{'font-weight':'bold'}}>Null values are not allowed for concept_url, concept_name, usecase and area. </span>
                                    <br/><br/>
                                    <div>If you prefer you can download the csv file.
                                        <span> <Button size='sm' onClick={(e)=>onSaveExample(e,'concepts')} variant='warning'> <FontAwesomeIcon icon={faDownload} /> Download</Button></span>
                                    </div>

                                    <hr/>
                                    <div className='examples'>
                                        <div style={{'display':'flex','justify-content':'center'}}>
                                        <div>
                                        <span style={{'font-weight':'bold'}}>concept_url,concept_name,usecase,area</span><br/>
                                        {/*concept_url,name,json_concept,usecase,area<br/>*/}
                                        http://purl.obolibrary.org/obo/UBERON_0003346,Rectal mucous membrane,Colon,Anatomical Location<br/>
                                        http://purl.obolibrary.org/obo/UBERON_0001157,Transverse Colon,Colon,Anatomical Location<br/>
                                        http://purl.obolibrary.org/obo/UBERON_0001052,"Rectum, NOS",Colon,Anatomical Location<br/>
                                        http://purl.obolibrary.org/obo/UBERON_0001158,Descending colon,Colon,Anatomical Location<br/>
                                        http://purl.obolibrary.org/obo/UBERON_0001153,Caecum,Colon,Anatomical Location<br/>
                                        </div>
                                    </div></div>

                                </div>}
                                <hr />
                                <div><h3>Files for LABELS ANNOTATION <i style={{'font-size':'1rem'}}>(Optional)</i></h3>If you want to perform labels annotation you must provide the labels related to the use cases you are interested in.</div>
                                {([...new Set(UsesInserted.concat(PubMedUsesInserted))].length > 0) &&<div>
                                    <hr/>

                                        <div>
                                            You inserted reports for: <b>{[...new Set(UsesInserted.concat(PubMedUsesInserted))].join(', ')}</b>; EXAMODE labels are available for these usecases. <b>You can insert the EXAMODE labels or upload your own ones.</b>&nbsp;&nbsp;
                                            {LoadExaLabels === false ? <Button variant='primary' size = 'sm' onClick={()=>{SetGeneralMessage('');SetFinalMessage(''); SetCheckLabels(0);SetWarningLabels(0);SetLoadExaLabels(true)}}>Get EXAMODE labels</Button> :
                                                <div style={{fontWeight:'bold',color:'royalblue'}}>You decided to add EXAMODE labels <Button className='delete-button' onClick={()=>{SetGeneralMessage('');SetFinalMessage(''); SetCheckLabels(0);SetLoadExaLabels(false);SetWarningLabels(0)}}><FontAwesomeIcon icon={faTimes} /></Button></div>}


                                                </div>
                                    <hr/>

                                </div>}

                                <Form.Group style={{'margin-top':'20px','margin-bottom':'20px'}}>
                                    <div><span>Insert here the .CSV file with the annotation labels.</span><div className='conf-div'><Button onClick={()=>SetShowLabelExample(prev=>!prev)} variant="info" size='sm'>Example</Button></div></div>
                                    <Form.File id="exampleFormControlFile4" onClick={(e) => {SetShowDeleteLabels(false);SetWarningLabels(0);(e.target.value = null);SetGeneralMessage('');SetGeneralMessage('');SetFinalMessage(''); SetCheckLabels(0)}} onChange={(e)=>{showDelete(e,'labels');}} multiple/>
                                    {ShowDeleteLabels === true && <div><Button className='delete-button' onClick={(e)=>deleteInput(e,'labels')}><FontAwesomeIcon icon={faTimes} />Delete file</Button></div>}
                                </Form.Group>

                                {CheckLabels !== 0 && WarningLabels === 0 &&  <div>
                                    {(CheckLabels === true && CheckLabels !== 0) ? <div style={{'color':'green'}}>OK</div> : <div style={{'color':'red'}}><span>The file contains some errors: </span><span>{CheckLabels}</span></div>}

                                </div>}
                                {WarningLabels !== 0 ? <div style={{'color':'orange'}}>{WarningLabels}</div> : <div></div>}
                                {ShowLabelExample && <div style={{'text-align':'center'}}>This is an example of labels file. <br/> Your file must contain the header row (the one in boldface) containing the name of each column. In each row the values must be comma separated.<br/> <span style={{'font-weight':'bold'}}>Null values are not allowed, for each row you must provide a label and a usecase</span>
                                    <br/><br/>
                                    <div>If you prefer you can download the csv file.
                                        <span> <Button size='sm' onClick={(e)=>onSaveExample(e,'labels')} variant='warning'> <FontAwesomeIcon icon={faDownload} /> Download</Button></span>
                                    </div>
                                    <hr/>
                                    <div className='examples'>
                                        <div style={{'display':'flex','justify-content':'center'}}>
                                        <div>
                                        <span style={{'font-weight':'bold'}}>usecase,label</span><br/>
                                        Colon,Cancer<br/>
                                        Colon,Adenomatous polyp - high grade dysplasia<br/>
                                        Colon,Adenomatous polyp - low grade dysplasia<br/>
                                        Colon,Hyperplastic polyp<br/>
                                        Colon,Non-informative<br/>
                                        </div>
                                    </div>
                                    </div>

                                </div>}
                                <hr />
                                {FinalMessage !== '' ? <div style={{'margin-bottom':'20px'}}>
                                    {
                                        FinalMessage.includes('OK') ? <div style={{'color':'green','font-weight':'bold'}}>{FinalMessage}</div> : <div style={{'color':'red','font-weight':'bold'}}>{FinalMessage}</div>
                                    }

                                </div> : <div></div>}
                                <div style={{'text-align':'center'}}>
                                    <Button size='lg' variant="primary" onClick={(e)=>onCheckAll(e)}>
                                        Check
                                    </Button>&nbsp;&nbsp;
                                <Button size='lg' variant="success" onClick={(e)=>onAdd(e)}>
                                    Confirm
                                </Button>&nbsp;&nbsp;
                                    </div>

                            </Form>
                        </div>


                    </div>
                    </div>
                </Container>
            </div> : <ConfigureResult />}
            {BackClick === true && <Redirect to='./InfoAboutConfiguration'/>}
            {ShowModalToComplete === true && <Modal show={ShowModalToComplete} onHide={handleCloseToComplete}>
                <Modal.Header closeButton>
                    <Modal.Title>Attention</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    {/*<div>In order to confirm you need to provide the username the password (if these are required), the reports file (these are mandatory) and or the labels file, or the concepts file or you need to set at least one field to <i>Display and Annotate</i>.</div>*/}
                    {/*<div>If you have provided all the files and you have not checked them yet, please, click on Check button. If under all the files that you have inserted there is <i>Ok</i> or a warning you can Confirm and populate the database.</div>*/}
                    {/*<div>If the files have some errors, correct them and then confirm.</div>*/}
                    {FinalMessage === '' && <div>Please, Check the files you provided before confirm.</div>}
                    {FinalMessage !== '' && <div>Correct the error(s) before confirm. If you did not inserted the minimum number of files required you will not be able to confirm.</div>}
                </Modal.Body>
                <Modal.Footer>
                    <Button variant="primary" onClick={handleCloseToComplete}>
                        Ok
                    </Button>


                </Modal.Footer>
            </Modal>}
            {ShowConfirm === true && Missing !== '' && Missing !== false && <Modal show={ShowConfirm} onHide={handleClose}>
                <Modal.Header closeButton>
                    <Modal.Title>Attention</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    <div >{Missing}</div>
                    <div>Remember that without these files you will not be able to use all the functions this app provides.</div>
                    <div>Click on <i>Add more files</i> in order to add these fiels. Click on <i>Save anyway</i> to save the files you provided.</div>
                </Modal.Body>
                <Modal.Footer>
                    <Button variant="primary" onClick={handleClose}>
                        Add more files
                    </Button>&nbsp;&nbsp;
                    <Button variant="secondary" onClick={()=>{SetSaveData(true);SetShowConfirm(false)}}>
                        Save anyway
                    </Button>

                </Modal.Footer>
            </Modal>}

            </ConfigureContext.Provider>
                </div>}

        </div>


    );
}



export default Configure;


