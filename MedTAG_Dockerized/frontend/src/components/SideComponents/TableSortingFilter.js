import React, {useEffect, useState} from 'react'
import styled from 'styled-components'
import Button from "react-bootstrap/Button";
import makeData from './makeData'
import {Col} from "react-bootstrap";
import axios from "axios";
import { useTable, usePagination, useBlockLayout, useResizeColumns, useRowSelect, useSortBy } from 'react-table'
import Typography from "@material-ui/core/Typography";
import Toolbar from "@material-ui/core/Toolbar";
import {faFileAlt} from "@fortawesome/free-solid-svg-icons";
import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";
import {
    faTrash
} from '@fortawesome/free-solid-svg-icons';
// const Styles = styled.div`
  ///* This is required to make the table full-width */
  //display: block;
  //max-width: 100%;
  //
  ///* This will make the table scrollable when it gets too small */
  //.tableWrap {
  //  display: block;
  //  max-width: 100%;
  //  overflow-x: scroll;
  //  overflow-y: hidden;
  //  border-bottom: 1px solid black;
  //}
  //padding: 1rem;
  //
  //
  //table {
  //  /* Make sure the inner table is always as wide as needed */
  //  width: 100%;
  //  border-spacing: 0;
  //  border: 1px solid black;
  //
  //
  //  tr {
  //    :last-child {
  //      td {
  //        border-bottom: 0;
  //      }
  //    }
  //  }
  //
  //  th,
  //  td {
  //    margin: 0;
  //    padding: 0.5rem;
  //    border-bottom: 1px solid black;
  //    border-right: 1px solid black;
  //
  //    /* The secret sauce */
  //    /* Each cell should grow equally */
  //    width: 1%;
  //    /* But "collapsed" cells should be as small as possible */
  //    &.collapse {
  //      width: 0.0000000001%;
  //    }
  //
  //    :last-child {
  //      border-right: 0;
  //    }
  //  }
  //}
const Styles = styled.div`
  padding: 1rem;
  th:has(div) {
    width: 8px !important;
  }
  table {
    border-spacing: 0;
    border: 1px solid black;

    tr {
      :last-child {
        td {
          border-bottom: 0;
        }
      }
    }

    th,
    td {
      margin: 0;
      padding: 0.5rem;
      border-bottom: 1px solid black;
      border-right: 1px solid black;

      :last-child {
        border-right: 0;
      }
    }
  
  .pagination {
    padding: 0.5rem;
  }
`



const IndeterminateCheckbox = React.forwardRef(
    ({ indeterminate, ...rest }, ref) => {
        const defaultRef = React.useRef()
        const resolvedRef = ref || defaultRef

        React.useEffect(() => {
            resolvedRef.current.indeterminate = indeterminate
        }, [resolvedRef, indeterminate])

        return <input type="checkbox" ref={resolvedRef} {...rest} />
    }
)

function Table({ columns, data,hidden }) {
    // Use the state and functions returned from useTable to build your UI
    const {
        getTableProps,
        getTableBodyProps,
        headerGroups,
        rows,
        prepareRow,
        allColumns,
        getToggleHideAllColumnsProps,
        state,
        page, // Instead of using 'rows', we'll use page,
        // which has only the rows for the active page
        // The rest of these things are super handy, too ;)
        canPreviousPage,
        canNextPage,
        pageOptions,
        pageCount,
        gotoPage,
        nextPage,
        previousPage,
        selectedFlatRows,
        setPageSize,
        state: { pageIndex, pageSize, selectedRowIds },


    } = useTable(
        {
            columns,
            data,
            // initialState: { pageIndex: 2 },
            initialState: {
                pageIndex: 0,
                hiddenColumns: hidden
            },

        },

        usePagination,
        useRowSelect,
        useSortBy,
        hooks => {
            hooks.visibleColumns.push(columns => [
                // Let's make a column for selection
                {
                    id: 'selection',
                    // The header can use the table's getToggleAllRowsSelectedProps method
                    // to render a checkbox
                    Header: ({ getToggleAllRowsSelectedProps }) => (
                        <div>
                            <IndeterminateCheckbox {...getToggleAllRowsSelectedProps()} />
                        </div>
                    ),
                    // The cell can use the individual row's getToggleRowSelectedProps method
                    // to the render a checkbox
                    Cell: ({ row }) => (
                        <div>
                            <IndeterminateCheckbox {...row.getToggleRowSelectedProps()} />
                        </div>
                    ),
                },
                ...columns,
            ])
        }

    )
    const [ShowChecks,SetShowChecks] = useState(false)
    const numSelected= Object.keys(selectedRowIds).length
    // Render the UI for your table
    return (
        <>
            <div style={{'margin-bottom':'2%','text-align':'center'}}>Click <Button variant='info' size='sm' onClick={()=>SetShowChecks(prev=>!prev)}>here</Button> to decide what columns you want to display in the table (default: <i>id_report, language, use_case, institute</i>)</div>
            {ShowChecks && <div style={{'margin-bottom':'2%','text-align':'center'}}>
                <span style={{'margin-bottom':'5px'}}>
                    <IndeterminateCheckbox {...getToggleHideAllColumnsProps()} />&nbsp;&nbsp;Toggle All
                </span>&nbsp;&nbsp;&nbsp;&nbsp;
                {allColumns.map(column => (
                    <span key={column.id}>
                        <label>
                            <input type="checkbox" {...column.getToggleHiddenProps()} />{' '}
                            {column.id}&nbsp;&nbsp;&nbsp;&nbsp;
                        </label>
                    </span>
                ))}
                <br />
            </div>}

            <div style={{'text-align':'right'}}>
                <span>Go to page:{' '}
                    <input
                        type="number"
                        defaultValue={pageIndex + 1}
                        onChange={e => {
                            const page = e.target.value ? (Number(e.target.value) - 1) : 0
                            gotoPage(page)
                        }}
                        style={{ width: '100px' }}
                    />
                    </span>&nbsp;&nbsp;
                    <select
                        value={pageSize}
                        onChange={e => {
                            setPageSize(Number(e.target.value))
                        }}
                    >
                        {[10, 20, 30, 40, 50].map(pageSize => (
                            <option key={pageSize} value={pageSize}>
                                Show {pageSize}
                            </option>
                        ))}
                    </select>
            </div>
            {numSelected > 0 && (
                <div>
                    <span style={{'text-align':'left'}}>{numSelected} reports selected</span>
                    <span style={{'text-align':'right'}}><FontAwesomeIcon icon={faTrash} /></span>
                </div>
            ) }
            <div style={{'text-align':'-webkit-center','overflow':'auto'}}>
                <table {...getTableProps()}>

                    <thead>
                    {headerGroups.map(headerGroup => (
                        <tr {...headerGroup.getHeaderGroupProps()}>
                            {headerGroup.headers.map(column => (
                                // Add the sorting props to control sorting. For this example
                                // we can add them into the header props
                                <th {...column.getHeaderProps(column.getSortByToggleProps())}>
                                    {column.render('Header')}
                                    {/* Add a sort direction indicator */}
                                    <span>
                    {column.isSorted
                        ? column.isSortedDesc
                            ? ' 🔽'
                            : ' 🔼'
                        : <span>&nbsp;&nbsp;</span>}
                  </span>
                                </th>
                            ))}
                        </tr>
                    ))}
                    </thead>

                    <tbody {...getTableBodyProps()}>
                    {page.map((row, i) => {
                        prepareRow(row)
                        return (
                            <tr {...row.getRowProps()}>
                                {row.cells.map(cell => {
                                    return <td {...cell.getCellProps()}>{cell.render('Cell')}</td>
                                })}
                            </tr>
                        )
                    })}
                    </tbody>
                </table>
            </div>

            {/*
        Pagination can be built however you'd like.
        This is just a very basic UI implementation:
      */}
      <div style={{'justify-content':'center','display':'flex'}}>
          <div className="pagination" >
              <Button variant='info' size='sm' onClick={() => {gotoPage(0);window.scrollTo(0,0)}} disabled={!canPreviousPage}>
                  {'<<'}
              </Button>&nbsp;
              <Button variant='info' size='sm' onClick={() => {previousPage();window.scrollTo(0,0)}} disabled={!canPreviousPage}>
                  {'<'}
              </Button>&nbsp;
              <Button variant='info' size='sm' onClick={() => {nextPage();window.scrollTo(0,0)}} disabled={!canNextPage}>
                  {'>'}
              </Button>&nbsp;
              <Button variant='info' size='sm' onClick={() => {gotoPage(pageCount - 1);window.scrollTo(0,0)}} disabled={!canNextPage}>
                  {'>>'}
              </Button>&nbsp;
              <span>&nbsp;&nbsp;
                  Page{' '}
                  <strong>
            {pageIndex + 1} of {pageOptions.length}
          </strong>{' '}
        </span>

          </div>
      </div>

        </>
    )
}


function TableSortingFilter(props) {

    const columns = React.useMemo(
        () => props.columns,
        []
    )
    const data = React.useMemo(() => makeData(100000), [])
    return (
        <Styles>

            <Table columns={columns} data={props.data} hidden={props.hidden} />
        </Styles>
    )
}

export default TableSortingFilter
