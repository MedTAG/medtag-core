import React, {Component, useEffect, useState, useContext} from 'react'
import axios from "axios";
import 'bootstrap/dist/css/bootstrap.min.css';
import {Container,Row,Col} from "react-bootstrap";
import {
    faLanguage,
    faUser,
    faSignOutAlt,
    faMicroscope,
    faCogs,
    faHospital,
    faBars,
    faDownload,
    faRobot,faListOl
} from '@fortawesome/free-solid-svg-icons';
import {AppContext} from "../../App";
import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";
import Form from "react-bootstrap/Form";
import Button from "react-bootstrap/Button";
import Dropdown from "react-bootstrap/Dropdown";
import './selectMenu.css';
import OptionsModal from "./OptionsModal";
import Modal from "react-bootstrap/Modal";
import DownloadGT from "./DownloadGT";
import DownloadGTUser from "./DownloadGTUser";
// axios.defaults.xsrfCookieName = "csrftoken";
// axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";

function SelectMenu(props){
    const { reports,report_type,batchNumber,updateSingle,updateMenu,usecaseList,instituteList,languageList,annotation, index,username,showbar, report,action,showOptions,showDownload, insertionTimes,institute,language,usecase } = useContext(AppContext);
    const [ShowModalDownload, SetShowModalDownload] = showDownload;
    const [Annotation, SetAnnotation] = annotation
    const [ReportType, SetReportType] = report_type
    const [UseCase,SetUseCase] = usecase;
    const [BatchNumber,SetBatchNumber] = batchNumber
    const [BatchList,SetBatchList] = useState([])

    const [Username,SetUsername] = username;
    const [ShowBar,SetShowBar] = showbar;
    const [ShowModal, SetShowModal] = showOptions;
    const [Institute,SetInstitute] = institute;
    const [Language,SetLanguage] = language;
    const [UseCaseList,SetUseCaseList] = usecaseList;
    const [LanguageList,SetLanguageList] = languageList;
    const [InstituteList,SetInstituteList] = instituteList;
    const [Reports,SetReports] = reports
    const [Action,SetAction] = action
    const [Inst,SetInst] = useState('')
    const [Use,SetUse] = useState('')
    const [Lang,SetLang] = useState('')
    const [Rep,SetRep] = useState('')
    const [Batch,SetBatch] = useState('')
    const [Index,SetIndex] = index
    const [Report,SetReport] = report
    const [IndexSel, SetIndexSel] = useState(0)
    const [ArrayBool,SetArrayBool] = useState([])
    const [ArrayInsertionTimes,SetArrayInsertionTimes] = insertionTimes;
    const [LangFlag,SetLangFlag] = useState('')
    const [UpdateSingleReport,SetUpdateSingleReport] = updateSingle
    const [UpdateMenu, SetUpdateMenu] = updateMenu;

    useEffect(()=>{

        if(Language !== '' && UseCase !== '' && Institute !== '' && BatchNumber !== ''){

            SetLang(Language)
            SetInst(Institute)
            SetUse(UseCase)
            SetBatch(BatchNumber)
        }

    },[Language,UseCase,Institute,BatchNumber])



    useEffect(()=>{
        if(Use !== '' && Inst !== '') {
            if(Inst === 'PUBMED'){
                axios.get('http://0.0.0.0:8000/get_PUBMED_batch_list', {params: {usecase: Use}}).then(response => {
                    SetBatchList(response.data['batch_list']);
                })
            }
            else{
                axios.get('http://0.0.0.0:8000/get_batch_list', {params: {usecase: Use}}).then(response => {
                    SetBatchList(response.data['batch_list']);
                })
            }


        }
    },[UseCase,Use,Inst,Institute])


    function handleChange(e){
        SetShowModal(prevState => !prevState)
    }
    function handleChangeDownload(e){
        SetShowModalDownload(prevState => !prevState)
    }
    function handleBar(e){
        SetShowBar(prevState => !prevState)
    }
    function handleChangeLanguage(e){
        SetLang(e.target.value)
        // SetLanguage(e.target.value)
        axios.post("http://0.0.0.0:8000/new_credentials", {
            usecase: UseCase, language: e.target.value, institute: Institute, annotation: Annotation,report_type: ReportType,batch:BatchNumber
        })
            .then(function (response) {
                SetLanguage(e.target.value)
                SetUpdateMenu(true)

                // SetUpdateSingleReport(true)

            })
            .catch(function (error) {

                console.log('ERROR', error);
            });


    }

    function handleChangeInstitute(e){
        SetInst(e.target.value)
        // SetInstitute(e.target.value)

        var i = ''
        var batch = ''
        if(e.target.value === 'PUBMED'){
            i = 'pubmed'

        }
        else{
            i = 'reports'
        }

        // SetUse(e.target.value)
        var opt_batches = []
        if(i === 'pubmed'){
            axios.get('http://0.0.0.0:8000/get_PUBMED_batch_list', {params: {usecase: UseCase}}).then(response => {
                SetBatchList(response.data['batch_list']);
                opt_batches = response.data['batch_list']
                var b = 1
                if (opt_batches.length > 0){
                    b = opt_batches[0]
                }
                axios.post("http://0.0.0.0:8000/new_credentials", {
                    usecase: UseCase, language: Language, institute: e.target.value, annotation: Annotation,report_type: i,batch:b
                })
                    .then(function (response) {
                        SetInstitute(e.target.value)
                        SetUpdateMenu(true)
                        SetReportType(i)
                        SetBatch(b)
                        SetBatchNumber(b)



                    })
                    .catch(function (error) {

                        console.log('ERROR', error);
                    });
            })
        }
        else{
            axios.get('http://0.0.0.0:8000/get_batch_list', {params: {usecase: UseCase}}).then(response => {
                SetBatchList(response.data['batch_list']);
                opt_batches = response.data['batch_list']
                var b = 1
                if (opt_batches.length > 0){
                    b = opt_batches[0]
                }
                axios.post("http://0.0.0.0:8000/new_credentials", {
                    usecase: UseCase, language: Language, institute: e.target.value, annotation: Annotation,report_type: i,batch:b
                })
                    .then(function (response) {
                        SetInstitute(e.target.value)
                        SetUpdateMenu(true)
                        SetReportType(i)
                        SetBatch(b)
                        SetBatchNumber(b)

                    })
                    .catch(function (error) {
                        console.log('ERROR', error);
                    });
            })
        }



    }



    function handleChangeUseCase(e){
        SetUse(e.target.value)
        var opt_batches = []
        if(ReportType === 'pubmed'){
            axios.get('http://0.0.0.0:8000/get_PUBMED_batch_list', {params: {usecase: e.target.value}}).then(response => {
                SetBatchList(response.data['batch_list']);
                opt_batches = response.data['batch_list']
                var b = 1
                if (opt_batches.length > 0){
                    b = opt_batches[0]
                }
                axios.post("http://0.0.0.0:8000/new_credentials", {
                    usecase: e.target.value, language: Language, institute: Institute, annotation: Annotation,report_type: ReportType,batch:b
                })
                    .then(function (response) {
                        console.log('usecase cambio',e.target.value)
                        SetUseCase(e.target.value)
                        SetUpdateMenu(true)
                        SetBatch(b)
                        SetBatchNumber(b)

                    })
                    .catch(function (error) {
                        console.log('ERROR', error);
                    });
            })
        }
        else{
            axios.get('http://0.0.0.0:8000/get_batch_list', {params: {usecase: e.target.value}}).then(response => {
                SetBatchList(response.data['batch_list']);
                opt_batches = response.data['batch_list']
                var b = 1
                if (opt_batches.length > 0){
                    b = opt_batches[0]
                }
                axios.post("http://0.0.0.0:8000/new_credentials", {
                    usecase: e.target.value, language: Language, institute: Institute, annotation: Annotation,report_type: ReportType,batch:b
                })
                    .then(function (response) {
                        console.log('usecase cambio',e.target.value)
                        SetUseCase(e.target.value)
                        SetUpdateMenu(true)
                        SetBatch(opt_batches[0])
                        SetBatchNumber(opt_batches[0])

                    })
                    .catch(function (error) {
                        console.log('ERROR', error);
                    });
            })
        }

    }

    function handleChangeBatch(e){
        SetBatch(e.target.value)
        axios.post("http://0.0.0.0:8000/new_credentials", {
            usecase: UseCase, language: Language, institute: Institute, annotation: Annotation,report_type: ReportType,batch:e.target.value
        })
            .then(function (response) {
                SetBatchNumber(e.target.value)
                SetUpdateMenu(true)

            })
            .catch(function (error) {
                console.log('ERROR', error);
            });


    }


    return(
        <div className='selection_menu'>
            <Row>
                <Col md={1}>
                    <span> <button className='menuButton' onClick={(e)=>handleBar(e)}><FontAwesomeIcon icon={faBars} size='2x' /></button></span>

                </Col>

                <Col md={8} style={{'text-align':'center'}}>
                    <div>
                        <span className='configuration' style={{'font-weight':'bold'}}>Configuration:</span>

                        <span className='configuration'><FontAwesomeIcon icon={faMicroscope} /></span>&nbsp;
                        {UseCaseList.length > 0 && Use !== '' &&
                        <select style={{'vertical-align':'bottom','font-size':'0.8rem'}} className='select_class'
                                value = {Use}
                                onChange={(e)=>handleChangeUseCase(e)}>
                            {UseCaseList.map(use=>
                                <option value = {use}>{use}</option>
                            )}
                        </select>}
                        {BatchList.length > 1 && Use !== '' && Batch !== '' && <span>
                            <span className='configuration'><FontAwesomeIcon icon={faListOl} /></span>&nbsp;
                            <select style={{'vertical-align':'bottom','font-size':'0.8rem'}} className='select_class'
                                    value = {Batch}
                                    onChange={(e)=>handleChangeBatch(e)}>
                                {BatchList.map(use=>
                                    <option value = {use}>{use}</option>
                                )}
                            </select>
                        </span>
                        }

                        {/*<span className='configuration'><FontAwesomeIcon icon={faLanguage} /> <span>{UseCase}</span></span>*/}
                        {/*<span className='configuration'><FontAwesomeIcon icon={faLanguage} /> <span>{Language}</span></span>*/}
                        {/*<span className='configuration'><FontAwesomeIcon icon={faHospital} /> <span>{Institute}</span></span>*/}

                        <span className='configuration'><FontAwesomeIcon icon={faLanguage} />&nbsp;
                            {LanguageList.length > 0 && Language !== '' && Lang !== '' && <select style={{'vertical-align':'bottom','font-size':'0.8rem'}} className='select_class'
                                                                                   value = {Lang}
                                                                                   onChange={(e)=>handleChangeLanguage(e)}>
                                {LanguageList.map(lang=>
                                    <option value = {lang}>{lang}</option>
                                )}
                            </select>}</span>
                        <span className='configuration'><FontAwesomeIcon icon={faHospital} />&nbsp;
                            {InstituteList.length > 0 && Institute !== '' && Inst !== '' &&
                            <select style={{'vertical-align':'bottom','font-size':'0.8rem'}} className='select_class'
                                    value = {Inst}
                                    onChange={(e)=>handleChangeInstitute(e)}>
                                {InstituteList.map(inst=>
                                    <option value = {inst}>{inst}</option>
                                )}
                            </select>}</span>
                        <span className='configuration'><FontAwesomeIcon icon={faRobot} />&nbsp;
                            <span>{Annotation}</span></span>

                        <span className='configuration_btn '> <Button id='conf' onClick={(e)=>handleChange(e)} style={{'padding':'0','font-size':'10px','height':'25px','width':'76px'}} variant='success'> <FontAwesomeIcon icon={faCogs} /> Change</Button></span>
                        <span > <Button id='conf' onClick={(e)=>handleChangeDownload(e)} style={{'padding':'0','font-size':'10px','height':'25px','width':'76px'}} variant='info'> <FontAwesomeIcon icon={faDownload} /> Download</Button></span>
                        {ShowModal ? <OptionsModal show={ShowModal}/> : <div></div>}
                        {ShowModalDownload ? <DownloadGTUser show={ShowModalDownload}/> : <div></div>}
                    </div>

                </Col>
                <Col md={3} style={{'text-align':'right'}}>
                    <span className='userInfo'><span > {Username} </span><FontAwesomeIcon icon={faUser} size='2x'/> <a  href="http://0.0.0.0:8000/logout" className="badge badge-secondary" >Logout <FontAwesomeIcon icon={faSignOutAlt}/></a></span>

                </Col>

            </Row>
        </div>








    );




}
export default SelectMenu