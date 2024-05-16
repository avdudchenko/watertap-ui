import React, { Fragment, useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { Grid, Button, Box, Paper, Stack, Toolbar, FormControl, InputLabel, Select, MenuItem } from '@mui/material';
import { Table, TableBody, TableCell, TableHead, TableRow } from '@mui/material';
import DownloadIcon from '@mui/icons-material/Download';
import { downloadCSV, loadConfig, listConfigNames }  from '../../services/output.service.js'

export default function OutputComparisonTable(props) {
    let params = useParams(); 
    const { historyData } = props;
    const [leftConfigIndex, setLeftConfigIndex]  = React.useState(0)
    const [rightConfigIndex, setRightConfigIndex]  = React.useState(0)
    const [dense, setDense] = React.useState(true);
    const [ showTable, setShowTable ] = React.useState(false)

    useEffect(() => {
        if (historyData.length > 0) {
            setLeftConfigIndex(historyData.length-1)
            setShowTable(true)
        }
    
    }, [historyData])

useEffect(()=>{
  listConfigNames(params.id, outputData.inputData.version)
  .then(response => response.json())
  .then((data)=>{
    console.log("list config names:", data);
    setPastConfigs(data)
    var tempHistory = []
    for (const config of data) {
      loadConfig(params.id, config)
      .then(response => response.json())
      .then((data2)=>{
      tempHistory.push({name: config.replaceAll('"',''), data:data2})
      setHistoryData([...tempHistory])
      }).catch((err)=>{
          console.error("unable to get load config: ",err)
      });
  }
  }).catch((err)=>{
      console.error("unable to get list of config names: ",err)
  })
  
}, []);

const organizeVariables = () => {
  var tempHistory = []
  for (const bvars of historyData) {
    let var_sections = {}
    let tempVariables = {}
    let tempName = bvars.name
    for (const [key, v] of Object.entries(bvars.data.outputData.exports)) {
        
        let catg
        let is_input = v.is_input
        let is_output = v.is_output
        if (is_input) catg = v.input_category
        if (is_output) catg = v.output_category
        if (catg === null) {
            catg = ""
        }
        if (!Object.hasOwn(var_sections, catg)) {
            var_sections[catg] = {display_name: catg, variables: [], input_variables:[], output_variables:[]}
        }
        if (!Object.hasOwn(tempVariables, catg)) {
          tempVariables[catg] = {variables: [], input_variables:[], output_variables:[]}
      }
      tempVariables[catg].variables.push(v)
      var_sections[catg]["variables"] = [...tempVariables[catg].variables];
        if(is_output) {
          tempVariables[catg].output_variables.push(v)
          var_sections[catg]["output_variables"] = [...tempVariables[catg].output_variables];
        }
    }
    tempHistory.push({name: tempName, data: var_sections})
    setHistoryDataOrganized([...tempHistory])
    setLeftConfigIndex(tempHistory.length-1)
    setShowTable(true)
    // console.log("historyDataOrganized",tempHistory)
  }
  
}
    const handleLeftConfigSelection = (event) => {
      setLeftConfigIndex(event.target.value)
    }

    const handleRightConfigSelection = (event) => {
      setRightConfigIndex(event.target.value)
    }

    const renderConfigurationSelect = (index) => {
        return <FormControl >
            <InputLabel id="demo-simple-select-label"></InputLabel>
            <Select
                labelId="demo-simple-select-label"
                id="demo-simple-select"
                value={index===0 ? leftConfigIndex : rightConfigIndex}
                label="Past Configurations"
                onChange={index===0 ? handleLeftConfigSelection : handleRightConfigSelection}
                variant='standard'
            >
                {historyData.map((value, ind) => {
                    return <MenuItem key={value+ind} value={ind}>{value.name}</MenuItem>
                })}
            </Select>
        </FormControl>
    }

    const downloadSheet = () => {
      var arg = {"values": []}
      var cat1 = {}
      var cat2 = {}
      for(const cat of Object.keys(historyData[leftConfigIndex].data)) {
        cat1[cat] = {}
        cat2[cat] = {}
        for (var i = 0; i < historyData[leftConfigIndex].data[cat].variables.length; i++) {
          var rounding
          if (historyData[leftConfigIndex].data[cat].variables[i]["rounding"]) {
            rounding = historyData[leftConfigIndex].data[cat].variables[i]["rounding"]
          } else {
            rounding = 5
          }
          
          var metricName = historyData[leftConfigIndex].data[cat].variables[i]["name"]
          var leftValue = parseFloat((historyData[leftConfigIndex].data[cat].variables[i]["value"]).toFixed(rounding))
          var rightValue = parseFloat((historyData[rightConfigIndex].data[cat].variables[i]["value"]).toFixed(rounding))
          var units = historyData[rightConfigIndex].data[cat].variables[i]["display_units"]
          cat1[cat][metricName] = [leftValue,units]
          cat2[cat][metricName] = [rightValue,units]
        }

      }
      arg.values.push(cat1)
      arg.values.push(cat2)
      downloadCSV(params.id, arg)
      .then(response => response.blob())
      .then((data)=>{
        const href = window.URL.createObjectURL(data);
        const link = document.createElement('a');
        link.href = href;
        link.setAttribute('download', 'comparison_results.csv');
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      });
    }

    const renderRows = () => {


      return Object.keys(historyData[leftConfigIndex].data).map((category,index)=>{  
        if (historyData[leftConfigIndex].data[category] && historyData[rightConfigIndex].data[category]) {
        if (historyData[leftConfigIndex].data[category].variables.length > 0) {
          return ( <Fragment key={category+index}>
            <TableRow key={category+" "+index}>
              <TableCell rowSpan={historyData[leftConfigIndex].data[category].variables.length + 1}>
                <b>{category}</b>
              </TableCell>
            </TableRow>
            {historyData[leftConfigIndex].data[category].variables.map((metric, index) => { 
              var rounding
              if (metric.rounding != null) {
                rounding = metric.rounding
              } else {
                rounding = 5
              }
              return <TableRow key={index}>
                <TableCell>{metric.name}</TableCell>
                <TableCell>{parseFloat((metric.value).toFixed(rounding))+" "+metric.display_units}</TableCell>
                <TableCell>{parseFloat((historyData[rightConfigIndex].data[category].variables[index].value).toFixed(rounding))+" "+historyData[rightConfigIndex].data[category].variables[index].display_units}</TableCell>
                <TableCell align='right'>
                  {(Math.round((metric.value-historyData[rightConfigIndex].data[category].variables[index].value) * 100) / 100).toFixed(2)}</TableCell>
              </TableRow>
            })}
          </Fragment>
            )
        }
      }
      else {
        if (!historyData[leftConfigIndex].data[category]) {
          console.error('category '+category+' not found for left column')
        }
        if (!historyData[rightConfigIndex].data[category]) {
          console.error('category '+category+' not found for right column')
        }
      }
        })
    }


    const renderComparisonTable = () => {

        return <Grid item xs={12}>
          <Grid item xs={12}>
          <Toolbar spacing={2}>
              <Box sx={{ flexGrow: 1 }}></Box>
              <Stack direction="row" spacing={2}>
                <Button variant="outlined" startIcon={<DownloadIcon />} onClick={downloadSheet}>Download Results</Button>
              </Stack>
          </Toolbar>
          </Grid>
        <Paper>
          <Table style={{border:"1px solid #ddd"}} size={dense ? 'small' : 'medium'}>
            <TableHead>
              <TableRow key="tablehead">
                <TableCell style={{ width: '15%' }}></TableCell>
                <TableCell style={{ width: '20%' }}>Metric</TableCell>
                <TableCell style={{ width: '25%' }}>{renderConfigurationSelect(0)}</TableCell>
                <TableCell style={{ width: '25%' }}>{renderConfigurationSelect(1)}</TableCell>
                <TableCell style={{ width: '15%' }}>Value Difference</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {renderRows()}
            </TableBody>
          </Table>
        </Paper>
        {/* <Grid item xs={12}>
        <Button variant="text" startIcon={<DownloadIcon />} onClick={downloadSheet}>Download Results</Button>
        </Grid> */}
        </Grid>
      
    }

  return (

        <Grid container spacing={0} alignItems="flex-start"> 
          <Grid aria-label="output-table-grid" item xs={12}>
            {  showTable &&
                renderComparisonTable()
            }
        </Grid>
        </Grid>
      
  );
}
