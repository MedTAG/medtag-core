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
import '../General/first_row.css';
import ProgressBar from 'react-bootstrap/ProgressBar'
import {
    CircularProgressbar,ProgressProvider,
    CircularProgressbarWithChildren,
    buildStyles
} from "react-circular-progressbar";
import "react-circular-progressbar/dist/styles.css";

// import { easeQuadInOut } from "d3-ease";
// import AnimatedProgressProvider from "./AnimatedProgressProvider";
import ChangingProgressProvider from "../SideComponents/ChangingProgressProvider";

import SelectMenu from "../SelectMenu/SelectMenu";

import SideBar from "../General/SideBar";
import ProgressiveComponent from "../SideComponents/ProgressiveComponent";
import axios from "axios";
import Spinner from "react-bootstrap/Spinner";
import Form from "react-bootstrap/Form";
import {backdropClasses, Collapse} from "@mui/material";
import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";
import {faChevronDown, faChevronUp, faSlidersH} from "@fortawesome/free-solid-svg-icons";
import TableToShow from "../ReportStatistics/TableToShow";
import ProgTable from "./ProgTable";
import Buttons from "../General/Buttons";

function ProgressiveAnnotation() {
    const { showbar,username,usecaseList,usecase,annotation,usersList,language,batchNumber,institute,reports,languageList,instituteList } = useContext(AppContext);
    const [Annotation,SetAnnotation] = annotation;
    const [UseCaseList,SetUseCaseList] = usecaseList;
    const [LanguageList,SetLanguageList] = languageList;
    const [InstituteList,SetInstituteList] = instituteList;
    const [Aux,SetAux] = useState(false)
    const [ShowBar,SetShowBar] = showbar;
    const [Username,SetUsername] = username;
    const [Reports,SetReports] = reports;
    const [SelectedMode,SetSelectedMode] = useState('')
    // const [ShowStats,SetShowStats] = useState(new Array(usecaseList.length+1).fill(false))
    const [StatsArray,SetStatsArray] = useState(false)
    const [StatsArrayPubMed,SetStatsArrayPubMed] = useState(false)
    const [StatsArrayPercent,SetStatsArrayPercent] = useState(false)
    const [StatsArrayPercentPubMed,SetStatsArrayPercentPubMed] = useState(false)
    const [Actions,SetActions] = useState(['labels','mentions','concepts','concept-mention'])
    const [SelectedLang,SetSelectedLang] = useState('')
    const [SelectedUse,SetSelectedUse] = useState('')
    const [SelectedBatch,SetSelectedBatch] = useState('')
    const [SelectedInstitute,SetSelectedInstitute] = useState('')
    const [StatsAuto,SetStatsAuto] = useState(0)
    const [ChosenStats,SetChosenStats] = useState('')
    const [UsesExtraxcted,SetUsesExtracted] = useState([])
    const [Language,SetLanguage] = language;
    const [Institute,SetInstitute] = institute;
    const [useCase,SetUseCase] = usecase
    const [BatchNumber,SetBatchNumber] = batchNumber;
    const [BatchList,SetBatchList] = useState([]);
    const [IncremenetListVals,SetIncremenetListVals] = useState([]);
    const [IncrementList,SetIncrementList] = useState([1]);
    const [Robot,SetRobot] = useState(false);
    const [UsersList,SetUsersList] = usersList
    const [MaxVal,SetMaxVal] = useState([]);
    const [Colors,SetColors] = useState(['red','blue','green','orange']);
    const [ReportTotal,SetReportTotal] = useState(0)
    const [Cols,SetCols] = useState([])
    const [ColsNoAnno,SetColsNoAnno] = useState([])
    const [data,setdata] = useState([])
    const [HiddenCols,SetHiddenCols] = useState([])
    const [rows, setRows] = useState(false)
    const [rowsNoAnno, setRowsNoAnno] = useState(false)
    const [defaultColumnWidths,setdefaultColumnWidths] = useState([]);
    const [defaultColumnWidthsNoAnno,setdefaultColumnWidthsNoAnno] = useState([]);
    const [defaultColumnGroup,setdefaultColumGroup] = useState([]);
    const [Committed,SetCommitted] = useState(false)
    const [Loading,SetLoading] = useState(false)
    const [Empty,SetEmpty] = useState(false)
    const [NoAnno,SetNoAnno] = useState(false)

    useEffect(()=>{
        axios.get("http://examode.dei.unipd.it/exatag/get_usecase_inst_lang").then(response => {
            SetUseCaseList(response.data['usecase']);
            SetUsesExtracted(response.data['usecase']);
            SetLanguageList(response.data['language']);
            SetInstituteList(response.data['institute']);

        })
            .catch(function(error){
                console.log('error: ',error)
            })
        axios.get('http://examode.dei.unipd.it/exatag/get_batch_list').then(response=>SetBatchList(response.data['batch_list']))

        if(BatchNumber !== '' && Language !== '' && useCase !== '' && Institute !== ''){
            SetSelectedBatch(BatchNumber)
            SetSelectedLang(Language)
            SetSelectedUse(useCase)
            SetSelectedInstitute(Institute)
        }


    },[])

    useEffect(()=>{
        if(BatchNumber !== '' && Language !== '' && useCase !== '' && Institute !== ''){
            SetSelectedBatch(BatchNumber)
            SetSelectedLang(Language)
            SetSelectedUse(useCase)
            SetSelectedInstitute(Institute)
        }
    },[BatchNumber,useCase,Language,Institute])

    function submit_data_prog(){
        var opt = []
        SetLoading(true)
        var username = window.username
        // console.log('username', username)
        SetUsername(username)
        var arr_data = []
        var miss_data = []
        var col = []
        var no_anno = []
        var no_anno_w = []
        var wd_col = []
        var g = []
        // col.push({name:'delete',width:150})
        // col.push({name:'download'})
        col.push({name:'usecase',title:'usecase'})
        no_anno.push({name:'usecase',title:'usecase'})
        wd_col.push({columnName:'usecase',width:150})
        no_anno_w.push({columnName:'usecase',width:150})

        col.push({name:'institute',title:'institute'})
        no_anno.push({name:'institute',title:'institute'})
        wd_col.push({columnName:'institute',width:150})
        no_anno_w.push({columnName:'institute',width:150})

        col.push({name:'language',title:'language'})
        no_anno.push({name:'language',title:'language'})
        wd_col.push({columnName:'language',width:150})
        no_anno_w.push({columnName:'language',width:150})

        col.push({name:'batch',title:'batch'})
        no_anno.push({name:'batch',title:'batch'})
        wd_col.push({columnName:'batch',width:100})
        no_anno_w.push({columnName:'batch',width:100})

        col.push({name:'mode',title:'annotation mode'})
        no_anno.push({name:'mode',title:'annotation mode'})
        wd_col.push({columnName:'mode',width:150})
        no_anno_w.push({columnName:'mode',width:150})

        col.push({name:'annotations',title:'Number of annotations'})
        wd_col.push({columnName:'annotations',width:180})
        col.push({name:'number_of_reports',title:'Annotated reports'})
        no_anno.push({name:'number_of_reports',title:'Not annotated reports'})
        wd_col.push({columnName:'number_of_reports',width:180})
        no_anno_w.push({columnName:'number_of_reports',width:200})

        col.push({name:'percentage',title:'% annotated reports'})
        no_anno.push({name:'percentage',title:'% NOT annotated reports'})
        wd_col.push({columnName:'percentage',width:180})
        no_anno_w.push({columnName:'percentage',width:200})

        col.push({name:'',title:''})
        no_anno.push({name:'',title:''})
        wd_col.push({columnName:'',width:150})
        no_anno_w.push({columnName:'',width:150})
        SetCols(col)
        SetColsNoAnno(no_anno)
        setdefaultColumnWidthsNoAnno(no_anno_w)
        setdefaultColumnWidths(wd_col)
        setdefaultColumGroup(g)


        axios.get('http://examode.dei.unipd.it/exatag/get_prog_data',{params:{language:SelectedLang,usecase:SelectedUse,institute: SelectedInstitute,batch:SelectedBatch}}).then(function (response){
            SetReportTotal(response.data['total'])
            if(response.data['total'] > 0){
                response.data['reports'].map((elem,ind)=>{
                    arr_data.push(
                        {
                            id:ind,annotations: elem['total'],number_of_reports:elem['number_of_reports'],percentage: elem['percentage'],
                            ...elem['report']

                        }
                    )
                    SetCommitted(true)
                })
                response.data['missing_reports'].map((elem,ind)=>{
                    miss_data.push(
                        {
                            id:ind,number_of_reports:elem['number_of_reports'],percentage: elem['percentage'],
                            ...elem['report']

                        }
                    )
                    SetCommitted(true)
                })
                // setdata(arr_data)
                setRows(arr_data)
                setRowsNoAnno(miss_data)
            }
            else{
                SetEmpty(true)
            }

            SetLoading(false)

        })

    }




    function handleChangeLangSelected(option){
        SetEmpty(false)
        SetNoAnno(false)
        console.log('selected_lang',SelectedLang)
        SetSelectedLang(option.target.value)
    }

    function handleChangeInstSelected(option){
        SetEmpty(false)
        SetNoAnno(false)
        console.log('selected_lang',SelectedLang)
        SetSelectedInstitute(option.target.value)
    }

    function handleChangeUseSelected(option){
        SetEmpty(false)
        SetNoAnno(false)

        console.log('selected_lang',SelectedUse)
        SetSelectedUse(option.target.value)
    }
    function handleChangeBatchSelected(option){
        SetEmpty(false)
        SetNoAnno(false)

        console.log('selected_lang',SelectedBatch)
        SetSelectedBatch(option.target.value)
    }




    return (
        <div className="App">
            {Username === '' ?
                <div><h1>FORBIDDEN</h1>
                    <div>
                        <a href="http://examode.dei.unipd.it/exatag/index">
                            Back
                        </a>
                    </div>
                </div>:
                <div>
                    <Container fluid>

                        {ShowBar && <SideBar />}
                        {(InstituteList.length >= 0  && LanguageList.length >=0 && UseCaseList.length >= 0) ? <div><SelectMenu />
                            <div><hr/></div>


                            <div style={{'text-align':'center'}}><h2>ANNOTATION PROGRESS</h2></div>
                                <div style={{textAlign:'center'}}>In this section you can check how many reports have been annotated so far for the required configuration.</div>
                            <div  style={{'margin-bottom':'2vh'}}>
                                Given a number of annotations (<i>Number of Annotations</i> column) the number of reports having exactly that number ground-truths (<i>Annotated reports</i> column) and the corresponding percentage over the total of reports for the required configuration (<i>% annotated reports</i> column) are provided.
                                The annotated reports ids and the users who annotated them are downloadable in csv and json formats respectively.
                                <br/>
                                It is provided also an overview of the number of reports without annotations. The reports ids which have not annotations are downloadable in csv and json formats respectively.

                            </div>



                            {(Committed === true) ? <>
                                {Committed === true && <div style={{'text-align':'center'}}><b>Use case : <i style={{color:'royalblue'}}>{SelectedUse}</i></b> - <b>Language : <i style={{color:'royalblue'}}>{SelectedLang}</i></b> - <b>Institute : <i style={{color:'royalblue'}}>{SelectedInstitute}</i></b> - <b>Batch : <i style={{color:'royalblue'}}>{SelectedBatch}</i></b>
                                    &nbsp;&nbsp;<span><Button onClick={(e)=>{setRows(false);setRowsNoAnno(false);SetCommitted(false);setdata([]);SetSelectedInstitute(''); SetSelectedBatch('');SetSelectedLang('');SetSelectedUse('')}} size = 'sm' variant = 'outline-primary'><FontAwesomeIcon icon={faSlidersH}  /></Button></span></div>}
                                {rows.length === 0 && <div style={{marginBottom:'2%',marginTop:'2%'}}>This configuration has not been annotated yet.</div>}
                                {(Cols.length>0 && defaultColumnWidths.length>0 && rows.length >= 0 && ReportTotal > 0) ? <div>
                                    <div style={{marginBottom:'2%',marginTop:'2%'}}>The total number of reports for the required configuration is: <b>{ReportTotal}</b></div>
                                    <div><ProgTable columns={Cols} righe={rows} default_width={defaultColumnWidths}/></div>
                                    <div>Check how many reports have <b>0</b> annotations <Button variant='primary' size='sm' onClick={()=>SetNoAnno(prev=>!prev)}>{NoAnno === false ? <>Show</> : <>Hide</>}</Button></div>
                                    {NoAnno && rowsNoAnno && <div><ProgTable columns={ColsNoAnno} righe={rowsNoAnno} default_width={defaultColumnWidthsNoAnno}/></div>}

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
                                        <><div style={{'text-align':'center',marginTop:'2%'}} >Select the batch</div>
                                            <Row><Col md={4}></Col>
                                                <Col md={4}><Form.Control style={{'text-align':'center'}}  value={SelectedBatch} as="select" onChange={(option)=>handleChangeBatchSelected(option)} placeholder="Select a language...">
                                                    <option value="">Select a batch</option>
                                                    {BatchList.map((b)=>
                                                        <option value={b}>{b}</option>
                                                    )}
                                                </Form.Control>
                                                </Col><Col md={4}></Col>
                                            </Row></>
                                        {SelectedLang !== '' && SelectedUse !== '' && SelectedInstitute !== '' && SelectedBatch !== '' && <Button  style={{'text-align':'center',marginTop:'2%'}} size='sm' variant='primary' onClick={submit_data_prog} >Confirm</Button>}
                                    </div>}


                            </>





                            }






                        </div> : <div className='spinnerDiv'><Spinner animation="border" role="status"/></div>}
                    </Container>
                </div>}

        </div>







    );
}



export default ProgressiveAnnotation;

