import React, {useContext, useEffect, useLayoutEffect, useState} from 'react';
import Button from '@material-ui/core/Button';
import Dialog from '@material-ui/core/Dialog';
import Paper from '@material-ui/core/Paper';
import Draggable from 'react-draggable';
import {AppContext} from "../../App";
import { withStyles } from '@material-ui/core/styles';
import MuiDialogTitle from '@material-ui/core/DialogTitle';
import MuiDialogContent from '@material-ui/core/DialogContent';
import MuiDialogActions from '@material-ui/core/DialogActions';
import IconButton from '@material-ui/core/IconButton';
import CloseIcon from '@material-ui/icons/Close';
import Typography from '@material-ui/core/Typography';
import {ResizableBox, Resizable} from "react-resizable";
import D3Graph from "./D3Graph";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import {faCompress, faExpand} from "@fortawesome/free-solid-svg-icons";

import './graph.css'


const styles_title = (theme) => ({
    root: {
        margin: 0,
        padding: theme.spacing(2),
    },
    closeButton: {
        position: 'absolute',
        right: theme.spacing(1),
        top: theme.spacing(1),
        color: theme.palette.grey[500],
    },
});

const styles = theme => ({
    resizable: {
        position: "relative",
        "& .react-resizable-handle": {
            position: "absolute",
            width: 20,
            height: 20,
            bottom: 0,
            right: 0,
            background:
                "url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCA2IDYiIHN0eWxlPSJiYWNrZ3JvdW5kLWNvbG9yOiNmZmZmZmYwMCIgeD0iMHB4IiB5PSIwcHgiIHdpZHRoPSI2cHgiIGhlaWdodD0iNnB4Ij48ZyBvcGFjaXR5PSIwLjMwMiI+PHBhdGggZD0iTSA2IDYgTCAwIDYgTCAwIDQuMiBMIDQgNC4yIEwgNC4yIDQuMiBMIDQuMiAwIEwgNiAwIEwgNiA2IEwgNiA2IFoiIGZpbGw9IiMwMDAwMDAiLz48L2c+PC9zdmc+')",
            "background-position": "bottom right",
            padding: "0 3px 3px 0",
            "background-repeat": "no-repeat",
            "background-origin": "content-box",
            "box-sizing": "border-box",
            cursor: "se-resize"
        }
    }
});

const DialogTitle = withStyles(styles_title)((props) => {
    const { children, classes, onClose, ...other } = props;
    return (
        <MuiDialogTitle disableTypography className={classes.root} {...other}>
            <Typography variant="h6">{children}</Typography>
            {onClose ? (
                <IconButton aria-label="close" className={classes.closeButton} onClick={onClose}>
                    <CloseIcon />
                </IconButton>
            ) : null}
        </MuiDialogTitle>
    );
});

const DialogContent = withStyles((theme) => ({
    root: {
        padding: theme.spacing(2),
    },
}))(MuiDialogContent);

const DialogActions = withStyles((theme) => ({
    root: {
        margin: 0,
        padding: theme.spacing(1),
    },
}))(MuiDialogActions);

function D3DraggableDialog(props) {
    const { showgraphmodal } = useContext(AppContext);
    const [openDraggableDialog, setOpenDraggableDialog] = useState(false);
    const [reportID, setReportID] = useState(false);
    const [reportID_Not_Hashed, setReportID_Not_Hashed] = useState(false);
    const [widthResizableBox, setWidthResizableBox] = useState(document.width);
    const [heightResizableBox, setHeightResizableBox] = useState(document.height);
    // const [fullWidthState, setFullWidthState] = useState(true);
    const [Language,SetLanguage] = useState('');
    const [LoadingFullScreen, SetLoadingFullScreen] = useState(false);
    const [ToggleExpandIcon, setToggleExpandIcon] = useState(faExpand);
    const [ToggleFullScreen, setToggleFullScreen] = useState(false);
    const [ToggleFullWidth, setToggleFullToggleFullWidth] = useState(false);
    const [DraggablePosition, setDraggablePosition] = useState(null);
    const [ResizeHandles, setResizeHandles] = useState(['se']);
    const [DraggableDisable, setDraggableDisable] = useState(false);
    const [ShowGraphModal,SetshowGraphModal] = showgraphmodal





    useEffect(()=>{
        if(props.graph_row){
            setOpenDraggableDialog(true)
            // console.log('dentro modale')
            setReportID(props.graph_row['id_report'])
            setReportID_Not_Hashed(props.graph_row['id_report_not_hashed'])
            SetLanguage(props.graph_row['language'])
        }
        else{
            setOpenDraggableDialog(false)
        }
    },[props.graph_row])

    // useEffect(()=>{
    //     console.log('dentro modale',reportID)
    //
    // },[reportID])

    function PaperComponent(props) {
        return (
            <Draggable defaultPosition={{x: 0, y: 0}} position={DraggablePosition} handle="#draggable-dialog-title" cancel={'[class*="MuiDialogContent-root"]'} disabled={DraggableDisable}>
                <Paper {...props} />
            </Draggable>
        );
    }


    const showDraggableDialog = () => {
        setOpenDraggableDialog(true);
    };

    const handleDraggableDialogClose = () => {
        setOpenDraggableDialog(false);
        SetshowGraphModal(false);
    };

    let d3chartdivID = "D3-chart-div-"+reportID;
    let d3charttitleID = "D3-chart-title-"+reportID;
    let d3expandchartID = "D3-expand-chart-"+reportID;
    let d3svgchartID = "D3-expand-chart-"+reportID;
    let d3svgchartgID = "D3-chart-g-"+reportID;

    // const onResize = (event, {el, size, handle}) => {
    //    let element = document.querySelector(".MuiDialog-paperWidthXl");
    //     console.dir(element.clientWidth, element.clientHeight);
    //     // setWidthResizableBox(element.clientWidth);
    //     // setHeightResizableBox(element.clientHeight);
    // }

    useLayoutEffect(() => {

            console.dir(document.height);
            setHeightResizableBox(document.body.clientHeight);
            setWidthResizableBox(0.8*document.body.clientWidth);
            SetLoadingFullScreen(true);

    },[]);

    function handleExpandClick() {
        if (ToggleExpandIcon == faExpand)
        {
            setDraggablePosition({x: 0, y: 0})
            setToggleFullScreen(true);
            setToggleFullToggleFullWidth(true);
            setToggleExpandIcon(faCompress);
            setHeightResizableBox(document.body.clientHeight);
            setWidthResizableBox(document.body.clientWidth);
            setResizeHandles([]);
            setDraggableDisable(true);


        }
        else
        {
            setDraggablePosition(null);
            setToggleFullScreen(false);
            setToggleFullToggleFullWidth(false);
            setToggleExpandIcon(faExpand);
            setHeightResizableBox(document.body.clientHeight);
            setWidthResizableBox(0.8*document.body.clientWidth);
            setResizeHandles(['se'])
            setDraggableDisable(false);
        }
    }

    function handleResize(){
        setDraggablePosition(null);
        setToggleExpandIcon(faExpand);
        setToggleFullToggleFullWidth(false);
        setToggleFullScreen(false);
        setHeightResizableBox(document.body.clientHeight);
        setWidthResizableBox(0.8*document.body.clientWidth);
    }

    return (

        <div>
            <Dialog
                open={openDraggableDialog}
                onClose={handleDraggableDialogClose}
                aria-labelledby="draggable-dialog-title"
                PaperComponent={PaperComponent}
                maxWidth={false}
                fullScreen={ToggleFullScreen}
                fullWidth={ToggleFullWidth}
            >
                <ResizableBox
                    height={heightResizableBox}
                    width={widthResizableBox}
                    className={props.classes.resizable}
                    minConstraints={[400, 400]}
                    maxConstraints={[1920, 1080]}
                    onResize = {handleResize}
                    resizeHandles = {ResizeHandles}
                >
                <>
                    <DialogTitle style={{ cursor: 'move' }} id="draggable-dialog-title" onClose={handleDraggableDialogClose}>
                        Graph for report: <span className={"highlighted"}>{reportID_Not_Hashed}</span>
                    </DialogTitle>
                    <DialogContent>
                            <div id={d3chartdivID}>
                                <h3 id={d3charttitleID}></h3>
                                <FontAwesomeIcon icon={ToggleExpandIcon} size="2x" className={"d3-expand-button"} onClick={handleExpandClick} />
                                {reportID && <D3Graph report_id ={reportID} language={Language}/>}
                            </div>
                    </DialogContent>
                    </>
            </ResizableBox>
            </Dialog>

        </div>
    );
}


export default withStyles(styles)(D3DraggableDialog);