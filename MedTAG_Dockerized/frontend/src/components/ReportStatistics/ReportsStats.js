import '../../App.css';
import {AppContext} from '../../App';
import React, {useState, useEffect, useContext, createContext} from "react";
import 'bootstrap/dist/css/bootstrap.min.css';
import 'react-bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'react-bootstrap';
import TableToShow from "./TableToShow";
import {Container,Row,Col} from "react-bootstrap";
import '../General/first_row.css';


import "react-circular-progressbar/dist/styles.css";

import SelectMenu from "../SelectMenu/SelectMenu";
import SideBar from "../General/SideBar";
import axios from "axios";
import Spinner from "react-bootstrap/Spinner";
import Form from "react-bootstrap/Form";
import { faSlidersH,faRobot,faStickyNote, faMicroscope,faTimesCircle,faLanguage,faLocationArrow,faCogs, faHospital } from '@fortawesome/free-solid-svg-icons';
import Button from "react-bootstrap/Button";

import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";


function ReportsStats() {


    const { selectedLanguage,selectedInstitute,selectedUse,showbar,username,admin,usecaseList,reports,languageList,instituteList } = useContext(AppContext);
    const [hiddenColumns,sethiddenColumns]  = useState([])
    const [UseCaseList,SetUseCaseList] = usecaseList;
    const [LanguageList,SetLanguageList] = languageList;
    const [InstituteList,SetInstituteList] = instituteList;
    const [Aux,SetAux] = useState(false)
    const [ShowBar,SetShowBar] = showbar;
    const [Username,SetUsername] = username;
    const [Reports,SetReports] = reports;
    // const [ShowStats,SetShowStats] = useState(new Array(usecaseList.length+1).fill(false))
    const [StatsArray,SetStatsArray] = useState(false)
    const [StatsArrayPercent,SetStatsArrayPercent] = useState(false)
    const [Options_uses,SetOptions_uses] = useState([])
    // const [Options_order,SetOptions_order] = useState([{value:'ID',label:'ID'},{value:'DESC',label:'Number of annotations (DESC)'},{value:'ASC',label:'Number of annotations (ASC)'}])
    const [Options_order,SetOptions_order] = useState([])
    const [Actions,SetActions] = useState(['Labels','Mentions','Concepts','Linking'])
    const [Use,SetUse] = useState('')
    const [Order,SetOrder] = useState('')
    const [Cols,SetCols] = useState([])
    const [data,setdata] = useState([])
    const [HiddenCols,SetHiddenCols] = useState([])
    const [rows, setRows] = useState([])
    // const [rows, setRows] = useState([]);
    const [selectedRows, setSelectedRows] = useState([]);
    const [deletedRows, setDeletedRows] = useState([]);
    const [purgeMode, setPurgeMode] = useState(true);
    const [defaultColumnWidths,setdefaultColumnWidths] = useState([]);
    const [Admin, SetAdmin] = admin;
    const [SelectedLang,SetSelectedLang] = selectedLanguage
    const [SelectedInstitute,SetSelectedInstitute] =selectedInstitute
    const [SelectedUse,SetSelectedUse] = selectedUse
    const [Committed,SetCommitted] = useState(false)
    const [Loading,SetLoading] = useState(false)
    const [Empty,SetEmpty] = useState(false)

    // useEffect(()=>{
    //     var opt = []
    //     axios.get("http://0.0.0.0:8000/get_usecase_inst_lang").then(response => {
    //         SetUseCaseList(response.data['usecase']);
    //         SetLanguageList(response.data['language']);
    //         SetInstituteList(response.data['institute']);
    //         response.data['usecase'].map((use,i)=>{
    //             opt.push(<option value={use}>{use}</option>)
    //             // opt.push({value:use,label:use})
    //         })
    //         SetOptions_uses(opt)
    //
    //     })
    //         .catch(function(error){
    //             console.log('error: ',error)
    //         })
    //
    //     var opt_ord = []
    //     var wd_col = []
    //     opt_ord.push(<option value='ID'>ID</option>)
    //     opt_ord.push(<option value='ASC'>Number of annotations (ASC)</option>)
    //     opt_ord.push(<option value='DESC'>Number of annotations (DESC)</option>)
    //     SetOptions_order(opt_ord)
    //     var username = window.username
    //     // console.log('username', username)
    //     SetUsername(username)
    //     var arr_data = []
    //     var col = []
    //     var hid_cols = []
    //
    //     // col.push({name:'delete',width:100})
    //     // col.push({name:'download'})
    //     col.push({name:'id_report',title:'id_report'})
    //     wd_col.push({columnName:'id_report',width:150})
    //     col.push({name:'language',title:'language'})
    //     wd_col.push({columnName:'language',width:150})
    //     col.push({name:'batch',title:'batch'})
    //     wd_col.push({columnName:'batch',width:100})
    //     col.push({name:'usecase',title:'usecase'})
    //     wd_col.push({columnName:'usecase',width:150})
    //
    //     col.push({name:'institute',title:'institute'})
    //     wd_col.push({columnName:'institute',width:150})
    //
    //
    //     col.push({name:'annotations',title:'annotations'})
    //     wd_col.push({columnName:'annotations',width:150,align:'right'})
    //
    //     // col.push({name:'labels',title:'labels'})
    //     // wd_col.push({columnName:'labels',width:150,align:'right'})
    //     // hid_cols.push('labels')
    //     //
    //     // col.push({name:'mentions',title:'mentions'})
    //     // wd_col.push({columnName:'mentions',width:150,align:'right'})
    //     // hid_cols.push('mentions')
    //     //
    //     // col.push({name:'concepts',title:'concepts'})
    //     // wd_col.push({columnName:'concepts',width:150,align:'right'})
    //     // hid_cols.push('concepts')
    //     //
    //     // col.push({name:'linking',title:'linking'})
    //     // wd_col.push({columnName:'linking',width:150,align:'right'})
    //     // hid_cols.push('linking')
    //
    //
    //     axios.get('http://0.0.0.0:8000/get_fields',{params:{all:'all'}}).then(function (response){
    //         response.data['all_fields'].map((elem,ind)=>{
    //             var nome = elem + '_0'
    //             col.push({name:nome,title:elem})
    //             wd_col.push({columnName:nome,width:200})
    //
    //             // col.push({Header:elem,accessor:elem})
    //             hid_cols.push(nome)
    //         })
    //         col.push({name:'',title:''})
    //         wd_col.push({columnName:'',width:200})
    //
    //
    //         SetCols(col)
    //         setdefaultColumnWidths(wd_col)
    //         SetHiddenCols(hid_cols)
    //     })
    //
    //     axios.get('http://0.0.0.0:8000/get_data',).then(function (response){
    //         response.data['reports'].map((elem,ind)=>{
    //             arr_data.push(
    //                 {
    //                     id:ind,annotations: elem['total'],
    //                     ...elem['report']
    //
    //                 }
    //             )
    //         })
    //         setdata(arr_data)
    //         setRows(arr_data)
    //     })
    //
    //
    //     // MODIFIED BY ORNELLA 04082021
    //     // axios.get("http://0.0.0.0:8000/get_reports", {params: {configure: 'configure'}}).then(response => {
    //     //     SetReports(response.data['report']);
    //     //
    //     // })
    //
    // },[])

    function submit_data(){
        var opt = []
        SetLoading(true)
        axios.get("http://0.0.0.0:8000/get_usecase_inst_lang").then(response => {
            SetUseCaseList(response.data['usecase']);
            SetLanguageList(response.data['language']);
            SetInstituteList(response.data['institute']);
            response.data['usecase'].map((use,i)=>{
                opt.push(<option value={use}>{use}</option>)
                // opt.push({value:use,label:use})
            })
            SetOptions_uses(opt)

        })
            .catch(function(error){
                console.log('error: ',error)
            })

        var opt_ord = []
        var wd_col = []
        opt_ord.push(<option value='ID'>ID</option>)
        opt_ord.push(<option value='ASC'>Number of annotations (ASC)</option>)
        opt_ord.push(<option value='DESC'>Number of annotations (DESC)</option>)
        SetOptions_order(opt_ord)
        var username = window.username
        // console.log('username', username)
        SetUsername(username)
        var arr_data = []
        var col = []
        var hid_cols = []

        // col.push({name:'delete',width:100})
        // col.push({name:'download'})
        col.push({name:'id_report',title:'id_report'})
        wd_col.push({columnName:'id_report',width:150})
        col.push({name:'id_report_not_hashed',title:'id_report_not_hashed'})
        wd_col.push({columnName:'id_report_not_hashed',width:150})
        col.push({name:'language',title:'language'})
        wd_col.push({columnName:'language',width:150})
        col.push({name:'batch',title:'batch'})
        wd_col.push({columnName:'batch',width:100})
        col.push({name:'usecase',title:'usecase'})
        wd_col.push({columnName:'usecase',width:150})

        col.push({name:'institute',title:'institute'})
        wd_col.push({columnName:'institute',width:150})


        col.push({name:'annotations',title:'annotations'})
        wd_col.push({columnName:'annotations',width:150,align:'right'})
        axios.get('http://0.0.0.0:8000/get_fields',{params:{all:'all'}}).then(function (response){
            response.data['all_fields'].map((elem,ind)=>{
                var nome = elem + '_0'
                col.push({name:nome,title:elem})
                wd_col.push({columnName:nome,width:200})

                // col.push({Header:elem,accessor:elem})
                hid_cols.push(nome)
            })
            col.push({name:'',title:''})
            wd_col.push({columnName:'',width:200})


            SetCols(col)
            setdefaultColumnWidths(wd_col)
            SetHiddenCols(hid_cols)
        })
        axios.get('http://0.0.0.0:8000/get_data',{params:{language:SelectedLang,usecase:SelectedUse,institute: SelectedInstitute}}).then(function (response){
            if(response.data['reports'].length > 0){
                response.data['reports'].map((elem,ind)=>{
                    arr_data.push(
                        {
                            id:ind,annotations: elem['total'],
                            ...elem['report']

                        }
                    )
                    SetCommitted(true)
                })
                setdata(arr_data)
                setRows(arr_data)
            }
            else{
                SetEmpty(true)
            }

            SetLoading(false)


        })
    }


    // useEffect(()=>{
    //     console.log('righe',rows)
    // },[rows])

    function handleChangeLangSelected(option){
        SetEmpty(false)
        console.log('selected_lang',SelectedLang)
        SetSelectedLang(option.target.value)
    }

    function handleChangeInstSelected(option){
        SetEmpty(false)
        console.log('selected_lang',SelectedLang)
        SetSelectedInstitute(option.target.value)
    }

    function handleChangeUseSelected(option){
        SetEmpty(false)
        console.log('selected_lang',SelectedUse)
        SetSelectedUse(option.target.value)
    }

    return (
        <div className="App">
            {(Username !== Admin && Username !== 'Test') ?
                <div><h1>FORBIDDEN</h1>
                    <div>
                        <a href="http://0.0.0.0:8000/index">
                            Back
                        </a>
                    </div>
                </div>:
                <div>
                    <Container fluid>

                        {ShowBar && <SideBar />}
                        {(InstituteList.length >= 0  && LanguageList.length >=0 && UseCaseList.length >= 0) ? <div><SelectMenu />
                            <div><hr/></div>


                            <div style={{'text-align':'center'}}><h2>REPORTS' OVERVIEW</h2></div>
                            <div style={{'margin-bottom':'2vh','text-align':'center'}}>In this section you can check how many reports have been annotated so far for each use case. You can also delete one or more reports if you want.</div>

                            {/*{(Cols.length>0 && defaultColumnWidths.length>0 && rows.length>0 && HiddenCols.length > 0) ? <div>*/}
                            {/*/!*{(rows.length>0) ? <div>*!/*/}

                            {/*<div><TableToShow columns={Cols} righe={rows} hiddenColumns={HiddenCols} default_width={defaultColumnWidths}/></div>*/}
                            {/*</div> : <div className='spinnerDiv'><Spinner animation="border" role="status"/></div>}*/}

                            {(Committed === true) ? <>
                                {Committed === true && <div style={{'text-align':'center'}}><b>Use case : <i style={{color:'royalblue'}}>{SelectedUse}</i></b> - <b>Language : <i style={{color:'royalblue'}}>{SelectedLang}</i></b> - <b>Institute : <i style={{color:'royalblue'}}>{SelectedInstitute}</i></b>
                                    &nbsp;&nbsp;<span><Button onClick={(e)=>{SetCommitted(false);setRows([]);setdata([]);SetSelectedInstitute(''); SetSelectedLang('');SetSelectedUse('')}} size = 'sm' variant = 'outline-primary'><FontAwesomeIcon icon={faSlidersH}  /></Button></span></div>}
                                {(Cols.length>0 && defaultColumnWidths.length>0 && rows.length>0 && HiddenCols.length > 0) ? <div>
                                    {/*{(rows.length>0) ? <div>*/}

                                    <div><TableToShow columns={Cols} righe={rows} hiddenColumns={HiddenCols} default_width={defaultColumnWidths}/></div>
                                </div> : <div className='spinnerDiv'><Spinner animation="border" role="status"/></div>}


                            </> :<>

                                {Loading ? <div className='spinnerDiv'><Spinner animation="border" role="status"/></div> :
                                    <div style={{'text-align':'center'}}>
                                        {Empty && <div><b>No reports found for this configuration</b></div>}
                                        <><div style={{'text-align':'center',marginTop:'2%'}} >Select the use case</div>
                                            <Row><Col md={4}></Col>
                                                <Col md={4}><Form.Control style={{'text-align':'center'}} value={SelectedUse} as="select" onChange={(option)=>handleChangeUseSelected(option)} placeholder="Select a use case...">
                                                    <option value="">Select a usecase</option>
                                                    {UseCaseList.map((use)=>
                                                        <option value={use}>{use}</option>
                                                    )}
                                                </Form.Control>
                                                </Col><Col md={4}></Col></Row></>
                                        <><div style={{'text-align':'center',marginTop:'2%'}} >Select the language</div>
                                            <Row><Col md={4}></Col>
                                                <Col md={4}><Form.Control style={{'text-align':'center'}} value={SelectedLang} as="select" onChange={(option)=>handleChangeLangSelected(option)} placeholder="Select a language...">
                                                    <option value="">Select a language</option>
                                                    {LanguageList.map((language)=>
                                                        <option value={language}>{language}</option>
                                                    )}
                                                </Form.Control>
                                                </Col><Col md={4}></Col></Row></>

                                        <><div style={{'text-align':'center',marginTop:'2%'}} >Select the institute</div>
                                            <Row><Col md={4}></Col>
                                                <Col md={4}><Form.Control style={{'text-align':'center'}}  value={SelectedInstitute} as="select" onChange={(option)=>handleChangeInstSelected(option)} placeholder="Select a language...">
                                                    <option value="">Select an institute</option>
                                                    {InstituteList.map((inst)=>
                                                        <option value={inst}>{inst}</option>
                                                    )}
                                                </Form.Control>
                                                </Col><Col md={4}></Col>
                                            </Row></>
                                        <Button  style={{'text-align':'center',marginTop:'2%'}} size='sm' variant='primary' onClick={submit_data} >Confirm</Button>
                                    </div>}


                            </>





                            }






                        </div> : <div className='spinnerDiv'><Spinner animation="border" role="status"/></div>}
                    </Container>
                </div>}

        </div>



    );
}


export default ReportsStats;
