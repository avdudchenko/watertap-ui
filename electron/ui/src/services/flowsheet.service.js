

export const getFlowsheet = (id, build) => {
    return fetch(process.env.REACT_APP_BACKEND_SERVER+'/flowsheets/'+id+'/config?build='+build, {mode: 'cors'});
    /*return new Promise((resolve, reject) => { 
        resolve(data3);
    });*/
    
}; 

export const saveFlowsheet = (id, data) => {
    return fetch(process.env.REACT_APP_BACKEND_SERVER+'/flowsheets/'+id+'/update', {
        method: 'POST', 
        mode: 'cors',
        body: JSON.stringify(data)
    });
}; 

export const resetFlowsheet = (id) => {
    return fetch(process.env.REACT_APP_BACKEND_SERVER+'/flowsheets/'+id+'/reset', {
        method: 'GET', 
        mode: 'cors'
    });
}; 

export const unbuildFlowsheet = (id) => {
    return fetch(process.env.REACT_APP_BACKEND_SERVER+'/flowsheets/'+id+'/unbuild', {
        method: 'GET', 
        mode: 'cors'
    });
}; 

export const selectOption = (id, data) => {
    return fetch(process.env.REACT_APP_BACKEND_SERVER+'/flowsheets/'+id+'/select_option', {
        method: 'POST', 
        mode: 'cors',
        body: JSON.stringify(data)
    });
}; 

export const getLogs = () => {
    return fetch(process.env.REACT_APP_BACKEND_SERVER+'/flowsheets/get_logs', {
        method: 'GET', 
        mode: 'cors'
    });
}

export const downloadLogs = () => {
    return fetch(process.env.REACT_APP_BACKEND_SERVER+'/flowsheets/download_logs', {
        method: 'POST', 
        mode: 'cors'
    });
}

export const setProject = (project) => {
    return fetch(process.env.REACT_APP_BACKEND_SERVER+'/flowsheets/set_project/'+project, {
        method: 'GET', 
        mode: 'cors'
    });
}