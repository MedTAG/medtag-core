import React, {useContext, useEffect} from 'react'
import Nav from "react-bootstrap/Nav";
import './sideBar.css';
import {AppContext} from "../../App";
import {faLocationArrow, faSignOutAlt, faTimes} from "@fortawesome/free-solid-svg-icons";
import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";
import {ReactCSSTransitionGroup,TransitionGroup} from 'react-transition-group'; // ES6
import Snackbar from '@material-ui/core/Snackbar';

function SnackBar(props){
    const { showSnack, showSnackMessage } = useContext(AppContext);
    const [ShowSnack,SetShowSnack] = showSnack;
    const [SnackMessage,SetSnackMessage] = showSnackMessage;

    const [state, setState] = React.useState({
        vertical: 'top',
        horizontal: 'right',
    });

    const { vertical, horizontal } = state;

    // useEffect(()=>{
    //     console.log('messaggio',ShowSnack)
    //     console.log('messaggio',props.message)
    // },[ShowSnack])


    const handleClose = () => {
        SetShowSnack(false)
    };

    return (
        <div style={{'width':'20%'}}>
            {/*{props.message}*/}
            <Snackbar style={{'width':'inherit'}}
                anchorOrigin={{ vertical, horizontal }}
                open={ShowSnack}

                onClose={handleClose}
                message={SnackMessage}
                key={vertical + horizontal}
            />
        </div>
    );

}

export default SnackBar
