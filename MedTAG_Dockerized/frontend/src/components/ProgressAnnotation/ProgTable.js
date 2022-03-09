import React, {useState, useEffect, useContext, createContext} from 'react';
import Paper from '@material-ui/core/Paper';
import {EditingState, SelectionState} from '@devexpress/dx-react-grid';
import '../ReportStatistics/tables.css'
// import Button from '@material-ui/core/Button'
import Button from "react-bootstrap/Button";
import GetAppOutlinedIcon from '@material-ui/icons/GetAppOutlined';
import GetAppIcon from '@material-ui/icons/GetApp';
import {
    SearchState,
    FilteringState,
    IntegratedFiltering,
    PagingState,
    IntegratedPaging,
    SortingState,
    IntegratedSorting,
    DataTypeProvider,
    GroupingState,
    IntegratedGrouping,

} from '@devexpress/dx-react-grid';
import {Container, Row, Col, OverlayTrigger} from "react-bootstrap";

import {
    Grid,
    Table,
    SearchPanel,
    TableHeaderRow,
    TableRowDetail,
    TableFilterRow,
    VirtualTable,
    DragDropProvider,
    TableColumnReordering,
    TableGroupRow,
    GroupingPanel,
    Toolbar,
    PagingPanel,
    TableEditColumn,
    ColumnChooser,
    TableSelection,
    TableColumnVisibility,
    TableColumnResizing,
} from '@devexpress/dx-react-grid-material-ui';
import PeopleIcon from '@material-ui/icons/People';

import {AppContext} from "../../App";

import Tooltip from "react-bootstrap/Tooltip";
import axios from "axios";
import InfoIcon from "@material-ui/icons/Info";


export const TableToShowContext = createContext('')
export default function ProgTable(props) {
    const { showannotations,showreporttext,showmajoritygt,showmajoritymodal,usecaseList,languageList,instituteList,username,admin } = useContext(AppContext);

    const [sortingStateColumnExtensions] = useState([
        { columnName: '', sortingEnabled: false },
    ]);
    const [pageSizes] = useState([5, 10, 25, 50, 0]);
    // const [tableColumnVisibilityColumnExtensions] = useState([
    //     { columnName: 'id_report', togglingEnabled: false },
    // ]);
    const [rows,setRows] = useState(props.righe)
    const [filteredRows,setFilteredRows] = useState(props.righe)
    const [deleteCols] = useState(['']);
    const [FilterExt] = useState([{columnName:'', filteringEnabled:false,SortingEnabled:false}])
    const [ResizeExt] = useState([{columnName:'', minWidth:150,maxWidth:150}])
    const [grouping] = useState([{ columnName: 'usecase' }]);
    var FileDownload = require('js-file-download');

    // function download_users(e,row){
    //     console.log('users')
    //     axios.get('http://examode.dei.unipd.it/exatag/download_prog_users',
    //         {params:{row:row}}).then(function (response){
    //             FileDownload((response.data), 'users.csv');
    //                             })
    //         .catch(function (error) {
    //             console.log('error message', error);
    //         });
    // }
    function download_reports(e,tipo,row){
        console.log('reports')
        axios.get('http://examode.dei.unipd.it/exatag/download_prog_reports',
            {params:{row:row,'type':tipo}}).then(function (response){
                if(tipo === 'csv'){
                    FileDownload((response.data), 'reports_ids.csv');

                }
                else if(tipo === 'json'){
                    FileDownload(JSON.stringify(response.data), 'reports_ids.json');

                }
        })
            .catch(function (error) {
                console.log('error message', error);
            });
    }



    const DeleteDownloadFormatter = ({ row }) =>
        <div>

            <OverlayTrigger
                key='left'
                placement='top'
                overlay={
                    <Tooltip id={`tooltip-top'`}>
                        Download the reports' ids (CSV)
                    </Tooltip>
                }
            >
                <Button className='opt_but' onClick={(e)=>{download_reports(e,'csv',row)}} size='sm'><GetAppIcon color="action"/></Button>
            </OverlayTrigger>

            <OverlayTrigger
                key='left'
                placement='top'
                overlay={
                    <Tooltip id={`tooltip-top'`}>
                        Download the reports' ids (JSON)
                    </Tooltip>
                }
            >
                <Button onClick={(e)=>{download_reports(e,'json',row)}}  className='opt_but' size='sm'><GetAppOutlinedIcon color="action"/></Button>
            </OverlayTrigger>


        </div>;

    const DeleteDownloadTypeProvider = props => (
        <DataTypeProvider
            formatterComponent={DeleteDownloadFormatter}
            {...props}
        />
    );

    const ModeFormatter = ({ row }) => (
        <div>


            <OverlayTrigger
                key='left'
                placement='top'
                overlay={
                    <Tooltip id={`tooltip-top'`}>
                        {row.mode === 'Manual' ? <>Users annotations</> : <>Automatic annotation edited by users</>}
                    </Tooltip>
                }
            >
                <div>{row.mode}</div>
            </OverlayTrigger>
        </div>

    );

    const ModeProvider = props => (
        <DataTypeProvider
            formatterComponent={ModeFormatter}
            {...props}
        />
    );




    const FilterCell = (props) => {
        const { column } = props;
        if(column.name === 'mode' || column.name === 'annotations'){
            return <TableFilterRow.Cell {...props} />;

        }
        else
        {
            return <th className="MuiTableCell-root MuiTableCell-head"> </th>
        }

    };




    return (

        <div>
                <div>
                    {(rows.length>0) && <div style={{ width:'100%' }}>

                        <Grid
                            rows={filteredRows}
                            columns={props.columns}
                        >
                            {/*<GroupingState*/}
                            {/*    defaultGrouping={grouping}*/}
                            {/*    columnExtensions={props.default_group}*/}
                            {/*/>*/}
                            <DeleteDownloadTypeProvider for={deleteCols} />
                            <ModeProvider for={['mode']} />

                            <SearchState />
                            <PagingState
                                defaultCurrentPage={0}
                                defaultPageSize={5}
                            />

                            <FilteringState columnExtensions={FilterExt} defaultFilters={[]} />
                            <IntegratedFiltering />
                            <SortingState defaultSorting={[{ columnName: 'annotations', direction: 'desc' }]}
                                          columnExtensions={sortingStateColumnExtensions}

                            />

                            <IntegratedSorting />
                            <IntegratedPaging />
                            <Table  />
                            <TableColumnResizing defaultColumnWidths={props.default_width}
                                                 columnExtensions={ResizeExt} />
                            <TableHeaderRow showSortingControls />

                            {/*<TableColumnVisibility*/}
                            {/*    columnExtensions={tableColumnVisibilityColumnExtensions}*/}
                            {/*/>*/}
                            <TableFilterRow
                                cellComponent={FilterCell}
                            />


                            <PagingPanel
                                pageSizes={pageSizes}
                            />

                        </Grid>
                    </div> }
                </div>
        </div>

    );
};







