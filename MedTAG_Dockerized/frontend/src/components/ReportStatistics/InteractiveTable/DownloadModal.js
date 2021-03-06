import React, {createContext, useContext, useEffect, useState} from 'react';
import PropTypes from 'prop-types';
import {confirmable, createConfirmation} from 'react-confirm';
import Modal from "react-bootstrap/Modal";
import Button from "react-bootstrap/Button";
import Form from "react-bootstrap/Form";
import './reportText.css'
import {
    faChartBar,faProjectDiagram,
    faRobot,
    faFileAlt
} from '@fortawesome/free-solid-svg-icons';
import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";
import {TableToShowContext} from "../TableToShow";
import 'bootstrap/dist/css/bootstrap.min.css';
import axios from "axios";
// import './selectMenu.css'

function DownloadModal(props){
    const { showmodaldownloadtable,selec,rowstodownload } = useContext(TableToShowContext);

    const [ShowModalDownload, SetShowModalDownload] = showmodaldownloadtable;
    const [RowsToDownload,SetRowsToDownload] = rowstodownload

    const [Act,SetAct] = useState('')
    const [Anno,SetAnno] = useState('')
    const [Format,SetFormat] = useState('')
    const [ShowNotDownload,SetShowNotDownload] = useState(false)
    const [ShowError,SetShowError] = useState(false)
    const handleClose = () => SetShowModalDownload(false);
    const [Options_gt_type, SetOptions_gt_type] = useState([])

    const [Options_actions, Setoptions_actions] = useState([])
    const [Options_reduced, Setoptions_reduced] = useState([])
    const [Options_format, Setoptions_format] = useState([])
    const [Options_format_red, Setoptions_format_red] = useState([])
    const [ShowFormat,SetShowFormat] = useState(false)
    const [BiocError, SetBiocError] = useState(false)
    const [Options_annotation, SetOptions_annotation] = useState([])
    const [selection, setSelection] = selec

    const [GTType,SetGTType] = useState('')
    var FileDownload = require('js-file-download');

    useEffect(()=>{

        console.log('SONO DENTRO')
        var options_actions = [{value:'labels',label:'Labels'},{value:'concepts',label:'Concepts'},{value:'mentions',label:'Mentions'},{value:'concept-mention',label:'Linking'}]
        var options_actions_red = [{value:'mentions',label:'Mentions'},{value:'concept-mention',label:'Linking'}]
        Setoptions_actions(options_actions)
        Setoptions_reduced(options_actions_red)

        var options_form=[{value:'json',label:'json'},{value:'csv',label:'csv'},{value:'biocxml',label:'BioC XML'},{value:'biocjson',label:'BioC JSON'}]
        var options_form_red=[{value:'json',label:'json'},{value:'csv',label:'csv'}]
        Setoptions_format(options_form)
        Setoptions_format_red(options_form_red)
        // var options_gt_type=[{value:'users_only',label:'All the users\' ground-truths for the required report(s)'},{value:'majority',label:'The ground-truth based on majority vote for the required report(s)'},{value:'All',label:'All'}]
        var options_gt_type=[{value:'users_only',label:'All the users\' ground-truths for the required report(s)'},{value:'majority',label:'The ground-truth based on majority vote for the required report(s)'}]
        SetOptions_gt_type(options_gt_type)
        var arr = []
        arr.push({value:'Manual',label:'Manual'})
        arr.push({value:'Automatic',label:'Automatic'})
        arr.push({value:'All',label:'All'})
        SetOptions_annotation(arr)


    },[])

    function onSave(e){
        e.preventDefault()
        console.log('FORMAT',Format)
        console.log('ACTION',Act)
        // console.log(Ins)
        // console.log(Lang)
        SetShowError(false)
        SetBiocError(false)
        SetShowNotDownload(false)
        SetShowFormat(false)
        if(Format === '' || Act === '' || GTType === '' || Anno === '' ){
            SetShowFormat(true)
        }
        else if((Format === 'biocxml' || Format === 'biocjson') &&  (Act === 'labels' || Act === 'concepts')){
            SetBiocError(true)
        }
        else if(Format !== '' && Act !== '' && GTType !== '' && Anno !== '' && RowsToDownload.length>0) {
            console.log('ROWS',RowsToDownload)
            axios.get('http://127.0.0.1:8000/get_gt_action_based',{params:{action:Act,annotation_mode:Anno}})
                .then(response=>{
                    if(response.data['count']>0){
                        axios.post('http://127.0.0.1:8000/download_for_report',
                            {
                                report_list:RowsToDownload,
                                action: Act,
                                format: Format,
                                type_gts:GTType,
                                annotation_mode:Anno
                        })
                            .then(function (response) {
                                console.log('message', response.data);

                                if (Format === 'json') {
                                    if(Act === 'concept-mention'){
                                        FileDownload(JSON.stringify(response.data), 'linking_json_ground_truth.json');

                                    }else{
                                        FileDownload(JSON.stringify(response.data), Act.toString() + '_json_ground_truth.json');
                                    }
                                    SetShowNotDownload(false)
                                    SetShowModalDownload(false)
                                    SetShowFormat(false)
                                    SetGTType('')
                                    SetAnno('')
                                    SetFormat('')
                                    SetAct('')
                                    setSelection([])

                                } else if (Format === 'csv') {
                                    if(Act === 'concept-mention'){
                                        FileDownload((response.data), 'linking_csv_ground_truth.csv');
                                    }
                                    else{
                                        FileDownload((response.data), Act.toString() + '_csv_ground_truth.csv');

                                    }
                                    SetShowNotDownload(false)
                                    SetShowModalDownload(false)
                                    SetShowFormat(false)
                                    SetGTType('')
                                    SetAnno('')
                                    SetFormat('')
                                    SetAct('')
                                    setSelection([])


                                } else if (Format === 'biocxml') {
                                    if(Act === 'concept-mention') {
                                        FileDownload((response.data), 'linking_bioc_ground_truth.xml');
                                    }
                                    else{
                                        FileDownload((response.data), 'mentions_bioc_ground_truth.xml');

                                    }
                                    SetShowNotDownload(false)
                                    SetShowModalDownload(false)
                                    SetShowFormat(false)
                                    SetGTType('')
                                    SetAnno('')
                                    SetFormat('')
                                    SetAct('')
                                    setSelection([])


                                } else if (Format === 'biocjson' ) {
                                    if(Act === 'concept-mention') {
                                        FileDownload((JSON.stringify(response.data)), 'linking_bioc_ground_truth.json');
                                    }
                                    else{
                                        FileDownload((JSON.stringify(response.data)), 'mentions_bioc_ground_truth.json');
                                    }
                                    SetShowNotDownload(false)
                                    SetShowModalDownload(false)
                                    SetShowFormat(false)
                                    SetGTType('')
                                    SetAnno('')
                                    SetFormat('')
                                    SetAct('')
                                    setSelection([])

                                }

                            })
                            .catch(function (error) {

                                console.log('error message', error);
                            });
                    }
                    else{
                        SetShowNotDownload(true)
                    }
                })

        }


    }

    function handleChangeAction(option){
        console.log(`Option selected:`, option.target.value);
        SetAct(option.target.value.toString())
    }
    function handleChangeFormat(option){
        console.log(`Option selected:`, option.target.value);
        SetFormat(option.target.value.toString())
    }
    function handleChangeMode(option){
        console.log(`Option selected:`, option.target.value);
        SetAnno(option.target.value.toString())

    }
    function handleChangeType(option){
        console.log(`Option selected:`, option.target.value);
        SetGTType(option.target.value.toString())

    }
    function onSaveKeyFiles(e,type_key){
        e.preventDefault()
        if(type_key === 'mentions'){
            axios.get('http://127.0.0.1:8000/download_key_files', {params:{type_key:'mentions'}})
                .then(function (response) {
                    console.log('message', response.data);
                    FileDownload((response.data), 'mentions.key');
                })
                .catch(function (error) {

                    console.log('error message', error);
                });
        }
        else if(type_key === 'concept-mention') {

            axios.get('http://127.0.0.1:8000/download_key_files', {params: {type_key: 'linking'}})
                .then(function (response) {
                    console.log('message', response.data);
                    FileDownload((response.data), 'linking.key');
                })
                .catch(function (error) {

                    console.log('error message', error);
                });
        }
    }

    const closeModalDownload = () => {SetShowModalDownload(false);SetRowsToDownload([])}



    return(
        <Modal
            show={ShowModalDownload && RowsToDownload.length>0}
            onHide={closeModalDownload}
            // backdrop="static"
            // keyboard={false}
        >
            <Modal.Header closeButton>
                <Modal.Title>Download the ground-truths for {RowsToDownload.length} {RowsToDownload.length === 1 ? <>report</> : <>reports</>}</Modal.Title>
            </Modal.Header>
            <Modal.Body>

                {(ShowFormat === true) && <h6>Please, fill all the required fields.</h6>}
                {ShowNotDownload === true && <h6>There are not ground-truths for the required configuration. </h6>}
                {BiocError === true && <h6>BioC is allowed only with mentions and linking. </h6>}

                <div>


                    <div>
                        <div><FontAwesomeIcon icon={faFileAlt} /> File format </div>
                        <Form.Control className='selection'  as="select" onChange={(option)=>handleChangeFormat(option)}>
                            <option value="">Select a file format...</option>
                            {Options_format.map((option)=>
                                <option value={option.value}>{option.label}</option>
                            )}
                        </Form.Control>


                        <hr/>

                        <div><FontAwesomeIcon icon={faProjectDiagram} /> Actions </div>
                        <Form.Control className='selection'  as="select" onChange={(option)=>handleChangeAction(option)} placeholder="select an annotation type...">
                            <option value="">select an annotation type...</option>
                            {Options_actions.map((option)=>
                                <option value={option.value}>{option.label}</option>
                            )}
                        </Form.Control>

                        {(Format === 'biocxml' || Format === 'biocjson') && Act === 'mentions' && <div className='selection'><a className='bioc_down' onClick={(e)=>onSaveKeyFiles(e,'mentions')}>Download BioC key file for mentions</a></div>}
                        {(Format === 'biocxml' || Format === 'biocjson') && Act === 'concept-mention' && <div className='selection'><a  className='bioc_down' onClick={(e)=>onSaveKeyFiles(e,'concept-mention')}>Download BioC key file for linking</a></div>}

                        <hr/>

                        <div><FontAwesomeIcon icon={faChartBar} /> Ground-truth type</div>
                        <Form.Control className='selection' as="select" onChange={(option)=>handleChangeType(option)} placeholder="Select a ground-truth type...">
                            <option value="">Select a type...</option>
                            {Options_gt_type.map((option)=>
                                <option value={option.value}>{option.label}</option>
                            )}
                        </Form.Control>
                        <hr/>

                        {Options_annotation.length>0 &&<div><div><FontAwesomeIcon icon={faRobot} /> Annotation mode </div>
                            <Form.Control className='selection' as="select" onChange={(option)=>handleChangeMode(option)} placeholder="Select an annotation mode...">
                                <option value="">Select an annotation mode...</option>
                                {Options_annotation.map((option)=>
                                    <option value={option.value}>{option.label}</option>
                                )}
                            </Form.Control></div>}

                        <hr/>
                    </div>
                </div>

            </Modal.Body>

            <Modal.Footer>
                <Button onClick={closeModalDownload} variant="secondary" >
                    Close
                </Button>

                <Button  onClick={(e)=>onSave(e)} variant="primary" >
                    Download
                </Button>
            </Modal.Footer>





        </Modal>


    );




}

// confirmable HOC pass props `show`, `dismiss`, `cancel` and `proceed` to your component.
// export default confirmable(LinkDialog);
export default DownloadModal;