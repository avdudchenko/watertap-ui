import './SweepOutput.css';
import React from 'react'; 
import { useEffect, useState } from 'react';
import DownloadIcon from '@mui/icons-material/Download';
import { Table, TableBody, TableCell, TableHead, TableRow, TableContainer, Select, ListItemButton } from '@mui/material';
import { Grid, Typography, Button, InputLabel, MenuItem, FormControl, Tabs, Tab, Box, List, ListItem, ListItemText } from '@mui/material';
import Plot from 'react-plotly.js';

export default function SweepOutput(props) {
    const { outputData, downloadOutput } = props;
    const [ plotType, setPlotType ] = useState(0)
    const [ plotData, setPlotData ] = useState({data: []})
    const [ showPlot, setShowPlot ] = useState(false)
    const [ indices, setIndices ] = useState([1, 0, 2])
    const [ tabValue, setTabValue ] = useState(0)
    const [ selectedItems, setSelectedItems ] = useState([]);
    const [ currentUnits, setCurrentUnits ] = useState(null)

    const styles = {
        parameters: {
            border:"1px solid #71797E",
            backgroundColor: "#f4f0ec"
        },
        outputs: {
            border:"1px solid #71797E"
        }, 
        tableHeader: {
            border:"2px solid #71797E", 
            backgroundColor:"#E5E4E2",
            fontWeight: "bold"
        }
    }

    useEffect(() => {
        if (tabValue === 1) {
            let num_parameters = outputData.outputData.sweep_results.num_parameters;
            if (num_parameters === 1) {
                setPlotType(1)
                unpackData(1, 0, 1)
            } else if (num_parameters === 2) {
                setPlotType(2)
                unpackData(2, 1, 0, 2)
            } else {
                // show parrallel lines plot
                setPlotType(3)
                unpackData(3)
            }
        }
        
    }, [props.outputData, tabValue])

    const addPlotLine = (yIndex, tempPlotData) => {
        let keys = outputData.outputData.sweep_results.keys
        let x = []
        let ys = []
        for (let i = 0; i < outputData.outputData.sweep_results.num_outputs; i++) {
            ys.push([])
        }
        for (let each of outputData.outputData.sweep_results.values) {
            x.push(Math.round(each[0] * 1000) / 1000)
            
            for(let i = 1; i < each.length; i++) {
                let out=null
                if (each[i]!==null){
                    out = Math.round(each[i] * 1000) / 1000}
                ys[i-1].push(out)
            }
        }
        let nextTrace = []
        let keyIdx = 1
        for (let each of ys) {
            if( keyIdx === yIndex){
                let yName = `${outputData.outputData.sweep_results.headers[keyIdx]}`
                let finalName = ``
                if (yName.length > 32) {
                    let nameArray = yName.split(" ")
                    for (let i = 0; i < nameArray.length; i++) {
                        console.log(nameArray[i])
                        finalName = finalName.concat(nameArray[i], " ")
                        console.log(finalName)
                        if (i % 3 == 0 && i != 0 && i != nameArray.length - 1) {
                            finalName = finalName.concat("<br>")
                        }
                    }
                }
                else {
                    finalName = `${outputData.outputData.sweep_results.headers[keyIdx]}`
                }
                let tempTrace = {x: x, y: each, type:"scatter", name: finalName}
                nextTrace.push(tempTrace)
                
            }
            keyIdx+=1
            
        }
        tempPlotData.push(nextTrace[0])

        let xLabel = `${outputData.outputData.sweep_results.headers[0]} (${outputData.outputData.exports[keys[0]].display_units})`
        let yLabel 
        let yUnits = outputData.outputData.exports[keys[yIndex]].display_units
        if (tempPlotData.length > 1) {
            yLabel = `${yUnits}`
        } else {
            yLabel = `${outputData.outputData.sweep_results.headers[yIndex]} (${yUnits})`
        }
        
        let tempLayout = {
            xaxis: {
                title: {
                    text: xLabel,
                },
            },
            yaxis: {
                title: {
                    text: yLabel,
                },
            },
            width: 700,
            height: 500,
        };
        setCurrentUnits(yUnits)
        setPlotData({data: tempPlotData, layout:tempLayout})
        setShowPlot(true);
    }

    const removePlotLine = (index) => {
        let itemToRemove = outputData.outputData.sweep_results.headers[index]
        let tempPlotData = [...plotData.data]
        let updatedPlotData = tempPlotData.filter(item => item.name !== itemToRemove);
        setPlotData({data: updatedPlotData, layout: plotData.layout})
    }

    const handleParameterSelection = (event, newIndex) => {
        if(plotType === 1) {
            // item has already been selected
            if (selectedItems.includes(newIndex)) {
                if (selectedItems.length == 1) {
                    return
                }

                const updatedItems = selectedItems.filter(item => item !== newIndex);
                
                removePlotLine(newIndex)
                setSelectedItems(updatedItems);
            }
            // item is unhighlighted
            else {
                let newUnits = outputData.outputData.exports[outputData.outputData.sweep_results.keys[newIndex]].display_units
                if (newUnits === currentUnits) { // add on to same plot
                    setSelectedItems([...selectedItems, newIndex]);
                    addPlotLine(newIndex, [...plotData.data])
                }
                else { // create new plot
                    setSelectedItems([newIndex]);
                    addPlotLine(newIndex, [])
                }
            }
        } else {
            unpackData(plotType, indices[0], indices[1], newIndex)
        } 
        
    }

    const handleTabChange = (event, newValue) => {
        setTabValue(newValue)
    }

    const unpackData = (plotType, xIndex, yIndex, zIndex) => {
        let keys = outputData.outputData.sweep_results.keys
        if (plotType === 2) { //contour map
            let x = []
            let y = []
            let z = []
            let currZ = []
            for (let each of outputData.outputData.sweep_results.values) {
                let tempX = Math.round(each[xIndex] * 1000) / 1000
                let tempY = Math.round(each[yIndex] * 1000) / 1000
                let tempZ = null
                if (each[zIndex]!==null){
                tempZ = Math.round(each[zIndex] * 1000) / 1000}
           

                if(!x.includes(tempX)) {
                    x.push(tempX)
                }
                if(!y.includes(tempY)) {
                    y.push(tempY)
                }
            }

            for (let each of outputData.outputData.sweep_results.values) {
                let tempZ = null
                if (each[zIndex]!==null){
                tempZ = Math.round(each[zIndex] * 1000) / 1000}
                currZ.push(tempZ)
                if (currZ.length === x.length) {
                    z.push(currZ)
                    currZ = []
                }
            }

            let xLabel = `${outputData.outputData.sweep_results.headers[xIndex]} (${outputData.outputData.exports[keys[xIndex]].display_units})`
            let yLabel = `${outputData.outputData.sweep_results.headers[yIndex]} (${outputData.outputData.exports[keys[yIndex]].display_units})`
            let zLabel = `${outputData.outputData.sweep_results.headers[zIndex]} (${outputData.outputData.exports[keys[zIndex]].display_units})`

            let tempPlotData = [{
                z:z,
                x:x,
                y:y,
                type: 'heatmap',
                zsmooth:false,
                hoverongaps: false,
                colorscale: 'Viridis',
                colorbar: {
                    title: {
                        text: zLabel,
                        side: "right"
                    },
                },
                }]

            let tempPlotLayout = {
                xaxis: {
                    title: {
                        text: xLabel,
                    }
                },
                yaxis: {
                    title: {
                        text: yLabel
                    }
                },
            }
            setPlotData({data: tempPlotData, layout: tempPlotLayout})
            setShowPlot(true)
            setSelectedItems([zIndex])
        } else if (plotType===1){ // line plot
            setSelectedItems([yIndex])
            addPlotLine(yIndex, [])
            setShowPlot(true)
        } else if (plotType ===3) { //parallel coordinates plot
            // console.log('making parallel coordinates plot')
            let dimensions = []
            for (let each of outputData.outputData.sweep_results.headers) {
                dimensions.push({label: each, values: []})
            }
            for (let each of outputData.outputData.sweep_results.values) {
                for(let i = 0; i < each.length; i++) {
                    let tempDimension = dimensions[i]
                    tempDimension.values.push(each[i])
                }
            }
            for (let each of dimensions) {
                // let maxRange
                let max = Math.max(...each.values)
                let min = Math.min(...each.values)
                if (max > 0 && min > 0) {
                    // maxRange = Math.ceil(max) + Math.ceil(min)
                    each.range = [0, Math.ceil(max+min)]
                }
            }
            // console.log(dimensions)
            let trace = {
                type: 'parcoords',
                line: {
                  color: 'blue'
                },
                dimensions: dimensions
              };
              let tempLayout = {
                width: 1000,
                height: 500,
            };
            setPlotData({data: [trace], layout:tempLayout})
            setShowPlot(true)
        }
        setIndices([xIndex, yIndex, zIndex])
    }
    
    return ( 
        <Grid container spacing={2}> 
            <Grid item xs={12}> 
                <Box sx={{display: 'flex', justifyContent: 'center'}}>
                    <Tabs value={tabValue} onChange={handleTabChange} aria-label="tabs">
                        <Tab label="Table View" />
                        <Tab label="Chart View" /> 
                    </Tabs>
                </Box>
                
            </Grid>
            
            {tabValue === 0 && 
            <>
                <Grid item xs={12}>
                <TableContainer sx={{maxHeight: "80vh", overflowX:'auto'}}>
                <Table className="parameter-sweep-output-table" style={{border:"1.5px solid #71797E"}} size={'small'}>
                    <TableHead>
                    <TableRow style={styles.tableHeader}>
                        <TableCell style={styles.tableHeader} colSpan={outputData.outputData.sweep_results.num_parameters} align="center">
                            Sweep Parameters
                        </TableCell>
                        <TableCell style={styles.tableHeader} colSpan={outputData.outputData.sweep_results.num_outputs} align="center">
                            Variables
                        </TableCell>
                    </TableRow>
                    <TableRow key="tablehead"> 
                        {outputData.outputData.sweep_results.headers.map( (value, index)  => {
                            return <TableCell style={{border:"1px solid #71797E", backgroundColor:"#E5E4E2"}} key={`head_${index}`}> 
                            <Typography noWrap>{value}</Typography>
                            </TableCell>
                        })}
                    </TableRow>
                    </TableHead>
                    <TableBody>
                        {outputData.outputData.sweep_results.values.map( (row, ridx)  => {
                            return (
                                <TableRow key={`row_${ridx}`}> 
                                {row.map( (cell, cidx) => {
                                    return (<TableCell 
                                                style={cidx < outputData.outputData.sweep_results.num_parameters ? styles.parameters : styles.outputs} key={`cell_${cidx}`} 
                                                align="right"
                                            > 
                                                {cell && cell.toFixed(3)}
                                            </TableCell>
                                    )
                                })}
                                </TableRow>
                            )
                        })}
                    </TableBody>
                </Table>
                </TableContainer>
                
                </Grid> 
                <Grid item xs={12}>
                    <Button variant="text" startIcon={<DownloadIcon />} onClick={downloadOutput}>Download Results</Button>
                </Grid>
            </>
            }
            {tabValue === 1 && 
            <>
            {showPlot && (outputData.outputData.sweep_results.num_parameters === 1 || outputData.outputData.sweep_results.num_parameters === 2) && 
                // Replacing FormControl with list
                // test by sweep ing TDS concentration
                <Grid sx={{marginTop:5, minWidth: 250, overflow: 'auto'}} item xs={3}>
                    <InputLabel sx={{marginTop:0, fontWeight: '500', fontSize: 17}} id="previous-configs-label">Output Metric&nbsp;</InputLabel>
                        <List
                        labelId="Parameter Selection"
                        id="Parameter Selection"
                        value={plotType === 2 ? indices[2]-outputData.outputData.sweep_results.num_parameters : plotType === 1 && indices[1]-outputData.outputData.sweep_results.num_parameters}
                        sx={{minWidth: 50, maxHeight: 500, fontSize: 15}}
                        >
                        {outputData.outputData.sweep_results.headers.slice(outputData.outputData.sweep_results.num_parameters).map((name, index) => {
                            let realIndex = index + outputData.outputData.sweep_results.num_parameters
                            return <ListItem
                                key={name+" "+realIndex}
                                dense 
                                style={{
                                border: '1px solid rgba(0, 0, 0, 0.5)',
                                borderRadius: '1px',
                                paddingTop: 0, 
                                paddingBottom: 0,
                                paddingLeft: 0,
                                paddingRight: 0}}
                            >
                                <ListItemButton
                                    onClick={(event) => handleParameterSelection(event, realIndex)}
                                    key={`${name}_${realIndex}`}
                                    value={realIndex}
                                    selected={selectedItems.includes(realIndex)}
                                    sx={{
                                        textAlign: 'center',
                                        justifyContent: 'center',
                                        '&.Mui-selected': {
                                            //backgroundColor: 'rgba(0, 0, 0, 0.04)', 
                                            backgroundColor: 'rgba(0, 0, 255, 0.12)', 
                                            padding: '12px', 
                                            borderRadius: '4px', 
                                                                    },
                                        '&:not(.Mui-selected)': {
                                            backgroundColor: 'transparent',
                                            padding: '12px',
                                            borderRadius: '4px',
                                            },
                                        '&:hover': {
                                        backgroundColor: 'rgba(0, 0, 0, 0.04)', 
                                        }}}
                                    >
                                    {name}
                                </ListItemButton>
                            </ListItem>
                        })}
                        </List>
                </Grid>
            }
              <Grid item xs={1}>
                {/* Empty grid for spacing */}
            </Grid>
                
            <Grid item xs={3} md={2}>
                {showPlot && 
                <>
                <Plot
                    data={plotData.data}
                    layout={plotData.layout}
                />
                </>
                
                }
            
            </Grid>
                
            </>
            }
            
        </Grid>
    );
}
