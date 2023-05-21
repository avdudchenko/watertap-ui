

export const getFlowsheet = (id) => {
    return fetch(process.env.REACT_APP_BACKEND_SERVER+'/flowsheets/'+id+'/config?build=1', {mode: 'cors'});
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